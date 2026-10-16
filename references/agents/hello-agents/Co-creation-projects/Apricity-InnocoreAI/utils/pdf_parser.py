"""
PDF 解析工具
支持从 PDF 文件中提取文本、标题、作者等信息
"""

import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class PDFParser:
    """PDF 解析器"""
    
    def __init__(self):
        """初始化 PDF 解析器"""
        self.supported_formats = ['.pdf']
    
    async def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            包含解析结果的字典
        """
        try:
            import pdfplumber
            
            logger.info(f"开始解析 PDF: {file_path}")
            
            with pdfplumber.open(file_path) as pdf:
                # 提取所有文本
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                if not full_text.strip():
                    logger.warning("PDF 文件为空或无法提取文本")
                    return {
                        "success": False,
                        "error": "无法从 PDF 中提取文本"
                    }
                
                # 提取元数据
                metadata = pdf.metadata or {}
                
                # 尝试从文本中提取标题（通常在第一页的前几行）
                title = self._extract_title(full_text, metadata)
                
                # 尝试提取作者
                authors = self._extract_authors(full_text, metadata)
                
                # 尝试提取摘要
                abstract = self._extract_abstract(full_text)
                
                # 统计信息
                page_count = len(pdf.pages)
                word_count = len(full_text.split())
                
                result = {
                    "success": True,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "full_text": full_text,
                    "page_count": page_count,
                    "word_count": word_count,
                    "metadata": {
                        "creator": metadata.get("/Creator", ""),
                        "producer": metadata.get("/Producer", ""),
                        "subject": metadata.get("/Subject", ""),
                        "keywords": metadata.get("/Keywords", "")
                    }
                }
                
                logger.info(f"PDF 解析成功: {page_count} 页, {word_count} 词")
                return result
                
        except ImportError:
            logger.error("pdfplumber 未安装")
            return {
                "success": False,
                "error": "PDF 解析库未安装，请运行: pip install pdfplumber"
            }
        except Exception as e:
            logger.error(f"PDF 解析失败: {str(e)}")
            return {
                "success": False,
                "error": f"PDF 解析失败: {str(e)}"
            }
    
    def _extract_title(self, text: str, metadata: Dict) -> str:
        """从文本或元数据中提取标题"""
        # 首先尝试从元数据获取
        if metadata.get("/Title"):
            return metadata["/Title"]
        
        # 从文本前几行提取（通常标题在最前面且字体较大）
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):  # 只检查前10行
            line = line.strip()
            # 标题通常较长且不包含特殊字符
            if len(line) > 10 and len(line) < 200 and not line.startswith(('http', 'www', '@')):
                # 排除一些常见的非标题行
                if not any(keyword in line.lower() for keyword in ['abstract', 'introduction', 'page', 'arxiv']):
                    return line
        
        return "未知标题"
    
    def _extract_authors(self, text: str, metadata: Dict) -> list:
        """从文本或元数据中提取作者"""
        authors = []
        
        # 首先尝试从元数据获取
        if metadata.get("/Author"):
            author_str = metadata["/Author"]
            authors = [a.strip() for a in re.split(r'[,;]', author_str) if a.strip()]
            if authors:
                return authors
        
        # 从文本中提取（通常在标题后面）
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):  # 检查前20行
            line = line.strip()
            # 查找包含作者信息的行（通常包含邮箱或机构）
            if '@' in line or 'university' in line.lower() or 'institute' in line.lower():
                # 尝试提取前面几行作为作者名
                for j in range(max(0, i-3), i):
                    potential_author = lines[j].strip()
                    if potential_author and len(potential_author) < 100:
                        # 简单的名字模式匹配
                        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', potential_author):
                            authors.append(potential_author)
        
        return authors if authors else ["未知作者"]
    
    def _extract_abstract(self, text: str) -> str:
        """从文本中提取摘要"""
        # 查找 Abstract 关键词
        abstract_patterns = [
            r'Abstract\s*[:\-]?\s*(.*?)(?=\n\n|\nIntroduction|\n1\.|\nKeywords)',
            r'ABSTRACT\s*[:\-]?\s*(.*?)(?=\n\n|\nINTRODUCTION|\n1\.|\nKEYWORDS)',
            r'摘要\s*[:\-]?\s*(.*?)(?=\n\n|关键词|引言|1\.)',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # 限制摘要长度
                if len(abstract) > 50 and len(abstract) < 2000:
                    return abstract[:1000]  # 最多返回1000字符
        
        # 如果没找到，返回前500个字符作为摘要
        return text[:500].strip() + "..."
    
    async def parse_pdf_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """
        从字节流解析 PDF
        
        Args:
            pdf_bytes: PDF 文件的字节内容
            filename: 文件名（用于日志）
            
        Returns:
            包含解析结果的字典
        """
        try:
            import pdfplumber
            import io
            
            logger.info(f"开始解析 PDF 字节流: {filename}")
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # 提取所有文本
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                if not full_text.strip():
                    return {
                        "success": False,
                        "error": "无法从 PDF 中提取文本"
                    }
                
                # 提取元数据
                metadata = pdf.metadata or {}
                
                # 提取信息
                title = self._extract_title(full_text, metadata)
                authors = self._extract_authors(full_text, metadata)
                abstract = self._extract_abstract(full_text)
                
                result = {
                    "success": True,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "full_text": full_text,
                    "page_count": len(pdf.pages),
                    "word_count": len(full_text.split()),
                    "metadata": {
                        "creator": metadata.get("/Creator", ""),
                        "producer": metadata.get("/Producer", ""),
                        "subject": metadata.get("/Subject", ""),
                        "keywords": metadata.get("/Keywords", "")
                    }
                }
                
                logger.info(f"PDF 字节流解析成功")
                return result
                
        except Exception as e:
            logger.error(f"PDF 字节流解析失败: {str(e)}")
            return {
                "success": False,
                "error": f"PDF 解析失败: {str(e)}"
            }


# 全局 PDF 解析器实例
pdf_parser = PDFParser()
