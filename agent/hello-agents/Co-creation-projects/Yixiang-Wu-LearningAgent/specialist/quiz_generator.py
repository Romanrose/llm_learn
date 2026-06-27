# specialist/quiz_generator.py
"""测验生成器 - 根据学习计划生成测验题"""

import json
from typing import List, Union
from hello_agents import HelloAgentsLLM


class QuizGeneratorAgent:
    """
    测验生成 Agent

    功能：
    - 基于学习计划生成问题
    - 支持不同难度级别（easy/medium/hard 或 0.0-1.0）
    - 生成单个或多个问题
    """

    def __init__(self, llm: HelloAgentsLLM):
        """
        初始化 QuizGeneratorAgent

        Args:
            llm: HelloAgentsLLM 实例
        """
        self.llm = llm

    def generate_question(
        self, plan: str, difficulty: Union[str, float] = "medium"
    ) -> str:
        """
        生成单个问题

        Args:
            plan: 学习计划内容
            difficulty: 难度级别
                - str: "easy", "medium", "hard"
                - float: 0.0-1.0（0.0=最简单，1.0=最难）

        Returns:
            生成的问题文本
        """
        # 转换难度级别
        difficulty_level = self._normalize_difficulty(difficulty)

        # 构建提示词
        user_prompt = f"""请基于以下学习计划，生成一个{difficulty_level}难度的问题：

【学习计划】
{plan[:2000]}

要求：
1. 问题应该清晰、具体
2. 难度符合 {difficulty_level} 级别
3. 直接返回问题，不需要额外说明
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个教育专家，擅长根据学习内容生成合适的测验问题。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.llm.invoke(messages)
            return response.strip()
        except Exception as e:
            # 降级：返回默认问题
            return f"请简要描述你从学习计划中学到的核心内容（难度：{difficulty_level}）"

    def generate_questions(
        self,
        plan: str,
        count: int = 3,
        difficulty: Union[str, float] = "medium",
    ) -> List[str]:
        """
        生成多个问题

        Args:
            plan: 学习计划内容
            count: 问题数量
            difficulty: 难度级别

        Returns:
            问题列表
        """
        questions = []

        for i in range(count):
            # 稍微调整每个问题的难度，增加多样性
            if isinstance(difficulty, float):
                # 在基础难度上浮动 ±0.1
                adjusted_difficulty = max(0.0, min(1.0, difficulty + (i - 1) * 0.1))
            else:
                adjusted_difficulty = difficulty

            question = self.generate_question(plan, adjusted_difficulty)
            questions.append(question)

        return questions

    def _normalize_difficulty(self, difficulty: Union[str, float]) -> str:
        """
        标准化难度级别

        Args:
            difficulty: 难度（str 或 float）

        Returns:
            标准化的难度描述
        """
        if isinstance(difficulty, float):
            if difficulty < 0.3:
                return "简单"
            elif difficulty < 0.7:
                return "中等"
            else:
                return "困难"
        else:
            # 映射字符串到中文
            mapping = {
                "easy": "简单",
                "medium": "中等",
                "hard": "困难",
            }
            return mapping.get(difficulty.lower(), "中等")
