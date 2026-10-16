import os
import json
import shutil
from hello_agents import HelloAgentsLLM, SimpleAgent

from agents.react_agent import NewReActAgent
from agents.agent_prompts import PLAN_AGENT_PROMPT, ANALYSIS_AGENT_PROMPT, REPORT_AGENT_PROMPT
from tools.data_exploration import create_data_exploration_registry
from tools.data_analysis import create_data_analysis_registry


if __name__ == "__main__":
    # 清空 out 目录
    if os.path.exists("out"):
        shutil.rmtree("out")
    os.makedirs("out", exist_ok=True)
    os.makedirs("out/figures", exist_ok=True)

    llm = HelloAgentsLLM()
    registry = create_data_exploration_registry()
    planning_agent = NewReActAgent(
        name="PlanningAgent",
        llm=llm,
        custom_prompt=PLAN_AGENT_PROMPT,
        tool_registry=registry,
        max_steps=5
    )

    question = "请开始分析"
    try:
        plan_result = planning_agent.run(question)
        print(f"任务规划: {plan_result}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")

    # 检查 plan_result 是否符合 python 列表格式
    if not isinstance(plan_result, list):
        print("错误：任务规划结果格式不正确，预期为Python列表。")
        exit(1)

    registry = create_data_analysis_registry()
    analysis_agent = NewReActAgent(
        name="AnalysisAgent",
        llm=llm,
        custom_prompt=ANALYSIS_AGENT_PROMPT,
        tool_registry=registry,
        max_steps=5
    )

    task_result = []

    for task in plan_result:
        print(f"执行任务: {task}")
        try:
            answer = analysis_agent.run(task)
            task_result.append({ "task": task, "result": answer })
            print(f"任务结果: {answer}")
        except Exception as e:
            print(f"执行过程中出现错误: {e}")

    print(f"\n所有任务结果: {task_result}")

    report_agent = SimpleAgent(
        name="ReportAgent",
        system_prompt=REPORT_AGENT_PROMPT,
        llm=llm,
        enable_tool_calling=False
    )

    final_result = report_agent.run(json.dumps(task_result, ensure_ascii=False))

    # 清理报告内容，确保以"# 执行摘要"开头
    if "# 执行摘要" in final_result:
        start_idx = final_result.find("# 执行摘要")
        final_result = final_result[start_idx:]

    print(f"\n最终分析报告: \n{final_result}")

    # 保存报告到文件
    os.makedirs("out", exist_ok=True)
    with open("out/analysis_report.md", "w", encoding="utf-8") as f:
        f.write(final_result)
