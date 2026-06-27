"""
第十二章示例6：GAIA评估最佳实践

对应文档：12.3.9 GAIA评估最佳实践

这个示例展示了GAIA评估的最佳实践，包括：
1. 分级评估
2. 小样本快速测试
3. 结果解读
"""

import os
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import GAIAEvaluationTool

# GAIA官方系统提示词
GAIA_SYSTEM_PROMPT = """You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings.
If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise.
If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."""

# 创建智能体
llm = HelloAgentsLLM()
agent = SimpleAgent(
    name="TestAgent",
    llm=llm,
    system_prompt=GAIA_SYSTEM_PROMPT
)

# 创建评估工具
gaia_tool = GAIAEvaluationTool()

# ============================================================
# 最佳实践1：分级评估
# ============================================================
print("="*60)
print("最佳实践1：分级评估")
print("="*60)

# 第一步：评估Level 1（简单任务）
print("\n第一步：评估Level 1（简单任务）")
results_l1 = gaia_tool.run(agent, level=1, max_samples=10)
print(f"Level 1精确匹配率: {results_l1['exact_match_rate']:.2%}")

# 第二步：如果Level 1表现良好，评估Level 2
if results_l1['exact_match_rate'] > 0.6:
    print("\n第二步：评估Level 2（中等任务）")
    results_l2 = gaia_tool.run(agent, level=2, max_samples=10)
    print(f"Level 2精确匹配率: {results_l2['exact_match_rate']:.2%}")
    
    # 第三步：如果Level 2表现良好，评估Level 3
    if results_l2['exact_match_rate'] > 0.4:
        print("\n第三步：评估Level 3（困难任务）")
        results_l3 = gaia_tool.run(agent, level=3, max_samples=10)
        print(f"Level 3精确匹配率: {results_l3['exact_match_rate']:.2%}")
    else:
        print("\n⚠️ Level 2表现不佳，建议先优化后再评估Level 3")
else:
    print("\n⚠️ Level 1表现不佳，建议先优化后再评估更高级别")

# ============================================================
# 最佳实践2：小样本快速测试
# ============================================================
print("\n" + "="*60)
print("最佳实践2：小样本快速测试")
print("="*60)

# 快速测试（每个级别2个样本）
for level in [1, 2, 3]:
    print(f"\n快速测试 Level {level}:")
    results = gaia_tool.run(agent, level=level, max_samples=2)
    print(f"  精确匹配率: {results['exact_match_rate']:.2%}")

# ============================================================
# 最佳实践3：结果解读
# ============================================================
print("\n" + "="*60)
print("最佳实践3：结果解读")
print("="*60)

def interpret_results(level, exact_match_rate):
    """解读评估结果"""
    print(f"\nLevel {level} 结果解读:")
    print(f"精确匹配率: {exact_match_rate:.2%}")
    
    if level == 1:
        if exact_match_rate >= 0.6:
            print("✅ 优秀 - 基础能力扎实")
        elif exact_match_rate >= 0.4:
            print("⚠️ 良好 - 基础能力可用")
        else:
            print("❌ 较差 - 需要改进")
            print("建议:")
            print("  - 检查系统提示词是否包含GAIA官方格式要求")
            print("  - 检查答案提取逻辑是否正确")
            print("  - 检查LLM模型是否足够强大")
    
    elif level == 2:
        if exact_match_rate >= 0.4:
            print("✅ 优秀 - 中等任务能力强")
        elif exact_match_rate >= 0.2:
            print("⚠️ 良好 - 中等任务能力可用")
        else:
            print("❌ 较差 - 需要改进")
            print("建议:")
            print("  - 增强多步推理能力")
            print("  - 增加工具使用能力")
            print("  - 优化推理链的构建")
    
    elif level == 3:
        if exact_match_rate >= 0.2:
            print("✅ 优秀 - 复杂任务能力强")
        elif exact_match_rate >= 0.1:
            print("⚠️ 良好 - 复杂任务能力可用")
        else:
            print("❌ 较差 - 需要改进")
            print("建议:")
            print("  - 增强复杂推理能力")
            print("  - 增加长上下文处理能力")
            print("  - 优化工具链的组合使用")

# 解读结果
if 'results_l1' in locals():
    interpret_results(1, results_l1['exact_match_rate'])
if 'results_l2' in locals():
    interpret_results(2, results_l2['exact_match_rate'])
if 'results_l3' in locals():
    interpret_results(3, results_l3['exact_match_rate'])

# ============================================================
# 难度递进分析
# ============================================================
print("\n" + "="*60)
print("难度递进分析")
print("="*60)

if 'results_l1' in locals() and 'results_l2' in locals():
    if results_l1['exact_match_rate'] > results_l2['exact_match_rate']:
        print("✅ 正常递进：Level 1 > Level 2")
    else:
        print("⚠️ 异常情况：Level 2 >= Level 1（可能是数据集偏差或智能体特性）")

if 'results_l2' in locals() and 'results_l3' in locals():
    if results_l2['exact_match_rate'] > results_l3['exact_match_rate']:
        print("✅ 正常递进：Level 2 > Level 3")
    else:
        print("⚠️ 异常情况：Level 3 >= Level 2（可能是数据集偏差或智能体特性）")

