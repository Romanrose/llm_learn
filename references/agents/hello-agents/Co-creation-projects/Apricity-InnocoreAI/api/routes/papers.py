"""
论文相关API路由
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import arxiv
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic模型
class PaperSearchRequest(BaseModel):
    keywords: str
    source: str = "arxiv"
    limit: int = 10

class PaperResponse(BaseModel):
    id: str
    title: str
    authors: List[str]
    abstract: str
    url: str
    published_date: str

@router.post("/search", response_model=Dict[str, Any])
async def search_papers(request: PaperSearchRequest):
    """搜索论文 - 使用真实的 ArXiv API"""
    try:
        papers = []
        
        if request.source == "arxiv" or request.source == "all":
            # 使用 ArXiv API 搜索
            logger.info(f"正在搜索 ArXiv: {request.keywords}")
            
            # 构建搜索查询
            search = arxiv.Search(
                query=request.keywords,
                max_results=request.limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            # 获取搜索结果
            for result in search.results():
                paper = {
                    "id": result.entry_id.split('/')[-1],
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary.replace('\n', ' ').strip(),
                    "url": result.entry_id,
                    "published_date": result.published.strftime("%Y-%m-%d"),
                    "pdf_url": result.pdf_url,
                    "categories": result.categories,
                    "primary_category": result.primary_category
                }
                papers.append(paper)
            
            logger.info(f"找到 {len(papers)} 篇论文")
        
        # 如果没有找到结果，返回提示
        if not papers:
            return {
                "success": True,
                "papers": [],
                "total_found": 0,
                "keywords": request.keywords,
                "source": request.source,
                "message": "未找到相关论文，请尝试其他关键词"
            }
        
        return {
            "success": True,
            "papers": papers,
            "total_found": len(papers),
            "keywords": request.keywords,
            "source": request.source
        }
        
    except Exception as e:
        logger.error(f"论文搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.post("/upload", response_model=Dict[str, Any])
async def upload_paper(file: UploadFile = File(...)):
    """上传论文PDF"""
    try:
        # 检查文件类型
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 模拟文件上传
        file_url = f"/uploads/{file.filename}"
        
        return {
            "success": True,
            "file_url": file_url,
            "filename": file.filename,
            "size": getattr(file, 'size', 0),
            "message": "文件上传成功"
        }
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

