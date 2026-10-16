"""
InnoCore AI 校验官 (Validator Agent)
负责生成引用格式并联网校验元数据
"""

import asyncio
import aiohttp
import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from agents.base import BaseAgent
from core.database import db_manager
from core.exceptions import AgentException, ExternalAPIException

class ValidatorAgent(BaseAgent):
    """校验官智能体"""
    
    def __init__(self, llm=None):
        super().__init__("Validator", llm)
        
        # API配置
        self.crossref_base_url = "https://api.crossref.org/works"
        self.google_scholar_url = "https://serpapi.com/search"
        
        # 添加工具
        self.add_tool("generate_bibtex", self._generate_bibtex, "生成BibTeX引用")
        self.add_tool("generate_apa", self._generate_apa, "生成APA格式引用")
        self.add_tool("generate_ieee", self._generate_ieee, "生成IEEE格式引用")
        self.add_tool("verify_metadata", self._verify_metadata, "校验元数据")
        self.add_tool("crossref_lookup", self._crossref_lookup, "CrossRef查询")
        self.add_tool("scholar_lookup", self._scholar_lookup, "Google Scholar查询")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行引用校验任务"""
        await self.validate_input(input_data)
        
        self.set_state("running")
        
        try:
            paper_info = input_data["paper_info"]
            formats = input_data.get("formats", ["bibtex", "apa", "ieee"])
            verify_external = input_data.get("verify_external", True)
            
            # 1. 生成多种格式的引用
            citations = await self._generate_citations(paper_info, formats)
            
            # 2. 外部校验元数据
            verification_result = {}
            if verify_external:
                verification_result = await self._verify_paper_metadata(paper_info)
            
            # 3. 合并和更新引用信息
            final_citations = await self._merge_citation_data(
                citations, 
                verification_result, 
                paper_info
            )
            
            # 4. 缓存结果
            await self._cache_citation_results(final_citations)
            
            self.set_state("completed")
            
            return {
                "status": "success",
                "paper_info": paper_info,
                "citations": final_citations,
                "verification": verification_result,
                "formats_generated": list(citations.keys()),
                "verification_status": verification_result.get("status", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.set_state("error")
            raise AgentException(f"Validator Agent执行失败: {str(e)}")
    
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        return ["paper_info"]
    
    async def _generate_citations(self, paper_info: Dict, formats: List[str]) -> Dict[str, Any]:
        """生成多种格式的引用"""
        citations = {}
        
        for format_type in formats:
            try:
                if format_type.lower() == "bibtex":
                    citations["bibtex"] = await self._generate_bibtex_citation(paper_info)
                elif format_type.lower() == "apa":
                    citations["apa"] = await self._generate_apa_citation(paper_info)
                elif format_type.lower() == "ieee":
                    citations["ieee"] = await self._generate_ieee_citation(paper_info)
                else:
                    self._add_to_history(f"不支持的引用格式: {format_type}")
                    
            except Exception as e:
                self._add_to_history(f"生成{format_type}格式失败: {str(e)}")
                citations[format_type] = f"生成失败: {str(e)}"
        
        return citations
    
    async def _generate_bibtex_citation(self, paper_info: Dict) -> str:
        """生成BibTeX格式引用"""
        # 生成引用键
        first_author = paper_info.get("authors", [""])[0]
        if isinstance(first_author, str):
            last_name = first_author.split()[-1].lower()
        else:
            last_name = "unknown"
        
        year = paper_info.get("year", datetime.now().year)
        title_words = paper_info.get("title", "").split()[:3]
        title_key = "".join([w.lower() for w in title_words if w.isalpha()])
        
        citation_key = f"{last_name}{year}{title_key}"
        
        # 构建BibTeX条目
        entry_type = self._determine_entry_type(paper_info)
        
        bibtex = f"@{entry_type}{{{citation_key},\n"
        
        # 添加作者
        authors = paper_info.get("authors", [])
        if authors:
            bibtex += f"  author = {{{self._format_bibtex_authors(authors)}}},\n"
        
        # 添加标题
        title = paper_info.get("title", "")
        if title:
            bibtex += f"  title = {{{title}}},\n"
        
        # 添加期刊/会议信息
        if entry_type == "article":
            journal = paper_info.get("journal", "")
            if journal:
                bibtex += f"  journal = {{{journal}}},\n"
            
            volume = paper_info.get("volume", "")
            if volume:
                bibtex += f"  volume = {{{volume}}},\n"
            
            number = paper_info.get("number", "")
            if number:
                bibtex += f"  number = {{{number}}},\n"
            
            pages = paper_info.get("pages", "")
            if pages:
                bibtex += f"  pages = {{{pages}}},\n"
        
        elif entry_type == "inproceedings":
            booktitle = paper_info.get("booktitle", "")
            if booktitle:
                bibtex += f"  booktitle = {{{booktitle}}},\n"
            
            pages = paper_info.get("pages", "")
            if pages:
                bibtex += f"  pages = {{{pages}}},\n"
        
        # 添加年份
        if year:
            bibtex += f"  year = {{{year}}},\n"
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            bibtex += f"  doi = {{{doi}}},\n"
        
        # 添加URL
        url = paper_info.get("url", "")
        if url:
            bibtex += f"  url = {{{url}}},\n"
        
        # 移除最后的逗号并关闭
        bibtex = bibtex.rstrip(",\n") + "\n}"
        
        return bibtex
    
    async def _generate_apa_citation(self, paper_info: Dict) -> str:
        """生成APA格式引用"""
        authors = paper_info.get("authors", [])
        year = paper_info.get("year", "")
        title = paper_info.get("title", "")
        
        # 格式化作者
        if len(authors) == 0:
            author_text = ""
        elif len(authors) == 1:
            author_text = authors[0]
        elif len(authors) == 2:
            author_text = f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 7:
            author_text = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_text = ", ".join(authors[:6]) + f", ... {authors[-1]}"
        
        # 构建APA引用
        if year:
            apa_citation = f"{author_text} ({year}). {title}."
        else:
            apa_citation = f"{author_text}. {title}."
        
        # 添加期刊信息
        journal = paper_info.get("journal", "")
        volume = paper_info.get("volume", "")
        number = paper_info.get("number", "")
        pages = paper_info.get("pages", "")
        
        if journal:
            if volume and number:
                apa_citation += f" *{journal}*, *{volume}({number})*"
            elif volume:
                apa_citation += f" *{journal}*, *{volume}*"
            else:
                apa_citation += f" *{journal}*"
            
            if pages:
                apa_citation += f", {pages}."
            else:
                apa_citation += "."
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            apa_citation += f" https://doi.org/{doi}"
        
        return apa_citation
    
    async def _generate_ieee_citation(self, paper_info: Dict) -> str:
        """生成IEEE格式引用"""
        authors = paper_info.get("authors", [])
        year = paper_info.get("year", "")
        title = paper_info.get("title", "")
        
        # 格式化作者（IEEE使用首字母缩写）
        ieee_authors = []
        for author in authors[:3]:  # IEEE通常只列出前3个作者
            if isinstance(author, str):
                parts = author.split()
                if len(parts) >= 2:
                    last_name = parts[-1]
                    initials = " ".join([p[0] + "." for p in parts[:-1]])
                    ieee_authors.append(f"{initials} {last_name}")
                else:
                    ieee_authors.append(author)
        
        if len(authors) > 3:
            ieee_authors.append("et al.")
        
        author_text = ", ".join(ieee_authors)
        
        # 构建IEEE引用
        if title:
            ieee_citation = f'"{title},"'
        else:
            ieee_citation = ""
        
        # 添加期刊信息
        journal = paper_info.get("journal", "")
        volume = paper_info.get("volume", "")
        number = paper_info.get("number", "")
        pages = paper_info.get("pages", "")
        
        if journal:
            if volume and number:
                ieee_citation += f" *{journal}*, vol. {volume}, no. {number}"
            elif volume:
                ieee_citation += f" *{journal}*, vol. {volume}"
            else:
                ieee_citation += f" *{journal}*"
            
            if pages:
                ieee_citation += f", pp. {pages}"
        
        # 添加年份和月份
        if year:
            month = paper_info.get("month", "")
            if month:
                ieee_citation += f", {month}. {year}."
            else:
                ieee_citation += f", {year}."
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            ieee_citation += f" doi: {doi}"
        
        return ieee_citation
    
    def _determine_entry_type(self, paper_info: Dict) -> str:
        """确定BibTeX条目类型"""
        if paper_info.get("journal"):
            return "article"
        elif paper_info.get("booktitle"):
            return "inproceedings"
        elif paper_info.get("publisher"):
            return "book"
        else:
            return "misc"
    
    def _format_bibtex_authors(self, authors: List[str]) -> str:
        """格式化BibTeX作者"""
        formatted_authors = []
        for author in authors:
            if isinstance(author, str):
                # 将 "First Last" 转换为 "Last, First"
                parts = author.split()
                if len(parts) >= 2:
                    formatted_authors.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
                else:
                    formatted_authors.append(author)
            else:
                formatted_authors.append(str(author))
        
        return " and ".join(formatted_authors)
    
    async def _verify_paper_metadata(self, paper_info: Dict) -> Dict[str, Any]:
        """校验论文元数据"""
        verification_result = {
            "status": "pending",
            "crossref_verified": False,
            "scholar_verified": False,
            "discrepancies": [],
            "suggested_corrections": {},
            "verification_timestamp": datetime.now().isoformat()
        }
        
        doi = paper_info.get("doi", "")
        title = paper_info.get("title", "")
        
        try:
            # 1. CrossRef校验
            if doi:
                crossref_data = await self._crossref_lookup_by_doi(doi)
                if crossref_data:
                    verification_result["crossref_verified"] = True
                    discrepancies = self._compare_metadata(paper_info, crossref_data)
                    if discrepancies:
                        verification_result["discrepancies"].extend(discrepancies)
                        verification_result["suggested_corrections"].update(
                            self._generate_corrections(discrepancies)
                        )
            
            # 2. Google Scholar校验
            if title:
                scholar_data = await self._scholar_lookup_by_title(title)
                if scholar_data:
                    verification_result["scholar_verified"] = True
                    discrepancies = self._compare_metadata(paper_info, scholar_data)
                    if discrepancies:
                        verification_result["discrepancies"].extend(discrepancies)
                        verification_result["suggested_corrections"].update(
                            self._generate_corrections(discrepancies)
                        )
            
            # 确定最终状态
            if verification_result["crossref_verified"] or verification_result["scholar_verified"]:
                if not verification_result["discrepancies"]:
                    verification_result["status"] = "verified"
                else:
                    verification_result["status"] = "discrepancies_found"
            else:
                verification_result["status"] = "unverified"
            
        except Exception as e:
            verification_result["status"] = "error"
            verification_result["error"] = str(e)
            self._add_to_history(f"元数据校验失败: {str(e)}")
        
        return verification_result
    
    async def _crossref_lookup_by_doi(self, doi: str) -> Optional[Dict]:
        """通过DOI查询CrossRef"""
        try:
            url = f"{self.crossref_base_url}/{doi}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_crossref_data(data)
                    else:
                        self._add_to_history(f"CrossRef查询失败，状态码: {response.status}")
                        return None
                        
        except Exception as e:
            self._add_to_history(f"CrossRef查询异常: {str(e)}")
            return None
    
    async def _scholar_lookup_by_title(self, title: str) -> Optional[Dict]:
        """通过标题查询Google Scholar"""
        try:
            config = self.config.external_apis
            if not config.serpapi_key:
                self._add_to_history("SerpApi key缺失，跳过Google Scholar查询")
                return None
            
            params = {
                "engine": "google_scholar",
                "q": title,
                "api_key": config.serpapi_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.google_scholar_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_scholar_data(data)
                    else:
                        self._add_to_history(f"Google Scholar查询失败，状态码: {response.status}")
                        return None
                        
        except Exception as e:
            self._add_to_history(f"Google Scholar查询异常: {str(e)}")
            return None
    
    def _parse_crossref_data(self, data: Dict) -> Dict:
        """解析CrossRef数据"""
        message = data.get("message", {})
        
        return {
            "title": " ".join(message.get("title", [])),
            "authors": [f"{author.get('given', '')} {author.get('family', '')}" 
                       for author in message.get("author", [])],
            "year": message.get("published-print", {}).get("date-parts", [[""]])[0][0][:4],
            "journal": message.get("short-container-title", [""])[0],
            "volume": message.get("volume", ""),
            "issue": message.get("issue", ""),
            "page": message.get("page", ""),
            "doi": message.get("DOI", ""),
            "source": "crossref"
        }
    
    def _parse_scholar_data(self, data: Dict) -> Dict:
        """解析Google Scholar数据"""
        organic_results = data.get("organic_results", [])
        if not organic_results:
            return {}
        
        first_result = organic_results[0]
        
        # 提取年份
        publication_info = first_result.get("publication_info", {})
        year = ""
        if "summary" in publication_info:
            year_match = re.search(r'\b(19|20)\d{2}\b', publication_info["summary"])
            if year_match:
                year = year_match.group()
        
        return {
            "title": first_result.get("title", ""),
            "authors": first_result.get("publication_info", {}).get("authors", []),
            "year": year,
            "journal": publication_info.get("summary", "").split(",")[0] if publication_info.get("summary") else "",
            "source": "google_scholar"
        }
    
    def _compare_metadata(self, original: Dict, reference: Dict) -> List[Dict]:
        """比较元数据差异"""
        discrepancies = []
        
        # 比较标题
        orig_title = original.get("title", "").lower().strip()
        ref_title = reference.get("title", "").lower().strip()
        if orig_title and ref_title and orig_title != ref_title:
            discrepancies.append({
                "field": "title",
                "original": original.get("title", ""),
                "reference": reference.get("title", ""),
                "similarity": self._calculate_similarity(orig_title, ref_title)
            })
        
        # 比较作者
        orig_authors = set([author.lower() for author in original.get("authors", [])])
        ref_authors = set([author.lower() for author in reference.get("authors", [])])
        if orig_authors and ref_authors and orig_authors != ref_authors:
            discrepancies.append({
                "field": "authors",
                "original": original.get("authors", []),
                "reference": reference.get("authors", []),
                "missing_in_original": list(ref_authors - orig_authors),
                "extra_in_original": list(orig_authors - ref_authors)
            })
        
        # 比较年份
        orig_year = str(original.get("year", ""))
        ref_year = str(reference.get("year", ""))
        if orig_year and ref_year and orig_year != ref_year:
            discrepancies.append({
                "field": "year",
                "original": orig_year,
                "reference": ref_year
            })
        
        return discrepancies
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_corrections(self, discrepancies: List[Dict]) -> Dict:
        """生成修正建议"""
        corrections = {}
        
        for discrepancy in discrepancies:
            field = discrepancy["field"]
            if field == "title" and discrepancy.get("similarity", 0) > 0.8:
                corrections[field] = discrepancy["reference"]
            elif field == "year":
                corrections[field] = discrepancy["reference"]
            elif field == "authors":
                # 对于作者，建议使用参考数据的完整列表
                corrections[field] = discrepancy["reference"]
        
        return corrections
    
    async def _merge_citation_data(self, citations: Dict, verification: Dict, paper_info: Dict) -> Dict[str, Any]:
        """合并引用数据"""
        final_citations = {}
        
        for format_type, citation_text in citations.items():
            if isinstance(citation_text, str) and not citation_text.startswith("生成失败"):
                # 添加校验状态标记
                verification_status = verification.get("status", "unknown")
                
                if verification_status == "verified":
                    citation_text += "  % [Verified]"
                elif verification_status == "discrepancies_found":
                    citation_text += "  % [Discrepancies Found]"
                else:
                    citation_text += "  % [Unverified]"
                
                final_citations[format_type] = citation_text
            else:
                final_citations[format_type] = citation_text
        
        # 添加元数据
        final_citations["metadata"] = {
            "original_info": paper_info,
            "verification": verification,
            "generated_formats": list(citations.keys()),
            "generation_timestamp": datetime.now().isoformat()
        }
        
        return final_citations
    
    async def _cache_citation_results(self, citations: Dict):
        """缓存引用结果"""
        try:
            metadata = citations.get("metadata", {})
            original_info = metadata.get("original_info", {})
            doi = original_info.get("doi", "")
            
            if doi:
                # 缓存BibTeX格式
                bibtex = citations.get("bibtex", "")
                if bibtex and not bibtex.startswith("生成失败"):
                    verification = metadata.get("verification", {})
                    is_verified = verification.get("status") == "verified"
                    
                    await db_manager.cache_reference(
                        doi=doi,
                        bibtex=bibtex,
                        is_verified=is_verified
                    )
                    
                    self._add_to_history(f"引用已缓存: {doi}")
                    
        except Exception as e:
            self._add_to_history(f"缓存引用失败: {str(e)}")
    
    # 工具方法
    async def _generate_bibtex(self, paper_info: Dict) -> str:
        """生成BibTeX工具"""
        return await self._generate_bibtex_citation(paper_info)
    
    async def _generate_apa(self, paper_info: Dict) -> str:
        """生成APA工具"""
        return await self._generate_apa_citation(paper_info)
    
    async def _generate_ieee(self, paper_info: Dict) -> str:
        """生成IEEE工具"""
        return await self._generate_ieee_citation(paper_info)
    
    async def _verify_metadata(self, paper_info: Dict) -> Dict:
        """校验元数据工具"""
        return await self._verify_paper_metadata(paper_info)
    
    async def _crossref_lookup(self, identifier: str) -> Dict:
        """CrossRef查询工具"""
        if identifier.startswith("10."):  # DOI
            return await self._crossref_lookup_by_doi(identifier)
        else:
            return {"error": "请提供有效的DOI"}
    
    async def _scholar_lookup(self, title: str) -> Dict:
        """Google Scholar查询工具"""
        return await self._scholar_lookup_by_title(title)