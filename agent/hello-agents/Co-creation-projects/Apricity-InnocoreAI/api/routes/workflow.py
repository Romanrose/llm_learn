"""
工作流API路由 - 协调多个智能体完成复杂任务
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
import asyncio
from agents.controller import agent_controller

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic模型
class WorkflowRequest(BaseModel):
    keywords: str
    analysis_type: str = "summary"  # summary, innovation, comparison, comprehensive
    citation_format: str = "bibtex"  # bibtex, apa, ieee, mla
    writing_task: Optional[str] = None  # improve, polish, translate
    limit: int = 5  # 搜索论文数量

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str  # running, completed, failed
    current_step: str
    progress: int  # 0-100

@router.post("/complete", response_model=Dict[str, Any])
async def complete_workflow(request: WorkflowRequest):
    """
    完整工作流：搜索 -> 分析 -> 校验引用 -> 写作辅助
    自动协调所有智能体完成任务
    """
    try:
        workflow_id = f"workflow_{asyncio.get_event_loop().time()}"
        results = {
            "workflow_id": workflow_id,
            "status": "running",
            "steps": []
        }
        
        # 步骤 1: Hunter - 搜索论文
        logger.info(f"[工作流 {workflow_id}] 步骤 1/4: 搜索论文")
        try:
            from api.routes.papers import search_papers, PaperSearchRequest
            
            search_result = await search_papers(PaperSearchRequest(
                keywords=request.keywords,
                source="arxiv",
                limit=request.limit
            ))
            
            papers = search_result.get("papers", [])
            results["steps"].append({
                "step": 1,
                "name": "Hunter - 论文搜索",
                "status": "completed",
                "result": {
                    "total_found": len(papers),
                    "papers": papers
                }
            })
            
            if not papers:
                raise HTTPException(status_code=404, detail="未找到相关论文")
            
        except Exception as e:
            logger.error(f"论文搜索失败: {str(e)}")
            results["steps"].append({
                "step": 1,
                "name": "Hunter - 论文搜索",
                "status": "failed",
                "error": str(e)
            })
            results["status"] = "failed"
            return results
        
        # 步骤 2: Miner - 分析每篇论文
        logger.info(f"[工作流 {workflow_id}] 步骤 2/4: 分析论文")
        analyses = []
        try:
            from api.routes.analysis import analyze_paper, PaperAnalysisRequest
            
            # 分析前3篇论文
            for i, paper in enumerate(papers[:3]):
                try:
                    analysis_result = await analyze_paper(PaperAnalysisRequest(
                        paper_url=paper["url"],
                        analysis_type=request.analysis_type
                    ))
                    analyses.append({
                        "paper_id": paper["id"],
                        "title": paper["title"],
                        "analysis": analysis_result.get("analysis", "")
                    })
                except Exception as e:
                    logger.warning(f"分析论文 {paper['id']} 失败: {str(e)}")
                    continue
            
            results["steps"].append({
                "step": 2,
                "name": "Miner - 论文分析",
                "status": "completed",
                "result": {
                    "total_analyzed": len(analyses),
                    "analyses": analyses
                }
            })
            
        except Exception as e:
            logger.error(f"论文分析失败: {str(e)}")
            results["steps"].append({
                "step": 2,
                "name": "Miner - 论文分析",
                "status": "failed",
                "error": str(e)
            })
        
        # 步骤 3: Validator - 生成和校验引用
        logger.info(f"[工作流 {workflow_id}] 步骤 3/4: 生成引用")
        citations = []
        try:
            from api.routes.citations import validate_citation, CitationValidationRequest
            
            # 为每篇论文生成引用
            for paper in papers[:3]:
                try:
                    # 构建引用文本
                    authors_str = ", ".join(paper["authors"][:3])
                    if len(paper["authors"]) > 3:
                        authors_str += " et al."
                    
                    citation_text = f"{authors_str} ({paper['published_date'][:4]}). {paper['title']}. arXiv:{paper['id']}"
                    
                    citation_result = await validate_citation(CitationValidationRequest(
                        citation=citation_text,
                        format=request.citation_format
                    ))
                    
                    citations.append({
                        "paper_id": paper["id"],
                        "title": paper["title"],
                        "formatted_citation": citation_result.get("formatted_citation", "")
                    })
                except Exception as e:
                    logger.warning(f"生成引用失败: {str(e)}")
                    continue
            
            results["steps"].append({
                "step": 3,
                "name": "Validator - 引用生成",
                "status": "completed",
                "result": {
                    "total_citations": len(citations),
                    "citations": citations
                }
            })
            
        except Exception as e:
            logger.error(f"引用生成失败: {str(e)}")
            results["steps"].append({
                "step": 3,
                "name": "Validator - 引用生成",
                "status": "failed",
                "error": str(e)
            })
        
        # 步骤 4: Coach - 生成综合报告（可选）
        if request.writing_task:
            logger.info(f"[工作流 {workflow_id}] 步骤 4/4: 生成报告")
            try:
                from api.routes.writing import writing_coach, WritingCoachRequest
                
                # 构建综合报告文本
                report_text = f"# 关于 '{request.keywords}' 的研究综述\n\n"
                report_text += f"## 搜索结果\n找到 {len(papers)} 篇相关论文\n\n"
                
                if analyses:
                    report_text += "## 论文分析\n"
                    for i, analysis in enumerate(analyses[:3], 1):
                        report_text += f"\n### {i}. {analysis['title']}\n"
                        report_text += f"{analysis['analysis'][:500]}...\n"
                
                if citations:
                    report_text += "\n## 参考文献\n"
                    for i, citation in enumerate(citations, 1):
                        report_text += f"{i}. {citation['formatted_citation']}\n"
                
                # 使用 Coach 改进报告
                writing_result = await writing_coach(WritingCoachRequest(
                    text=report_text,
                    style="academic",
                    task=request.writing_task
                ))
                
                results["steps"].append({
                    "step": 4,
                    "name": "Coach - 报告生成",
                    "status": "completed",
                    "result": {
                        "report": writing_result.get("result", "")
                    }
                })
                
            except Exception as e:
                logger.error(f"报告生成失败: {str(e)}")
                results["steps"].append({
                    "step": 4,
                    "name": "Coach - 报告生成",
                    "status": "failed",
                    "error": str(e)
                })
        
        # 完成工作流
        results["status"] = "completed"
        results["summary"] = {
            "total_papers": len(papers),
            "analyzed_papers": len(analyses),
            "generated_citations": len(citations),
            "keywords": request.keywords
        }
        
        logger.info(f"[工作流 {workflow_id}] 完成")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"工作流执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"工作流执行失败: {str(e)}")

@router.post("/search-and-analyze", response_model=Dict[str, Any])
async def search_and_analyze(request: WorkflowRequest):
    """
    简化工作流：搜索 + 分析
    只执行搜索和分析步骤
    """
    try:
        results = {
            "status": "running",
            "steps": []
        }
        
        # 步骤 1: 搜索论文
        from api.routes.papers import search_papers, PaperSearchRequest
        
        search_result = await search_papers(PaperSearchRequest(
            keywords=request.keywords,
            source="arxiv",
            limit=request.limit
        ))
        
        papers = search_result.get("papers", [])
        results["steps"].append({
            "step": 1,
            "name": "搜索论文",
            "status": "completed",
            "papers": papers
        })
        
        if not papers:
            raise HTTPException(status_code=404, detail="未找到相关论文")
        
        # 步骤 2: 分析第一篇论文
        from api.routes.analysis import analyze_paper, PaperAnalysisRequest
        
        first_paper = papers[0]
        analysis_result = await analyze_paper(PaperAnalysisRequest(
            paper_url=first_paper["url"],
            analysis_type=request.analysis_type
        ))
        
        results["steps"].append({
            "step": 2,
            "name": "分析论文",
            "status": "completed",
            "analysis": analysis_result
        })
        
        results["status"] = "completed"
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索和分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")

@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """获取工作流状态"""
    try:
        # 这里可以实现工作流状态跟踪
        # 暂时返回模拟状态
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "progress": 100,
            "message": "工作流已完成"
        }
    except Exception as e:
        logger.error(f"获取工作流状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
