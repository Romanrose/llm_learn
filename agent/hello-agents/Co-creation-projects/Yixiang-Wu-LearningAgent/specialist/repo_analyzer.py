# specialist/repo_analyzer.py
"""GitHub 仓库分析专家"""

import re
from typing import Dict, List, Optional
import requests
from hello_agents import HelloAgentsLLM


class RepoAnalyzerAgent:
    """
    GitHub 仓库分析专家

    功能：
    - 从 GitHub URL 提取仓库信息
    - 获取项目基本信息（描述、语言、stars等）
    - 获取并分析 README 内容
    - 识别技术栈
    - 推断前置知识要求
    """

    GITHUB_API_BASE = "https://api.github.com"

    def __init__(self, llm: HelloAgentsLLM, github_token: Optional[str] = None):
        """
        初始化 RepoAnalyzerAgent

        Args:
            llm: HelloAgentsLLM 实例
            github_token: GitHub API Token（可选，用于提高速率限制）
        """
        self.llm = llm
        self.github_token = github_token
        self.headers = {}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def _extract_repo_info(self, url: str) -> tuple[str, str]:
        """
        从 GitHub URL 提取 owner 和 repo 名称

        Args:
            url: GitHub URL（如 https://github.com/vuejs/core）

        Returns:
            (owner, repo) 元组
        """
        # 去掉 .git 后缀
        url = url.rstrip(".git")

        # 提取 owner 和 repo
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1]
            return owner, repo

        raise ValueError(f"无法解析 GitHub URL: {url}")

    def _fetch_repo_info(self, owner: str, repo: str) -> Dict:
        """
        获取仓库基本信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库信息字典
        """
        url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _fetch_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        获取 README 内容

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            README 文本内容，如果不存在则返回 None
        """
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # README 内容是 base64 编码的
                import base64

                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
        except Exception:
            pass
        return None

    def _extract_tech_stack_from_text(self, text: str) -> List[str]:
        """
        从文本中提取技术栈关键词

        Args:
            text: 文本内容

        Returns:
            技术栈列表
        """
        # 常见技术关键词
        tech_keywords = [
            "React",
            "Vue",
            "Angular",
            "Svelte",
            "TypeScript",
            "JavaScript",
            "Python",
            "Java",
            "Go",
            "Rust",
            "Node.js",
            "Django",
            "Flask",
            "FastAPI",
            "Express",
            "TensorFlow",
            "PyTorch",
            "Keras",
            "Docker",
            "Kubernetes",
            "MongoDB",
            "PostgreSQL",
            "MySQL",
            "Redis",
            "TailwindCSS",
            "Bootstrap",
            "CSS",
            "HTML",
        ]

        found_techs = []
        text_lower = text.lower()

        for tech in tech_keywords:
            if tech.lower() in text_lower:
                found_techs.append(tech)

        return found_techs

    def _analyze_with_llm(
        self, repo_info: Dict, readme: Optional[str]
    ) -> Dict[str, any]:
        """
        使用 LLM 深度分析仓库

        Args:
            repo_info: 仓库基本信息
            readme: README 内容（可选）

        Returns:
            分析结果字典
        """
        # 构建分析提示
        repo_name = repo_info.get("name", "unknown")
        description = repo_info.get("description", "")
        language = repo_info.get("language", "")
        topics = repo_info.get("topics", [])

        user_prompt = f"""请分析以下 GitHub 仓库并提取学习相关信息：

【仓库名称】
{repo_name}

【描述】
{description}

【主要语言】
{language}

【主题标签】
{', '.join(topics) if topics else '无'}

"""

        if readme:
            user_prompt += f"""
【README 内容】
{readme[:2000]}  # 限制长度
"""

        user_prompt += """
请提供以下信息（JSON格式）：
{
  "domain": "学习领域（如 web-development, data-science 等）",
  "tech_stack": ["技术1", "技术2", "..."],
  "prerequisites": ["前置知识1", "前置知识2", "..."],
  "learning_difficulty": "初级/中级/高级",
  "estimated_weeks": 学习所需周数（整数）
}
"""

        messages = [
            {
                "role": "system",
                "content": "你是一个技术教育专家，擅长分析开源项目并提取学习相关信息。",
            },
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.llm.invoke(messages)
            # 简化实现：返回基本信息（实际应该解析 LLM 返回的 JSON）
            return {
                "domain": repo_name.lower().replace("-", " "),
                "tech_stack": self._extract_tech_stack_from_text(
                    description + " " + language
                ),
                "prerequisites": [],
                "learning_difficulty": "中级",
                "estimated_weeks": 4,
            }
        except Exception:
            # 降级：使用基于规则的分析
            return {
                "domain": repo_name.lower().replace("-", " "),
                "tech_stack": [language] if language else [],
                "prerequisites": [],
                "learning_difficulty": "中级",
                "estimated_weeks": 4,
            }

    def analyze(self, github_url: str) -> Dict[str, any]:
        """
        分析 GitHub 仓库

        Args:
            github_url: GitHub 仓库 URL

        Returns:
            分析结果字典，包含：
            - domain: 学习领域
            - tech_stack: 技术栈列表
            - prerequisites: 前置知识列表
            - description: 项目描述
            - language: 主要语言
            - stars: Star 数量
        """
        # 提取仓库信息
        owner, repo = self._extract_repo_info(github_url)

        # 获取基本信息
        repo_info = self._fetch_repo_info(owner, repo)

        # 获取 README
        readme = self._fetch_readme(owner, repo)

        # 提取技术栈（基于规则）
        tech_stack = []
        if repo_info.get("language"):
            tech_stack.append(repo_info["language"])

        if readme:
            tech_stack.extend(self._extract_tech_stack_from_text(readme))

        # 去重
        tech_stack = list(set(tech_stack))

        # 使用 LLM 深度分析（如果可用）
        llm_analysis = self._analyze_with_llm(repo_info, readme)

        # 合并结果
        result = {
            "domain": llm_analysis.get("domain", repo.lower().replace("-", " ")),
            "tech_stack": tech_stack,
            "prerequisites": llm_analysis.get("prerequisites", []),
            "description": repo_info.get("description", ""),
            "language": repo_info.get("language", ""),
            "stars": repo_info.get("stargazers_count", 0),
            "learning_difficulty": llm_analysis.get("learning_difficulty", "中级"),
            "estimated_weeks": llm_analysis.get("estimated_weeks", 4),
        }

        return result
