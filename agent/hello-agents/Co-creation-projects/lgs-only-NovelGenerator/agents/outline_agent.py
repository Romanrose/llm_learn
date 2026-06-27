from dotenv import load_dotenv
load_dotenv()
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import NoteTool
from prompt import OUTLINE_PROMPT
import re
import os


def extract_note_id(output: str) -> str:
    """从 NoteTool 的输出文本中提取 note_id"""
    match = re.search(r"ID:\s*(note_[0-9_]+)", output)
    if not match:
        raise ValueError(f"无法从输出解析 note_id:\n{output}")
    return match.group(1)


class OutlineAgent(SimpleAgent):
    """小说大纲生成Agent"""

    def __init__(self, name: str, llm: HelloAgentsLLM = HelloAgentsLLM(), **kwargs):
        self.workspace = kwargs.pop("workspace", "./outputs")
        super().__init__(name=name, llm=llm)
        self.outline_length = 3000
        self.note_tools = {}

    def _ensure_tool(self, novel_id: str, title: str = None):
        if not self.note_tools.get(novel_id):
            if not title:
                raise ValueError(f"Tool for novel_id {novel_id} not initialized and title not provided.")
            self.note_tools[novel_id] = NoteTool(workspace=os.path.join(self.workspace, f"{title}-{novel_id}", 'outline'))

    def run(self, user_input: str, **kwargs) -> str:
        """运行 Agent"""
        # 小说id用来区分小说，命名可能会重复
        novel_id = kwargs.pop("novel_id", None)
        assert novel_id, "请提供小说ID"

        title = kwargs.pop("title", None)
        assert title, "请提供小说标题"

        self._ensure_tool(novel_id, title)

        # 1. 构建上下文
        target_length = kwargs.pop("target_length", self.outline_length)
        context = OUTLINE_PROMPT.format(
            user_input=user_input,
            title=title or "无",
            tags='，'.join([str(tag) for tag in kwargs.values() if tag]) or '无',
            target_length=target_length
        )

        # 2. 使用上下文调用 LLM
        messages = [{"role": "user", "content": context}]
        response = self.llm.invoke(messages)

        # 3. 保存大纲到笔记
        create_output = self.note_tools[novel_id].run({
            "action": "create",
            "title": f"{novel_id}-大纲",
            "content": response,
            "note_type": "outline",
            "tags": ["outline"]
        })
        # 获取笔记ID，建立与小说ID的关联
        note_id = extract_note_id(create_output)

        return response, note_id

    def get_outline(self, novel_id: str, note_id: str, title: str = None) -> str:    
        """获取大纲"""
        if title:
            self._ensure_tool(novel_id, title)
        return self.note_tools[novel_id].run({
            "action": "read",
            "note_id": note_id
        })
    
    def del_outline(self, novel_id: str, note_id: str, title: str = None):
        """删除大纲"""
        if title:
            self._ensure_tool(novel_id, title)
        self.note_tools[novel_id].run({
            "action": "delete",
            "note_id": note_id
        })

    def update_outline(self, novel_id: str, note_id: str, title: str = None, **kwargs):
        """更新大纲"""
        if title:
            self._ensure_tool(novel_id, title)
        self.note_tools[novel_id].run({
            "action": "update",
            "note_id": note_id,
            **kwargs
        })

def main():
    print("=" * 80)
    print("Novel OutlineAgent 示例")
    print("=" * 80 + "\n")

    llm = HelloAgentsLLM()
    novel_id = "demo_novel_001"
    title = "记忆之城"

    agent = OutlineAgent(
        name="小说大纲助手",
        llm=llm,
        workspace="./outputs",
    )

    user_idea = "一位能与城市记忆对话的年轻人，在拆迁浪潮中发现一段被刻意抹去的历史。"

    # 1. 生成大纲
    print(f"\n正在生成大纲...")
    response, note_id = agent.run(
        user_input=user_idea,
        novel_id=novel_id,
        title=title,
        风格标签="都市奇幻",
        情感基调="成长与和解",
    )

    print("生成的大纲（节选）:")
    print(response[:200] + "...\n")
    print(f"大纲已保存到 NoteTool，note_id: {note_id}")

    # 2. 读取大纲
    print(f"\n正在读取大纲 (Note ID: {note_id})...")
    # 注意：get_outline 需要传入 novel_id 和 note_id
    stored_outline = agent.get_outline(novel_id, note_id)
    print("从 NoteTool 中读取的大纲（节选）:")
    # 去掉可能存在的 frontmatter 后的内容预览（这里简单展示原始返回）
    print(stored_outline[:200] + "...")

    # 3. 更新大纲
    print(f"\n正在更新大纲...")
    # 简单模拟：在原有内容后追加一些信息
    # 注意：update_outline 会覆盖 content，所以需要先读取再追加，或者直接传入完整的新内容
    # 这里我们演示读取后追加
    new_content = stored_outline + "\n\n## 补充设定\n主角的能力在雨天会增强，且能听到建筑物的'呼吸声'。"
    agent.update_outline(novel_id, note_id, content=new_content, tags=["outline", "updated"])
    print("大纲已更新。")

    # 4. 再次读取验证更新
    print(f"\n正在验证更新后的内容...")
    updated_outline = agent.get_outline(novel_id, note_id)
    if "主角的能力在雨天会增强" in updated_outline:
        print("验证成功：更新内容已存在。")
    else:
        print("验证失败：未找到更新内容。")

    # 5. 删除大纲（演示，默认注释掉以免误删）
    # print(f"\n正在删除大纲...")
    # agent.del_outline(novel_id, note_id)
    # print("大纲已删除。")


if __name__ == "__main__":
    main()
