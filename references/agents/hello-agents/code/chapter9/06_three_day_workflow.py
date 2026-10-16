"""
CodebaseMaintainer 三天工作流演示

完整展示长程智能体在三天内的工作流程:
- 第一天: 探索代码库（Agent 自主探索）
- 第二天: 分析代码质量（Agent 自主分析）
- 第三天: 规划重构任务（Agent 自主规划）
- 一周后: 检查进度

"""

import os
# 配置嵌入模型（三选一）
# 方案一：TF-IDF（最简单，无需额外依赖）
os.environ['EMBED_MODEL_TYPE'] = 'tfidf'
os.environ['EMBED_MODEL_NAME'] = ''  # 重要：必须清空，否则会传递不兼容的参数
from dotenv import load_dotenv
load_dotenv()
# 方案二：本地Transformer（需要: pip install sentence-transformers 和 HF token）
# os.environ['EMBED_MODEL_TYPE'] = 'local'
# os.environ['EMBED_MODEL_NAME'] = 'sentence-transformers/all-MiniLM-L6-v2'
# os.environ['HF_TOKEN'] = 'your_hf_token_here'  # 或使用 huggingface-cli login
# 方案三：通义千问（需要API key）
# os.environ['EMBED_MODEL_TYPE'] = 'dashscope'
# os.environ['EMBED_MODEL_NAME'] = 'text-embedding-v3'
# os.environ['EMBED_API_KEY'] = 'your_api_key_here'

from hello_agents import HelloAgentsLLM
from datetime import datetime
import json
import time

# 导入 CodebaseMaintainer
import sys
sys.path.append('.')
from codebase_maintainer import CodebaseMaintainer


def day_1_exploration(maintainer):
    """第一天: 探索代码库（Agentic 方式）
    
    在这个阶段，我们只给 Agent 高层次的目标，
    Agent 会自主决定：
    - 使用哪些 shell 命令探索代码库
    - 查看哪些文件
    - 是否记录笔记
    """
    print("\n" + "=" * 80)
    print("第一天: 探索代码库（Agent 自主探索）")
    print("=" * 80 + "\n")

    # 1. 初步探索 - Agent 自主决定如何探索
    print("### 1. 初步探索项目结构 ###")
    print("💡 提示：Agent 会自主决定使用哪些命令（如 find, ls, cat）\n")
    response = maintainer.explore()
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 2. 深入分析某个模块 - Agent 自主决定分析方法
    print("### 2. 分析数据处理模块 ###")
    print("💡 提示：Agent 会自主决定如何分析这个文件\n")
    response = maintainer.run("请查看 data_processor.py 文件，分析其代码设计")
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 模拟时间流逝
    time.sleep(1)


def day_2_analysis(maintainer):
    """第二天: 分析代码质量（Agentic 方式）
    
    Agent 会自主决定：
    - 使用什么方法分析代码质量（grep TODO? 统计行数? 检查复杂度?）
    - 是否需要创建笔记记录问题
    - 如何组织分析结果
    """
    print("\n" + "=" * 80)
    print("第二天: 分析代码质量（Agent 自主分析）")
    print("=" * 80 + "\n")

    # 1. 整体质量分析 - Agent 自主决定分析方法
    print("### 1. 分析代码质量 ###")
    print("💡 提示：Agent 会自主决定如何分析（如 grep TODO, wc -l, 复杂度分析）\n")
    response = maintainer.analyze()
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 2. 查看具体问题 - Agent 自主深入分析
    print("### 2. 分析 API 客户端代码 ###")
    print("💡 提示：Agent 会自主决定如何分析这个文件的质量\n")
    response = maintainer.run(
        "请分析 api_client.py 的代码质量，特别是错误处理部分，给出改进建议"
    )
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 模拟时间流逝
    time.sleep(1)


def day_3_planning(maintainer):
    """第三天: 规划重构任务（Agentic 方式）
    
    Agent 会自主决定：
    - 回顾哪些历史笔记
    - 如何组织任务规划
    - 是否需要创建新的笔记
    - 如何安排优先级
    """
    print("\n" + "=" * 80)
    print("第三天: 规划重构任务（Agent 自主规划）")
    print("=" * 80 + "\n")

    # 1. 回顾进度 - Agent 自主查看历史笔记并规划
    print("### 1. 回顾当前进度并规划下一步 ###")
    print("💡 提示：Agent 会自主查看历史笔记，分析当前进度，并制定计划\n")
    response = maintainer.plan_next_steps()
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 2. 询问 Agent 创建详细计划（Agent 会自主决定是否使用 NoteTool）
    print("### 2. 让 Agent 创建详细的重构计划 ###")
    print("💡 提示：Agent 会自主决定如何创建和组织重构计划\n")
    response = maintainer.run(
        "请基于我们的分析，创建一个详细的本周重构计划。"
        "计划应该包括：目标、具体任务清单、时间安排和风险。"
        "请使用 NoteTool 创建一个 task_state 类型的笔记来记录这个计划。"
    )
    print(f"\n助手总结:\n{response[:500]}...\n")

    # 模拟时间流逝
    time.sleep(1)


def week_later_review(maintainer):
    """一周后: 检查进度"""
    print("\n" + "=" * 80)
    print("一周后: 检查进度")
    print("=" * 80 + "\n")

    # 1. 查看笔记摘要
    print("### 1. 笔记摘要 ###")
    summary = maintainer.note_tool.run({"action": "summary"})
    print("📊 笔记摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print()

    # 2. 生成完整报告
    print("### 2. 会话报告 ###")
    report = maintainer.generate_report()
    print("\n📄 会话报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def demonstrate_cross_session_continuity():
    """演示跨会话的连贯性"""
    print("\n" + "=" * 80)
    print("演示跨会话的连贯性")
    print("=" * 80 + "\n")

    # 第一次会话
    print("### 第一次会话 (session_1) ###")
    maintainer_1 = CodebaseMaintainer(
        project_name="demo_codebase",
        #实际使用的时候替换代码路径
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # 创建一些笔记
    maintainer_1.create_note(
        title="代码质量问题",
        content="发现多处 TODO 注释需要实现，特别是数据验证和错误处理部分",
        note_type="blocker",
        tags=["quality", "urgent"]
    )

    stats_1 = maintainer_1.get_stats()
    print(f"会话1统计: {stats_1['activity']}\n")

    # 模拟会话结束
    time.sleep(1)

    # 第二次会话 (新的会话ID,但笔记被保留)
    print("### 第二次会话 (session_2) ###")
    maintainer_2 = CodebaseMaintainer(
        project_name="demo_codebase",  # 同一个项目
        #实际使用的时候替换代码路径
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # 检索之前的笔记
    response = maintainer_2.run(
        "我们之前发现了什么代码质量问题？现在应该优先处理哪些？"
    )
    print(f"\n助手回答:\n{response[:300]}...\n")

    stats_2 = maintainer_2.get_stats()
    print(f"会话2统计: {stats_2['activity']}\n")

    # 展示笔记摘要
    summary = maintainer_2.note_tool.run({"action": "summary"})
    print("📊 跨会话笔记摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def demonstrate_tool_synergy():
    """演示三大工具的协同（Agentic 方式）
    
    在这个演示中：
    - 我们不再手动调用工具
    - 而是让 Agent 自主决定使用哪些工具
    - Agent 会根据任务自动协同使用多个工具
    """
    print("\n" + "=" * 80)
    print("演示三大工具的协同（Agent 自主协调）")
    print("=" * 80 + "\n")

    maintainer = CodebaseMaintainer(
        project_name="synergy_demo",
        #实际使用的时候替换代码路径
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # Agent 自主分析并记录
    print("### Agent 自主分析代码库中的 TODO 项 ###")
    print("💡 提示：Agent 会自主决定：\n")
    print("   1. 使用 TerminalTool 查找 TODO")
    print("   2. 使用 NoteTool 记录发现")
    print("   3. 使用 MemoryTool 记住关键信息\n")
    
    response = maintainer.run(
        "请分析代码库中的所有 TODO 项，并将发现记录到笔记中。"
        "然后告诉我应该优先实现哪些功能。"
    )
    print(f"助手回答:\n{response[:500]}...\n")

    # 展示统计信息
    stats = maintainer.get_stats()
    print("📊 工具使用统计:")
    print(f"  - 工具调用次数: {stats['activity']['tool_calls']}")
    print(f"  - 执行的命令: {stats['activity']['commands_executed']}")
    print(f"  - 创建的笔记: {stats['activity']['notes_created']}")


def main():
    """主函数"""
    print("=" * 80)
    print("CodebaseMaintainer 三天工作流演示（Agentic 版本）")
    print("=" * 80)
    
    print("\n✨ 核心特性：Agent 自主决策")
    print("💡 使用我们在 chapter9 创建的示例代码库")
    print("📁 代码库路径: ./codebase")
    print("📦 包含文件: data_processor.py, api_client.py, utils.py, models.py")
    print("\n🔧 Agent 可用工具：")
    print("   - TerminalTool: 执行 shell 命令")
    print("   - NoteTool: 创建和管理笔记")
    print("   - MemoryTool: 记忆管理")
    print("\n⚡ Agent 会自主决定：")
    print("   - 使用哪些工具")
    print("   - 执行什么命令")
    print("   - 如何组织信息\n")

    # 初始化助手
    maintainer = CodebaseMaintainer(
        project_name="demo_codebase",
        #实际使用的时候替换代码路径
        codebase_path="/Users/suntao/Documents/GitHub/hello-agents/code/chapter9/codebase",
        llm=HelloAgentsLLM()
    )

    # 执行三天工作流
    day_1_exploration(maintainer)
    day_2_analysis(maintainer)
    day_3_planning(maintainer)
    week_later_review(maintainer)

    # 额外演示
    print("\n\n" + "=" * 80)
    print("额外演示")
    print("=" * 80)

    demonstrate_cross_session_continuity()
    demonstrate_tool_synergy()

    print("\n" + "=" * 80)
    print("完整演示结束!")
    print("=" * 80)


if __name__ == "__main__":
    main()
