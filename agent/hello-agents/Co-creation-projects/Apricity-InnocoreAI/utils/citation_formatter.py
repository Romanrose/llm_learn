"""
InnoCore AI 引用格式化工具
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class CitationFormatter:
    """引用格式化器"""
    
    def __init__(self):
        self.month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
    
    def format_bibtex(self, paper_info: Dict[str, Any]) -> str:
        """格式化为BibTeX"""
        # 生成引用键
        citation_key = self._generate_citation_key(paper_info)
        
        # 确定条目类型
        entry_type = self._determine_entry_type(paper_info)
        
        # 构建BibTeX条目
        bibtex_lines = [f"@{entry_type}{{{citation_key}"]
        
        # 添加作者
        authors = paper_info.get("authors", [])
        if authors:
            formatted_authors = self._format_bibtex_authors(authors)
            bibtex_lines.append(f"  author = {{{formatted_authors}}}")
        
        # 添加标题
        title = paper_info.get("title", "")
        if title:
            bibtex_lines.append(f"  title = {{{title}}}")
        
        # 添加期刊/会议信息
        if entry_type == "article":
            journal = paper_info.get("journal", "")
            if journal:
                bibtex_lines.append(f"  journal = {{{journal}}}")
            
            volume = paper_info.get("volume", "")
            if volume:
                bibtex_lines.append(f"  volume = {{{volume}}}")
            
            number = paper_info.get("number", "")
            if number:
                bibtex_lines.append(f"  number = {{{number}}}")
            
            pages = paper_info.get("pages", "")
            if pages:
                bibtex_lines.append(f"  pages = {{{pages}}}")
        
        elif entry_type == "inproceedings":
            booktitle = paper_info.get("booktitle", "")
            if booktitle:
                bibtex_lines.append(f"  booktitle = {{{booktitle}}}")
            
            pages = paper_info.get("pages", "")
            if pages:
                bibtex_lines.append(f"  pages = {{{pages}}}")
        
        elif entry_type == "book":
            publisher = paper_info.get("publisher", "")
            if publisher:
                bibtex_lines.append(f"  publisher = {{{publisher}}}")
        
        # 添加年份
        year = paper_info.get("year", "")
        if year:
            bibtex_lines.append(f"  year = {{{year}}}")
        
        # 添加月份
        month = paper_info.get("month", "")
        if month:
            bibtex_lines.append(f"  month = {{{month}}}")
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            bibtex_lines.append(f"  doi = {{{doi}}}")
        
        # 添加URL
        url = paper_info.get("url", "")
        if url:
            bibtex_lines.append(f"  url = {{{url}}}")
        
        # 添加笔记
        note = paper_info.get("note", "")
        if note:
            bibtex_lines.append(f"  note = {{{note}}}")
        
        # 关闭条目
        bibtex_lines.append("}")
        
        return "\n".join(bibtex_lines)
    
    def format_apa(self, paper_info: Dict[str, Any]) -> str:
        """格式化为APA格式"""
        authors = paper_info.get("authors", [])
        year = paper_info.get("year", "")
        title = paper_info.get("title", "")
        
        # 格式化作者
        author_text = self._format_apa_authors(authors)
        
        # 构建基本引用
        if year:
            citation = f"{author_text} ({year}). {title}."
        else:
            citation = f"{author_text}. {title}."
        
        # 添加期刊信息
        journal = paper_info.get("journal", "")
        volume = paper_info.get("volume", "")
        number = paper_info.get("number", "")
        pages = paper_info.get("pages", "")
        
        if journal:
            if volume and number:
                citation += f" *{journal}*, *{volume}({number})*"
            elif volume:
                citation += f" *{journal}*, *{volume}*"
            else:
                citation += f" *{journal}*"
            
            if pages:
                citation += f", {pages}."
            else:
                citation += "."
        
        # 添加书籍信息
        publisher = paper_info.get("publisher", "")
        if publisher:
            citation += f" {publisher}."
        
        # 添加会议信息
        booktitle = paper_info.get("booktitle", "")
        if booktitle:
            citation += f" In *{booktitle}*"
            if pages:
                citation += f" (pp. {pages})."
            else:
                citation += "."
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            citation += f" https://doi.org/{doi}"
        
        return citation
    
    def format_ieee(self, paper_info: Dict[str, Any]) -> str:
        """格式化为IEEE格式"""
        authors = paper_info.get("authors", [])
        year = paper_info.get("year", "")
        title = paper_info.get("title", "")
        
        # 格式化作者（IEEE格式）
        author_text = self._format_ieee_authors(authors)
        
        # 构建基本引用
        citation = f'{author_text}, "{title},"'
        
        # 添加期刊信息
        journal = paper_info.get("journal", "")
        volume = paper_info.get("volume", "")
        number = paper_info.get("number", "")
        pages = paper_info.get("pages", "")
        
        if journal:
            if volume and number:
                citation += f" *{journal}*, vol. {volume}, no. {number}"
            elif volume:
                citation += f" *{journal}*, vol. {volume}"
            else:
                citation += f" *{journal}*"
            
            if pages:
                citation += f", pp. {pages}"
        
        # 添加会议信息
        booktitle = paper_info.get("booktitle", "")
        if booktitle:
            citation += f" in *{booktitle}*"
            if pages:
                citation += f", pp. {pages}"
        
        # 添加书籍信息
        publisher = paper_info.get("publisher", "")
        if publisher:
            citation += f" {publisher}"
        
        # 添加年份和月份
        month = paper_info.get("month", "")
        if year:
            if month:
                citation += f", {month}. {year}."
            else:
                citation += f", {year}."
        
        # 添加DOI
        doi = paper_info.get("doi", "")
        if doi:
            citation += f" doi: {doi}"
        
        return citation
    
    def format_mla(self, paper_info: Dict[str, Any]) -> str:
        """格式化为MLA格式"""
        authors = paper_info.get("authors", [])
        title = paper_info.get("title", "")
        journal = paper_info.get("journal", "")
        year = paper_info.get("year", "")
        pages = paper_info.get("pages", "")
        
        # 格式化作者（MLA格式）
        author_text = self._format_mla_authors(authors)
        
        # 构建基本引用
        if author_text:
            citation = f'{author_text}. "{title}."'
        else:
            citation = f'"{title}."'
        
        # 添加期刊信息
        if journal:
            citation += f" *{journal}*"
            
            if volume and number:
                citation += f", vol. {volume}, no. {number}"
            elif volume:
                citation += f", vol. {volume}"
            
            if year:
                citation += f", {year}"
            
            if pages:
                citation += f", pp. {pages}."
            else:
                citation += "."
        
        # 添加书籍信息
        publisher = paper_info.get("publisher", "")
        if publisher:
            citation += f" {publisher}"
            if year:
                citation += f", {year}."
            else:
                citation += "."
        
        return citation
    
    def format_chicago(self, paper_info: Dict[str, Any]) -> str:
        """格式化为Chicago格式"""
        authors = paper_info.get("authors", [])
        title = paper_info.get("title", "")
        journal = paper_info.get("journal", "")
        volume = paper_info.get("volume", "")
        number = paper_info.get("number", "")
        year = paper_info.get("year", "")
        pages = paper_info.get("pages", "")
        
        # 格式化作者（Chicago格式）
        author_text = self._format_chicago_authors(authors)
        
        # 构建基本引用
        if author_text:
            citation = f'{author_text}. "{title}."'
        else:
            citation = f'"{title}."'
        
        # 添加期刊信息
        if journal:
            citation += f" *{journal}*"
            
            if volume and number:
                citation += f" {volume}, no. {number}"
            elif volume:
                citation += f" {volume}"
            
            if year:
                citation += f" ({year})"
            
            if pages:
                citation += f": {pages}."
            else:
                citation += "."
        
        return citation
    
    def _generate_citation_key(self, paper_info: Dict[str, Any]) -> str:
        """生成引用键"""
        # 获取第一作者的姓氏
        authors = paper_info.get("authors", [])
        if authors:
            first_author = authors[0]
            if isinstance(first_author, str):
                last_name = first_author.split()[-1].lower()
            else:
                last_name = "unknown"
        else:
            last_name = "unknown"
        
        # 获取年份
        year = str(paper_info.get("year", datetime.now().year))
        
        # 获取标题关键词
        title = paper_info.get("title", "")
        title_words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())[:3]
        title_key = "".join(title_words)
        
        return f"{last_name}{year}{title_key}"
    
    def _determine_entry_type(self, paper_info: Dict[str, Any]) -> str:
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
                    last_name = parts[-1]
                    first_names = " ".join(parts[:-1])
                    formatted_authors.append(f"{last_name}, {first_names}")
                else:
                    formatted_authors.append(author)
            else:
                formatted_authors.append(str(author))
        
        return " and ".join(formatted_authors)
    
    def _format_apa_authors(self, authors: List[str]) -> str:
        """格式化APA作者"""
        if not authors:
            return ""
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 20:
            return ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            return ", ".join(authors[:19]) + f", ... {authors[-1]}"
    
    def _format_ieee_authors(self, authors: List[str]) -> str:
        """格式化IEEE作者"""
        formatted_authors = []
        
        for i, author in enumerate(authors[:3]):  # IEEE通常只列出前3个作者
            if isinstance(author, str):
                parts = author.split()
                if len(parts) >= 2:
                    # 转换为 "F. Last" 格式
                    initials = " ".join([f"{p[0]}." for p in parts[:-1]])
                    last_name = parts[-1]
                    formatted_authors.append(f"{initials} {last_name}")
                else:
                    formatted_authors.append(author)
            else:
                formatted_authors.append(str(author))
        
        if len(authors) > 3:
            formatted_authors.append("et al.")
        
        return ", ".join(formatted_authors)
    
    def _format_mla_authors(self, authors: List[str]) -> str:
        """格式化MLA作者"""
        if not authors:
            return ""
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]}, et al."
    
    def _format_chicago_authors(self, authors: List[str]) -> str:
        """格式化Chicago作者"""
        if not authors:
            return ""
        
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]}, et al."
    
    def parse_bibtex(self, bibtex_text: str) -> Dict[str, Any]:
        """解析BibTeX文本"""
        paper_info = {}
        
        # 提取条目类型和键
        entry_match = re.match(r'@(\w+)\{([^,]+),', bibtex_text)
        if entry_match:
            paper_info["entry_type"] = entry_match.group(1)
            paper_info["citation_key"] = entry_match.group(2)
        
        # 提取字段
        field_pattern = r'\s*(\w+)\s*=\s*\{([^}]*)\}'
        matches = re.findall(field_pattern, bibtex_text)
        
        for field_name, field_value in matches:
            paper_info[field_name] = field_value
        
        return paper_info
    
    def validate_citation(self, citation: str, style: str) -> Dict[str, Any]:
        """验证引用格式"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        if style.lower() == "bibtex":
            validation_result = self._validate_bibtex(citation, validation_result)
        elif style.lower() == "apa":
            validation_result = self._validate_apa(citation, validation_result)
        elif style.lower() == "ieee":
            validation_result = self._validate_ieee(citation, validation_result)
        
        return validation_result
    
    def _validate_bibtex(self, citation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证BibTeX格式"""
        # 检查基本结构
        if not citation.startswith('@'):
            result["is_valid"] = False
            result["errors"].append("BibTeX必须以@开头")
        
        if not citation.endswith('}'):
            result["is_valid"] = False
            result["errors"].append("BibTeX必须以}结尾")
        
        # 检查必需字段
        if 'title' not in citation:
            result["warnings"].append("缺少title字段")
        
        if 'author' not in citation:
            result["warnings"].append("缺少author字段")
        
        if 'year' not in citation:
            result["warnings"].append("缺少year字段")
        
        return result
    
    def _validate_apa(self, citation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证APA格式"""
        # 检查作者格式
        if '(' in citation and ')' in citation:
            year_pattern = r'\((\d{4})\)'
            if not re.search(year_pattern, citation):
                result["warnings"].append("APA格式应包含出版年份")
        
        # 检查标题格式
        if not citation.strip().endswith('.'):
            result["warnings"].append("APA引用应以句号结尾")
        
        return result
    
    def _validate_ieee(self, citation: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证IEEE格式"""
        # 检查引用格式
        if '"' not in citation:
            result["warnings"].append("IEEE格式中标题应使用双引号")
        
        # 检查期刊格式
        if '*' not in citation:
            result["warnings"].append("IEEE格式中期刊名应使用斜体（*）")
        
        return result
    
    def convert_between_formats(self, citation: str, from_style: str, to_style: str) -> str:
        """在不同格式间转换引用"""
        try:
            # 解析原始格式
            if from_style.lower() == "bibtex":
                paper_info = self.parse_bibtex(citation)
            else:
                # 对于其他格式，需要更复杂的解析逻辑
                # 这里提供简化实现
                paper_info = {
                    "title": "",
                    "authors": [],
                    "year": "",
                    "journal": ""
                }
            
            # 转换为目标格式
            if to_style.lower() == "bibtex":
                return self.format_bibtex(paper_info)
            elif to_style.lower() == "apa":
                return self.format_apa(paper_info)
            elif to_style.lower() == "ieee":
                return self.format_ieee(paper_info)
            elif to_style.lower() == "mla":
                return self.format_mla(paper_info)
            elif to_style.lower() == "chicago":
                return self.format_chicago(paper_info)
            else:
                return citation
                
        except Exception as e:
            return f"转换失败: {str(e)}"