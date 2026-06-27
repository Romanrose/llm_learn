import os
import re
from typing import List, Dict


class ProblemRepository:
    def __init__(self, root_dir="E:\PycharmProject_lmx\HelloAgents-main\output"):
        self.root_dir = root_dir
        self.problems = self._load_all_problems()

    def _load_all_problems(self) -> List[Dict]:
        problems = []

        for dirname in os.listdir(self.root_dir):
            readme_path = os.path.join(self.root_dir, dirname, "README.md")
            if not os.path.exists(readme_path):
                continue

            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            problem = self._parse_problem(content)
            if problem:
                problem["slug"] = dirname
                problem["path"] = readme_path
                problem["content"] = content
                problems.append(problem)

        return problems

    def _parse_problem(self, text: str) -> Dict | None:
        title = self._extract(r"# \[(.*?)\]", text)
        if not title:
            return None

        description = self._extract_block(
            text,
            start="## Description",
            end="\\*\\*Example"
        )

        examples = self._parse_examples(text)

        constraints = self._extract_block(
            text,
            start="\\*\\*Constraints:\\*\\*",
            end="\\*\\*Follow-up"
        )

        tags = self._extract(r"\*\*Tags:\*\*(.*)", text)
        difficulty = self._extract(r"\*\*Difficulty:\*\*(.*)", text)

        return {
            "title": title.strip(),
            "description": description.strip() if description else "",
            "examples": examples,
            "constraints": constraints.strip() if constraints else "",
            "tags": [t.strip() for t in tags.split(",")] if tags else [],
            "difficulty": difficulty.strip() if difficulty else "Unknown",
        }

    def _extract_block(self, text: str, start: str, end: str) -> str | None:
        pattern = rf"{start}(.*?){end}"
        match = re.search(pattern, text, re.S)
        return match.group(1) if match else None

    def _parse_examples(self, text: str) -> List[Dict]:
        examples = []

        pattern = re.compile(
            r"\*\*Example\s*\d+:\*\*(.*?)(?=\*\*Example|\*\*Constraints|\Z)",
            re.S
        )

        for block in pattern.findall(text):
            input_ = self._extract(
                r"Input:\s*(.*?)(?=\s*Output:|\s*Explanation:|\Z)",
                block
            )

            output = self._extract(
                r"Output:\s*(.*?)(?=\s*Explanation:|\Z)",
                block
            )

            explanation = self._extract(
                r"Explanation:\s*(.*)",
                block
            )

            examples.append({
                "input": input_.strip() if input_ else "",
                "output": output.strip() if output else "",
                "explanation": explanation.strip() if explanation else ""
            })

        return examples

    def _extract(self, pattern: str, text: str) -> str | None:
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def filter(self, *, tags=None, difficulty=None) -> List[Dict]:
        results = self.problems

        if tags:
            results = [
                p for p in results
                if any(tag in p["tags"] for tag in tags)
            ]

        if difficulty:
            results = [
                p for p in results
                if p["difficulty"].lower() == difficulty.lower()
            ]

        return results
