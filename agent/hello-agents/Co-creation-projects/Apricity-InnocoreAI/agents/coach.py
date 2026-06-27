"""
InnoCore AI 写作助教 (Coach Agent)
负责风格迁移、实时润色、解释复杂概念
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from agents.base import BaseAgent
from core.database import db_manager
from core.vector_store import vector_store_manager
from core.exceptions import AgentException

class CoachAgent(BaseAgent):
    """写作助教智能体"""
    
    def __init__(self, llm=None):
        super().__init__("Coach", llm)
        
        # 添加工具
        self.add_tool("explain_concept", self._explain_concept, "解释复杂概念")
        self.add_tool("polish_text", self._polish_text, "润色文本")
        self.add_tool("mimic_style", self._mimic_style, "模仿写作风格")
        self.add_tool("get_user_style", self._get_user_style, "获取用户写作风格")
        self.add_tool("suggest_improvements", self._suggest_improvements, "建议改进")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行写作助教任务"""
        await self.validate_input(input_data)
        
        self.set_state("running")
        
        try:
            user_id = input_data["user_id"]
            task_type = input_data["task_type"]  # explain, polish, mimic, suggest
            content = input_data["content"]
            context = input_data.get("context", {})
            
            result = None
            
            if task_type == "explain":
                result = await self._handle_explain_task(user_id, content, context)
            elif task_type == "polish":
                result = await self._handle_polish_task(user_id, content, context)
            elif task_type == "mimic":
                result = await self._handle_mimic_task(user_id, content, context)
            elif task_type == "suggest":
                result = await self._handle_suggest_task(user_id, content, context)
            else:
                raise AgentException(f"不支持的任务类型: {task_type}")
            
            self.set_state("completed")
            
            return {
                "status": "success",
                "task_type": task_type,
                "user_id": user_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.set_state("error")
            raise AgentException(f"Coach Agent执行失败: {str(e)}")
    
    def get_required_fields(self) -> List[str]:
        """获取必需的输入字段"""
        return ["user_id", "task_type", "content"]
    
    async def _handle_explain_task(self, user_id: str, content: str, context: Dict) -> Dict[str, Any]:
        """处理解释任务"""
        try:
            # 获取用户的历史论文作为上下文
            user_context = await self._get_user_context(user_id)
            
            explain_prompt = f"""
            请用通俗易懂的语言解释以下内容：
            
            需要解释的内容：
            {content}
            
            上下文信息：
            {json.dumps(context, ensure_ascii=False, indent=2)}
            
            用户研究领域背景：
            {json.dumps(user_context, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 简单易懂的解释
            2. 相关的例子或类比
            3. 在该领域的重要性
            4. 可能的应用场景
            
            请以JSON格式返回结果。
            """
            
            response = await self.think(explain_prompt)
            
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "explanation": response,
                    "examples": ["需要补充具体例子"],
                    "importance": "在相关领域具有重要意义",
                    "applications": ["潜在应用场景"]
                }
            
            self._add_to_history(f"完成解释任务: {content[:50]}...")
            return result
            
        except Exception as e:
            self._add_to_history(f"解释任务失败: {str(e)}")
            return {
                "explanation": f"解释过程中出现错误: {str(e)}",
                "examples": [],
                "importance": "",
                "applications": []
            }
    
    async def _handle_polish_task(self, user_id: str, content: str, context: Dict) -> Dict[str, Any]:
        """处理润色任务"""
        try:
            # 获取用户的写作风格偏好
            user_style = await self._get_user_writing_style(user_id)
            
            # 获取相关的风格参考
            style_references = await self._get_style_references(user_id, content)
            
            polish_prompt = f"""
            请将以下文本润色为地道的学术英语：
            
            原文：
            {content}
            
            用户写作风格偏好：
            {json.dumps(user_style, ensure_ascii=False, indent=2)}
            
            风格参考：
            {json.dumps(style_references, ensure_ascii=False, indent=2)}
            
            上下文信息：
            {json.dumps(context, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 润色后的英文文本
            2. 主要修改说明
            3. 风格改进建议
            4. 参考的论文句式来源
            
            要求：
            - 保持原意不变
            - 使用地道的学术表达
            - 符合目标期刊/会议的写作风格
            - 在注释中说明参考了哪些历史论文的句式
            
            请以JSON格式返回结果。
            """
            
            response = await self.think(polish_prompt)
            
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "polished_text": response,
                    "modifications": ["语法修正", "词汇优化"],
                    "style_suggestions": ["建议使用更正式的表达"],
                    "references": ["基于学术写作规范"]
                }
            
            self._add_to_history(f"完成润色任务: {content[:50]}...")
            return result
            
        except Exception as e:
            self._add_to_history(f"润色任务失败: {str(e)}")
            return {
                "polished_text": content,
                "modifications": [f"润色过程中出现错误: {str(e)}"],
                "style_suggestions": [],
                "references": []
            }
    
    async def _handle_mimic_task(self, user_id: str, content: str, context: Dict) -> Dict[str, Any]:
        """处理模仿任务"""
        try:
            # 获取目标风格参考
            target_style = context.get("target_style", "formal_academic")
            reference_papers = context.get("reference_papers", [])
            
            # 如果没有指定参考论文，从用户库中获取
            if not reference_papers:
                reference_papers = await self._get_user_top_papers(user_id, limit=3)
            
            mimic_prompt = f"""
            请基于以下参考论文的写作风格，重写给定内容：
            
            原文：
            {content}
            
            目标风格：
            {target_style}
            
            参考论文：
            {json.dumps(reference_papers, ensure_ascii=False, indent=2)}
            
            上下文信息：
            {json.dumps(context, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 重写后的文本
            2. 风格分析（说明如何体现目标风格）
            3. 具体的模仿技巧
            4. 参考的句式结构
            
            请以JSON格式返回结果。
            """
            
            response = await self.think(mimic_prompt)
            
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "rewritten_text": response,
                    "style_analysis": "基于学术写作风格进行重写",
                    "mimic_techniques": ["句式结构模仿", "词汇选择"],
                    "reference_structures": ["学术表达方式"]
                }
            
            self._add_to_history(f"完成模仿任务: {content[:50]}...")
            return result
            
        except Exception as e:
            self._add_to_history(f"模仿任务失败: {str(e)}")
            return {
                "rewritten_text": content,
                "style_analysis": f"模仿过程中出现错误: {str(e)}",
                "mimic_techniques": [],
                "reference_structures": []
            }
    
    async def _handle_suggest_task(self, user_id: str, content: str, context: Dict) -> Dict[str, Any]:
        """处理建议任务"""
        try:
            # 获取用户的历史写作数据
            user_writing_history = await self._get_user_writing_history(user_id)
            
            suggest_prompt = f"""
            请对以下文本提供改进建议：
            
            文本内容：
            {content}
            
            用户写作历史：
            {json.dumps(user_writing_history, ensure_ascii=False, indent=2)}
            
            上下文信息：
            {json.dumps(context, ensure_ascii=False, indent=2)}
            
            请提供：
            1. 整体评价
            2. 具体改进建议（按重要性排序）
            3. 语法和表达问题
            4. 结构优化建议
            5. 学术表达改进
            
            请以JSON格式返回结果。
            """
            
            response = await self.think(suggest_prompt)
            
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                result = {
                    "overall_evaluation": "文本整体质量良好",
                    "improvement_suggestions": ["建议加强逻辑表达", "可以增加更多细节"],
                    "grammar_issues": ["检查时态一致性"],
                    "structure_suggestions": ["建议优化段落结构"],
                    "academic_improvements": ["使用更正式的学术词汇"]
                }
            
            self._add_to_history(f"完成建议任务: {content[:50]}...")
            return result
            
        except Exception as e:
            self._add_to_history(f"建议任务失败: {str(e)}")
            return {
                "overall_evaluation": f"分析过程中出现错误: {str(e)}",
                "improvement_suggestions": [],
                "grammar_issues": [],
                "structure_suggestions": [],
                "academic_improvements": []
            }
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """获取用户的研究背景"""
        try:
            user = await db_manager.get_user(user_id)
            if user:
                return user.get("profile", {})
            return {}
        except Exception:
            return {}
    
    async def _get_user_writing_style(self, user_id: str) -> Dict[str, Any]:
        """获取用户写作风格偏好"""
        user_context = await self._get_user_context(user_id)
        return user_context.get("writing_style", {
            "tone": "formal",
            "complexity": "medium",
            "preferred_journals": ["Nature", "Science"],
            "language": "english"
        })
    
    async def _get_style_references(self, user_id: str, content: str) -> List[Dict[str, Any]]:
        """获取风格参考"""
        try:
            # 搜索用户库中的相关论文
            search_results = await vector_store_manager.hybrid_search(
                query=content,
                user_id=user_id,
                top_k=3,
                include_l2=True,
                include_l1=False
            )
            
            references = []
            for result in search_results:
                payload = result["payload"]
                references.append({
                    "title": payload.get("title", ""),
                    "abstract": payload.get("abstract", "")[:200],
                    "similarity": result["score"]
                })
            
            return references
            
        except Exception:
            return []
    
    async def _get_user_top_papers(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """获取用户评分最高的论文"""
        try:
            user_papers = await db_manager.get_user_papers(user_id, limit=limit)
            
            top_papers = []
            for paper in user_papers:
                top_papers.append({
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", "")[:300],
                    "rating": paper.get("rating", 0),
                    "authors": paper.get("authors", [])
                })
            
            return top_papers
            
        except Exception:
            return []
    
    async def _get_user_writing_history(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户写作历史"""
        try:
            # 这里应该从用户的写作历史记录中获取数据
            # 暂时返回模拟数据
            return [
                {
                    "date": "2024-01-01",
                    "content_type": "abstract",
                    "word_count": 200,
                    "feedback_score": 4.5
                }
            ]
        except Exception:
            return []
    
    # 工具方法
    async def _explain_concept(self, concept: str, context: Dict = None) -> Dict:
        """解释概念工具"""
        return await self._handle_explain_task(
            context.get("user_id", ""), 
            concept, 
            context or {}
        )
    
    async def _polish_text(self, text: str, context: Dict = None) -> Dict:
        """润色文本工具"""
        return await self._handle_polish_task(
            context.get("user_id", ""), 
            text, 
            context or {}
        )
    
    async def _mimic_style(self, text: str, target_style: str, context: Dict = None) -> Dict:
        """模仿风格工具"""
        ctx = context or {}
        ctx["target_style"] = target_style
        return await self._handle_mimic_task(
            ctx.get("user_id", ""), 
            text, 
            ctx
        )
    
    async def _get_user_style(self, user_id: str) -> Dict:
        """获取用户风格工具"""
        return await self._get_user_writing_style(user_id)
    
    async def _suggest_improvements(self, text: str, context: Dict = None) -> Dict:
        """建议改进工具"""
        return await self._handle_suggest_task(
            context.get("user_id", ""), 
            text, 
            context or {}
        )