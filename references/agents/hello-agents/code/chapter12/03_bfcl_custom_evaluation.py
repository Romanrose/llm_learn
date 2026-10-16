"""
第十二章示例3：BFCL自定义评估

对应文档：12.2.5 在HelloAgents中实现BFCL评估 - 方式3

这个示例展示如何使用底层组件进行自定义评估流程。
适合需要自定义评估流程的场景。
"""

from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.evaluation import BFCLDataset, BFCLEvaluator

# 1. 创建智能体
llm = HelloAgentsLLM()
agent = SimpleAgent(name="TestAgent", llm=llm)

# 2. 加载数据集
dataset = BFCLDataset(
    bfcl_data_dir="./temp_gorilla/berkeley-function-call-leaderboard/bfcl_eval/data",
    category="simple_python"
)
data = dataset.load()

print(f"✅ 加载了 {len(data)} 个测试样本")

# 3. 创建评估器
evaluator = BFCLEvaluator(
    dataset=dataset,
    category="simple_python"
)

# 4. 运行评估
results = evaluator.evaluate(
    agent=agent,
    max_samples=5  # 只评估5个样本
)

# 5. 查看详细结果
print(f"\n评估结果:")
print(f"总样本数: {results['total_samples']}")
print(f"正确样本数: {results['correct_samples']}")
print(f"准确率: {results['overall_accuracy']:.2%}")

# 6. 查看每个样本的详细结果
print(f"\n详细结果:")
for detail in results['detailed_results']:
    print(f"样本 {detail['sample_id']}:")
    print(f"  问题: {detail['question'][:50]}...")
    print(f"  预测: {detail['predicted']}")
    print(f"  正确答案: {detail['expected']}")
    print(f"  结果: {'✅ 正确' if detail['success'] else '❌ 错误'}")
    print()

# 7. 导出结果
evaluator.export_results(
    results,
    output_file="./evaluation_results/bfcl_custom_result.json"
)

print("✅ 结果已导出到 ./evaluation_results/bfcl_custom_result.json")

