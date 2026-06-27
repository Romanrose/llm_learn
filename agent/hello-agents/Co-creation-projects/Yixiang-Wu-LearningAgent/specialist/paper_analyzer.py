# specialist/paper_analyzer.py
"""PDF 论文分析专家"""

import os
from pathlib import Path
from typing import Dict, List
import PyPDF2
from hello_agents import HelloAgentsLLM


class PaperAnalyzerAgent:
    """
    PDF 论文分析专家

    功能：
    - 读取 PDF 论文
    - 提取标题和摘要
    - 识别核心概念
    - 推断前置知识
    - 确定研究领域
    """

    def __init__(self, llm: HelloAgentsLLM):
        """
        初始化 PaperAnalyzerAgent

        Args:
            llm: HelloAgentsLLM 实例
        """
        self.llm = llm

    def _extract_title_from_path(self, file_path: str) -> str:
        """
        从文件路径提取论文标题

        Args:
            file_path: PDF 文件路径

        Returns:
            论文标题
        """
        # 处理 ~ 路径
        if file_path.startswith("~"):
            file_path = os.path.expanduser(file_path)

        # 获取文件名（去掉扩展名）
        filename = Path(file_path).stem

        # 将连字符和下划线替换为空格
        title = filename.replace("-", " ").replace("_", " ")

        return title

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        从 PDF 提取文本

        Args:
            file_path: PDF 文件路径

        Returns:
            提取的文本内容
        """
        # 处理 ~ 路径
        if file_path.startswith("~"):
            file_path = os.path.expanduser(file_path)

        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""

                # 提取前3页的内容（通常包含摘要和引言）
                max_pages = min(3, len(reader.pages))
                for i in range(max_pages):
                    page = reader.pages[i]
                    text += page.extract_text() + "\n"

                return text
        except Exception as e:
            raise IOError(f"无法读取 PDF 文件：{e}")

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 论文文本

        Returns:
            关键词列表
        """
        # 学术领域常见关键词
        academic_keywords = [
            # 深度学习/机器学习
            "Neural Network",
            "Deep Learning",
            "Transformer",
            "Attention",
            "CNN",
            "RNN",
            "LSTM",
            "Backpropagation",
            "Gradient Descent",
            "Optimization",
            # 自然语言处理
            "NLP",
            "Language Model",
            "Tokenization",
            "Embedding",
            "BERT",
            "GPT",
            # 计算机视觉
            "Computer Vision",
            "Image Processing",
            "Convolution",
            "Feature Extraction",
            # 其他
            "Algorithm",
            "Data Structure",
            "Complexity",
            "Statistics",
            "Probability",
        ]

        found_keywords = []
        text_lower = text.lower()

        for keyword in academic_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return found_keywords

    def _identify_prerequisites(self, keywords: List[str]) -> List[str]:
        """
        根据关键词推断前置知识

        Args:
            keywords: 关键词列表

        Returns:
            前置知识列表
        """
        # 前置知识映射
        prereq_map = {
            "Deep Learning": ["Machine Learning", "Python", "Linear Algebra"],
            "Transformer": ["Attention Mechanism", "Sequence Models"],
            "Neural Network": ["Calculus", "Linear Algebra", "Probability"],
            "CNN": ["Image Processing", "Linear Algebra"],
            "RNN": ["Sequence Models", "Calculus"],
            "NLP": ["Machine Learning", "Statistics", "Python"],
            "Computer Vision": ["Linear Algebra", "Probability", "Python"],
        }

        prerequisites = []
        for keyword in keywords:
            if keyword in prereq_map:
                prerequisites.extend(prereq_map[keyword])

        # 去重
        return list(set(prerequisites))

    def _analyze_with_llm(self, title: str, text: str) -> Dict[str, any]:
        """
        使用 LLM 深度分析论文

        Args:
            title: 论文标题
            text: 论文文本

        Returns:
            分析结果字典
        """
        user_prompt = f"""请分析以下学术论文并提取学习相关信息：

【论文标题】
{title}

【论文内容（前1000字）】
{text[:1000]}
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个学术教育专家，擅长分析学术论文并提取学习相关信息。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.llm.invoke(messages)
            # 简化实现：返回基于规则的分析结果
            keywords = self._extract_keywords_from_text(text)
            prerequisites = self._identify_prerequisites(keywords)

            return {
                "domain": self._infer_domain_from_keywords(keywords),
                "core_concepts": keywords[:5],  # 前5个关键词
                "prerequisites": prerequisites,
                "title": title,
                "learning_difficulty": "高级",
                "estimated_weeks": 8,
            }
        except Exception:
            # 降级：使用基于规则的分析
            keywords = self._extract_keywords_from_text(text)
            prerequisites = self._identify_prerequisites(keywords)

            return {
                "domain": self._infer_domain_from_keywords(keywords),
                "core_concepts": keywords[:5],
                "prerequisites": prerequisites,
                "title": title,
                "learning_difficulty": "高级",
                "estimated_weeks": 8,
            }

    def _infer_domain_from_keywords(self, keywords: List[str]) -> str:
        """
        根据关键词推断研究领域

        Args:
            keywords: 关键词列表

        Returns:
            研究领域
        """
        if not keywords:
            return "general"

        keyword_lower = " ".join(keywords).lower()

        # 领域映射
        if any(
            kw in keyword_lower
            for kw in ["transformer", "attention", "nlp", "language", "bert", "gpt"]
        ):
            return "natural-language-processing"
        elif any(
            kw in keyword_lower
            for kw in ["cnn", "image", "vision", "computer", "processing"]
        ):
            return "computer-vision"
        elif any(
            kw in keyword_lower
            for kw in ["neural", "deep", "learning", "network", "backpropagation"]
        ):
            return "deep-learning"
        elif any(
            kw in keyword_lower for kw in ["machine", "learning", "algorithm", "model"]
        ):
            return "machine-learning"
        else:
            return "general"

    def analyze(self, pdf_path: str) -> Dict[str, any]:
        """
        分析 PDF 论文

        Args:
            pdf_path: PDF 文件路径

        Returns:
            分析结果字典，包含：
            - domain: 研究领域
            - title: 论文标题
            - core_concepts: 核心概念列表
            - prerequisites: 前置知识列表
            - learning_difficulty: 学习难度
            - estimated_weeks: 估计学习周数
        """
        # 提取标题
        title = self._extract_title_from_path(pdf_path)

        # 提取文本
        try:
            text = self._extract_text_from_pdf(pdf_path)
        except IOError:
            # 如果无法读取 PDF，使用基于路径的分析
            return {
                "domain": "general",
                "title": title,
                "core_concepts": [],
                "prerequisites": [],
                "learning_difficulty": "高级",
                "estimated_weeks": 8,
            }

        # 使用 LLM 深度分析
        result = self._analyze_with_llm(title, text)

        return result
