"""
InnoCore AI 前哨探员 (Hunter Agent)
负责每日根据关键词监控ArXiv/IEEE，初筛并下载PDF
"""

import asyncio
import aiohttp
import feedparser
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import os
from urllib.parse import urljoin, quote

from agents.base import BaseAgent
from core.database import db_manager
from core.exceptions import AgentException, ExternalAPIException

class HunterAgent(BaseAgent):
    """前哨探员智能体"""
    
    def __init__(self, llm=None):
        super().__init__("Hunter", llm)
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.ieee_base_url = "https://ieeexploreapi.ieee.org/api/v1"
        self.download_dir = "downloads/papers"
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 添加工具
        self.add_tool("search_arxiv", self._search_arxiv, "搜索ArXiv论文")
        self.add_tool("search_ieee", self._search_ieee, "搜索IEEE论文")
        self.add_tool("download_pdf", self._download_pdf, "下载PDF文件")
        self.add_tool("extract_metadata", self._extract_metadata, "提取论文元数据")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行论文抓取任务"""
        await self.validate_input(input_data)
        
        self.set_state("running")
        
        try:
            keywords = input_data["keywords"]
            max_papers = input_data.get("max_papers", 20)
            sources = input_data.get("sources", ["arxiv", "ieee"])
            days_back = input_data.get("days_back", 1)
            
            all_papers = []
            
            # 搜索不同来源
            if "arxiv" in sources:
                arxiv_papers = await self._search_papers_from_arxiv(keywords, max_papers, days_back)
                all_papers.extend(arxiv_papers)
            
            if "ieee" in sources:
                ieee_papers = await self._search_papers_from_ieee(keywords, max_papers, days_back)
                all_papers.extend(ieee_papers)
            
            # 去重和筛选
            unique_papers = self._deduplicate_papers(all_papers)
            filtered_papers = await self._filter_papers(unique_papers, keywords)
            
            # 下载PDF
            downloaded_papers = []
            for paper in filtered_papers[:max_papers]:
                try:
                    downloaded_paper = await self._download_and_save_paper(paper)
                    if downloaded_paper:
                        downloaded_papers.append(downloaded_paper)
                except Exception as e:
                    self._add_to_history(f"下载论文失败 {paper.get('title', 'Unknown')}: {str(e)}")
            
            self.set_state("completed")
            
            return {
                "status": "success",
                "total_found": len(all_papers),
                "unique_papers": len(unique_papers),
                "filtered_papers": len(filtered_papers),
                "downloaded_papers": len(downloaded_papers),
                "papers": downloaded_papers
            }
            
        except Exception as e:
            self.set_state("error")
            raise AgentException(f"Hunter Agent执行失败: {str(e)}")
    
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        return ["keywords"]
    
    async def _search_papers_from_arxiv(self, keywords: List[str], max_papers: int, days_back: int) -> List[Dict]:
        """从ArXiv搜索论文"""
        papers = []
        
        # 构建查询字符串
        query_parts = []
        for keyword in keywords:
            query_parts.append(f'all:"{keyword}"')
        query = " OR ".join(query_parts)
        
        # 添加时间过滤
        date_filter = ""
        if days_back > 0:
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
            date_filter = f"submittedDate:[{start_filter}0000 TO {datetime.now().strftime('%Y%m%d')}2359]"
        
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_papers * 2,  # 获取更多结果以便筛选
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.arxiv_base_url, params=params) as response:
                    if response.status != 200:
                        raise ExternalAPIException(f"ArXiv API请求失败: {response.status}")
                    
                    xml_content = await response.text()
                    feed = feedparser.parse(xml_content)
                    
                    for entry in feed.entries:
                        paper = {
                            "id": entry.id.split("/")[-1],
                            "title": entry.title,
                            "authors": [author.name for author in entry.authors],
                            "abstract": entry.summary,
                            "published": entry.published,
                            "pdf_url": entry.link.replace('/abs/', '/pdf/') + '.pdf',
                            "source": "arxiv",
                            "doi": entry.get('arxiv_doi', ''),
                            "categories": [tag.term for tag in entry.tags]
                        }
                        
                        papers.append(paper)
                        
        except Exception as e:
            self._add_to_history(f"ArXiv搜索失败: {str(e)}")
        
        return papers
    
    async def _search_papers_from_ieee(self, keywords: List[str], max_papers: int, days_back: int) -> List[Dict]:
        """从IEEE搜索论文"""
        papers = []
        
        # IEEE API需要API key，这里提供基础实现框架
        config = self.config.external_apis
        
        if not config.ieee_base_url:
            self._add_to_history("IEEE API配置缺失，跳过IEEE搜索")
            return papers
        
        # 构建查询参数
        query = " OR ".join([f'"All Meta Data:{keyword}"' for keyword in keywords])
        
        params = {
            "apikey": config.ieee_api_key or "",
            "querytext": query,
            "max_records": max_papers * 2,
            "start_record": 1,
            "sort_order": "desc",
            "sort_field": "publication_date"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.ieee_base_url, params=params) as response:
                    if response.status != 200:
                        raise ExternalAPIException(f"IEEE API请求失败: {response.status}")
                    
                    data = await response.json()
                    
                    for article in data.get("articles", []):
                        paper = {
                            "id": article.get("article_number", ""),
                            "title": article.get("title", ""),
                            "authors": [author.get("full_name", "") for author in article.get("authors", {}).get("authors", [])],
                            "abstract": article.get("abstract", ""),
                            "published": article.get("publication_date", ""),
                            "pdf_url": article.get("pdf_url", ""),
                            "source": "ieee",
                            "doi": article.get("doi", ""),
                            "categories": article.get("index_terms", {}).get("ieee_terms", {}).get("terms", [])
                        }
                        
                        papers.append(paper)
                        
        except Exception as e:
            self._add_to_history(f"IEEE搜索失败: {str(e)}")
        
        return papers
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """去重论文"""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get("title", "").lower().strip()
            title_hash = hashlib.md5(title.encode()).hexdigest()
            
            if title_hash not in seen_titles:
                seen_titles.add(title_hash)
                unique_papers.append(paper)
        
        return unique_papers
    
    async def _filter_papers(self, papers: List[Dict], keywords: List[str]) -> List[Dict]:
        """根据关键词筛选论文"""
        filtered_papers = []
        
        for paper in papers:
            title = paper.get("title", "").lower()
            abstract = paper.get("abstract", "").lower()
            combined_text = f"{title} {abstract}"
            
            # 计算关键词匹配分数
            score = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title:
                    score += 2  # 标题匹配权重更高
                if keyword_lower in abstract:
                    score += 1
            
            # 设定阈值
            if score >= 1:
                paper["relevance_score"] = score
                filtered_papers.append(paper)
        
        # 按相关性分数排序
        filtered_papers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return filtered_papers
    
    async def _download_and_save_paper(self, paper: Dict) -> Optional[Dict]:
        """下载并保存论文"""
        pdf_url = paper.get("pdf_url")
        if not pdf_url:
            return None
        
        try:
            # 生成文件名
            safe_title = re.sub(r'[^\w\s-]', '', paper.get("title", "unknown"))[:50]
            filename = f"{paper['id']}_{safe_title}.pdf"
            file_path = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                self._add_to_history(f"论文已存在: {filename}")
                paper["file_path"] = file_path
                return paper
            
            # 下载PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        # 计算文件哈希
                        content_hash = hashlib.sha256(content).hexdigest()
                        
                        # 更新论文信息
                        paper["file_path"] = file_path
                        paper["content_hash"] = content_hash
                        paper["file_size"] = len(content)
                        
                        # 保存到数据库
                        await self._save_paper_to_db(paper)
                        
                        self._add_to_history(f"成功下载论文: {filename}")
                        return paper
                    else:
                        self._add_to_history(f"下载失败，HTTP状态码: {response.status}")
                        return None
                        
        except Exception as e:
            self._add_to_history(f"下载论文异常: {str(e)}")
            return None
    
    async def _save_paper_to_db(self, paper: Dict):
        """保存论文到数据库"""
        try:
            # 检查是否已存在
            existing_paper = await db_manager.get_paper_by_hash(paper.get("content_hash"))
            if existing_paper:
                self._add_to_history(f"论文已存在于数据库: {paper.get('title')}")
                return
            
            # 创建论文记录
            paper_id = await db_manager.create_paper(
                title=paper.get("title", ""),
                authors=paper.get("authors", []),
                abstract=paper.get("abstract", ""),
                doi=paper.get("doi", ""),
                file_path=paper.get("file_path", ""),
                content_hash=paper.get("content_hash", ""),
                is_preset=False
            )
            
            paper["db_id"] = paper_id
            self._add_to_history(f"论文已保存到数据库: {paper_id}")
            
        except Exception as e:
            self._add_to_history(f"保存论文到数据库失败: {str(e)}")
    
    # 工具方法
    async def _search_arxiv(self, query: str) -> List[Dict]:
        """搜索ArXiv工具"""
        keywords = [kw.strip() for kw in query.split(",")]
        return await self._search_papers_from_arxiv(keywords, 10, 7)
    
    async def _search_ieee(self, query: str) -> List[Dict]:
        """搜索IEEE工具"""
        keywords = [kw.strip() for kw in query.split(",")]
        return await self._search_papers_from_ieee(keywords, 10, 7)
    
    async def _download_pdf(self, pdf_url: str) -> str:
        """下载PDF工具"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        file_path = os.path.join(self.download_dir, filename)
                        
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        return file_path
                    else:
                        return f"下载失败，状态码: {response.status}"
        except Exception as e:
            return f"下载异常: {str(e)}"
    
    async def _extract_metadata(self, file_path: str) -> Dict:
        """提取论文元数据工具"""
        # 这里应该使用PDF解析库提取元数据
        # 暂时返回基础信息
        return {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "extracted_at": datetime.now().isoformat()
        }