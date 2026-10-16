from hello_agents.tools.builtin.note_tool import NoteTool

class LearningNotesService:
    def __init__(self, workspace: str):
        self.note_tool = NoteTool(workspace=workspace)

    def save_learning_progress(
        self,
        user_id: str,
        progress: "LearningProgress"
    ):
        """保存学习路径与进度"""
        content = self._format_learning_content(progress)

        self.note_tool.run({
            "action": "create",
            "title": f"学习进度｜{progress.topic}",
            "content": content,
            "tags": [
                "learning",
                "progress",
                progress.level,
                user_id
            ]
        })

    def _format_learning_content(self, progress: "LearningProgress") -> str:
        content = f"# 学习主题：{progress.topic}\n\n"
        content += f"**当前水平**：{progress.level}\n\n"

        # 学习路径
        content += "## 学习路径\n\n"
        for idx, step in enumerate(progress.steps, start=1):
            status_icon = {
                "completed": "✅",
                "in_progress": "⏳",
                "not_started": "⬜"
            }.get(step.status, "⬜")

            content += f"{idx}. {status_icon} **{step.title}**\n"
            if step.notes:
                content += f"   - 备注：{step.notes}\n"
        content += "\n"

        # 掌握点
        if progress.mastered_points:
            content += "## 已掌握知识点\n\n"
            for p in progress.mastered_points:
                content += f"- ✅ {p}\n"
            content += "\n"

        # 薄弱点
        if progress.weak_points:
            content += "## 薄弱点\n\n"
            for p in progress.weak_points:
                content += f"- ⚠️ {p}\n"
            content += "\n"

        # 下一步建议
        content += "## 下一步学习建议\n\n"
        content += f"{progress.next_suggestion}\n"

        return content
