"""
写作辅助API路由
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
from core.config import get_config
from core.llm_adapter import get_llm_adapter

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化 LLM 适配器（基于 HelloAgent）
config = get_config()
try:
    llm = get_llm_adapter() if config.llm.api_key else None
except Exception as e:
    logger.warning(f"LLM 初始化失败: {str(e)}")
    llm = None

# Pydantic模型
class WritingAssistanceRequest(BaseModel):
    user_id: str
    task_type: str  # explain, polish, mimic, suggest
    content: str
    context: Optional[Dict[str, Any]] = {}

class ExplainRequest(BaseModel):
    user_id: str
    concept: str
    context: Optional[Dict[str, Any]] = {}

class PolishRequest(BaseModel):
    user_id: str
    text: str
    target_style: Optional[str] = "academic"

class WritingCoachRequest(BaseModel):
    text: str
    style: str = "formal"
    task: str = "polish"  # polish, translate, explain, expand
    context: Optional[Dict[str, Any]] = {}

class MimicRequest(BaseModel):
    user_id: str
    text: str
    target_style: str
    reference_papers: Optional[list] = []
    context: Optional[Dict[str, Any]] = {}

class SuggestRequest(BaseModel):
    user_id: str
    text: str
    context: Optional[Dict[str, Any]] = {}

@router.post("/coach", response_model=Dict[str, Any])
async def writing_coach(request: WritingCoachRequest):
    """写作助手 - 使用真实的 AI 处理"""
    try:
        if not llm:
            raise HTTPException(status_code=503, detail="AI 服务未配置，请设置 OPENAI_API_KEY")
        
        logger.info(f"处理写作任务: {request.task}, 风格: {request.style}")
        
        # 根据任务类型生成提示词
        prompts = {
            "polish": f"""作为一位专业的学术写作编辑，请帮我润色以下文本，使其符合{request.style}学术写作标准：

原文：
{request.text}

请提供：
1. 润色后的文本（保持原意，提升表达质量）
2. 具体的改进说明
3. 写作建议

要求：
- 保持学术严谨性
- 提升表达清晰度
- 使用恰当的学术用语
- 改善句子结构和逻辑流畅性""",
            
            "translate": f"""请将以下中文学术文本翻译成专业的英文学术论文表达：

原文：
{request.text}

要求：
- 保持学术专业性和准确性
- 使用地道的英文学术表达
- 符合{request.style}风格的学术写作规范
- 保持技术术语的准确性""",
            
            "explain": f"""请详细解释以下概念或内容：

{request.text}

要求：
- 用通俗易懂的语言解释
- 保持技术准确性
- 提供具体例子
- 说明应用场景和重要性""",
            
            "expand": f"""请扩展以下内容，使其更加详细和完整：

原文：
{request.text}

要求：
- 添加必要的背景信息
- 补充相关的理论支持
- 扩展方法论描述
- 增加潜在影响和应用
- 保持逻辑连贯性
- 符合{request.style}学术写作风格"""
        }
        
        prompt = prompts.get(request.task, prompts["polish"])
        
        # 调用 LLM 处理
        response = await llm.ainvoke(prompt)
        result_content = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "success": True,
            "task": request.task,
            "style": request.style,
            "original": request.text,
            "result": result_content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"写作助手处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@router.post("/explain", response_model=Dict[str, Any])
async def explain_concept(request: ExplainRequest):
    """解释复杂概念"""
    try:
        # 模拟概念解释
        return {
            "success": True,
            "concept": request.concept,
            "explanation": f"[Detailed explanation of {request.concept} in accessible terms while maintaining technical accuracy]",
            "examples": ["Example 1", "Example 2"],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"概念解释失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/polish", response_model=Dict[str, Any])
async def polish_text(request: PolishRequest):
    """润色文本"""
    try:
        # 模拟文本润色
        return {
            "success": True,
            "original": request.text,
            "improved": f"Based on {request.target_style} writing standards, the text can be improved: [Enhanced version]",
            "suggestions": ["Use more precise terminology", "Improve sentence structure"],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"文本润色失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mimic", response_model=Dict[str, Any])
async def mimic_style(request: MimicRequest):
    """模仿写作风格"""
    try:
        # 模拟风格模仿
        return {
            "success": True,
            "original": request.text,
            "mimicked": f"[Text rewritten in {request.target_style} style]",
            "style_analysis": f"Analysis of {request.target_style} writing characteristics",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"风格模仿失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest", response_model=Dict[str, Any])
async def suggest_improvements(request: SuggestRequest):
    """建议改进"""
    try:
        # 模拟改进建议
        return {
            "success": True,
            "original": request.text,
            "suggestions": [
                "Consider adding more specific examples",
                "Strengthen the introduction",
                "Include recent citations",
                "Clarify the methodology"
            ],
            "improved_version": "[Improved version with suggestions applied]",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"改进建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/style")
async def get_user_writing_style(user_id: str):
    """获取用户写作风格"""
    try:
        # 这里需要实现用户写作风格分析
        # 暂时返回模拟结果
        
        style_profile = {
            "user_id": user_id,
            "writing_style": {
                "tone": "formal_academic",
                "complexity": "medium",
                "sentence_length": "medium",
                "vocabulary_richness": "high",
                "clarity": "good"
            },
            "preferred_patterns": [
                "句式模式1",
                "句式模式2"
            ],
            "common_phrases": [
                "常用短语1",
                "常用短语2"
            ],
            "improvement_areas": [
                "改进领域1",
                "改进领域2"
            ],
            "style_evolution": {
                "last_month": "上个月的风格变化",
                "trend": "improving"
            }
        }
        
        return {
            "success": True,
            "style_profile": style_profile
        }
        
    except Exception as e:
        logger.error(f"获取用户写作风格失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/templates")
async def get_writing_templates(user_id: str):
    """获取写作模板"""
    try:
        # 这里需要实现写作模板推荐
        # 暂时返回模拟结果
        
        templates = {
            "user_id": user_id,
            "templates": [
                {
                    "id": "abstract_template",
                    "name": "摘要模板",
                    "category": "academic",
                    "structure": [
                        "背景介绍",
                        "问题陈述", 
                        "方法概述",
                        "主要结果",
                        "结论意义"
                    ],
                    "example": "摘要示例...",
                    "usage_count": 15
                },
                {
                    "id": "introduction_template",
                    "name": "引言模板",
                    "category": "academic",
                    "structure": [
                        "研究背景",
                        "相关工作",
                        "研究空白",
                        "主要贡献",
                        "论文结构"
                    ],
                    "example": "引言示例...",
                    "usage_count": 8
                }
            ],
            "recommended_templates": [
                "推荐模板1",
                "推荐模板2"
            ]
        }
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        logger.error(f"获取写作模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/grammar", response_model=Dict[str, Any])
async def check_grammar(text: str, user_id: Optional[str] = None):
    """语法检查"""
    try:
        # 这里需要实现语法检查逻辑
        # 暂时返回模拟结果
        
        grammar_check = {
            "text": text,
            "errors": [
                {
                    "type": "grammar",
                    "message": "语法错误描述",
                    "position": {"start": 10, "end": 20},
                    "suggestion": "修改建议",
                    "severity": "medium"
                }
            ],
            "suggestions": [
                {
                    "type": "style",
                    "message": "风格建议",
                    "position": {"start": 30, "end": 40},
                    "suggestion": "风格改进建议"
                }
            ],
            "score": 85,
            "corrected_text": "修正后的文本..."
        }
        
        return {
            "success": True,
            "grammar_check": grammar_check
        }
        
    except Exception as e:
        logger.error(f"语法检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/plagiarism", response_model=Dict[str, Any])
async def check_plagiarism(text: str, user_id: Optional[str] = None):
    """抄袭检查"""
    try:
        # 这里需要实现抄袭检查逻辑
        # 暂时返回模拟结果
        
        plagiarism_check = {
            "text": text,
            "similarity_score": 15.5,
            "sources": [
                {
                    "title": "相似文献标题",
                    "authors": ["作者1", "作者2"],
                    "similarity": 12.3,
                    "matched_text": "匹配的文本片段...",
                    "url": "文献链接"
                }
            ],
            "originality_score": 84.5,
            "risk_level": "low",
            "recommendations": [
                "建议1",
                "建议2"
            ]
        }
        
        return {
            "success": True,
            "plagiarism_check": plagiarism_check
        }
        
    except Exception as e:
        logger.error(f"抄袭检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))