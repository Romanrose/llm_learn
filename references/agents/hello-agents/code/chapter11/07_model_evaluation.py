"""
示例7: 模型评估

演示如何使用RLTrainingTool评估训练后的模型
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# 示例1: 评估SFT模型
# ============================================================================

def evaluate_sft_model():
    """
    评估SFT训练后的模型
    
    使用测试集评估模型的准确率
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/sft",
        "max_samples": 50  # 使用50个测试样本
    }
    
    print("评估SFT模型:")
    print(f"  模型路径: {config['model_path']}")
    print(f"  测试样本数: {config['max_samples']}")
    
    # 实际评估时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ 评估完成!")
    # print(f"  准确率: {result_dict['accuracy']}")
    # print(f"  平均奖励: {result_dict['average_reward']}")
    
    print("\n💡 提示: 取消注释以运行评估")
    
    return config


# ============================================================================
# 示例2: 评估GRPO模型
# ============================================================================

def evaluate_grpo_model():
    """
    评估GRPO训练后的模型
    
    对比GRPO模型和SFT模型的性能
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/grpo",
        "max_samples": 50
    }
    
    print("评估GRPO模型:")
    print(f"  模型路径: {config['model_path']}")
    print(f"  测试样本数: {config['max_samples']}")
    
    # 实际评估时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ 评估完成!")
    # print(f"  准确率: {result_dict['accuracy']}")
    # print(f"  平均奖励: {result_dict['average_reward']}")
    
    print("\n💡 提示: 取消注释以运行评估")
    
    return config


# ============================================================================
# 示例3: 对比SFT和GRPO模型
# ============================================================================

def compare_sft_grpo():
    """
    对比SFT和GRPO模型的性能
    
    在相同的测试集上评估两个模型
    """
    tool = RLTrainingTool()
    
    print("="*80)
    print("SFT vs GRPO 模型对比")
    print("="*80)
    
    # 评估SFT模型
    print("\n1. 评估SFT模型...")
    sft_config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/sft",
        "max_samples": 100
    }
    
    # 实际评估时取消注释
    # sft_result = tool.run(sft_config)
    # sft_data = json.loads(sft_result)
    # print(f"   SFT准确率: {sft_data['accuracy']}")
    
    # 评估GRPO模型
    print("\n2. 评估GRPO模型...")
    grpo_config = {
        "action": "evaluate",
        "model_path": "./output/quick_test/grpo",
        "max_samples": 100
    }
    
    # 实际评估时取消注释
    # grpo_result = tool.run(grpo_config)
    # grpo_data = json.loads(grpo_result)
    # print(f"   GRPO准确率: {grpo_data['accuracy']}")
    
    # 对比结果
    print("\n对比结果:")
    print("  SFT模型: 学习基本格式和推理步骤")
    print("  GRPO模型: 通过强化学习优化推理能力")
    print("  预期: GRPO模型准确率 > SFT模型准确率")
    
    print("\n💡 提示: 取消注释以运行实际评估")
    
    return sft_config, grpo_config


# ============================================================================
# 示例4: 评估基线模型
# ============================================================================

def evaluate_baseline():
    """
    评估基线模型(未训练的原始模型)
    
    用于对比训练效果
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "evaluate",
        "model_path": "Qwen/Qwen3-0.6B",  # 原始模型
        "max_samples": 50
    }
    
    print("评估基线模型:")
    print(f"  模型: {config['model_path']}")
    print(f"  测试样本数: {config['max_samples']}")
    
    # 实际评估时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ 评估完成!")
    # print(f"  基线准确率: {result_dict['accuracy']}")
    
    print("\n💡 提示: 基线模型通常准确率较低")
    print("   训练后的模型应该显著优于基线")
    
    return config


# ============================================================================
# 示例5: 完整评估流程
# ============================================================================

def complete_evaluation():
    """
    完整的评估流程
    
    评估基线、SFT和GRPO三个模型
    """
    tool = RLTrainingTool()
    
    models = {
        "基线模型": "Qwen/Qwen3-0.6B",
        "SFT模型": "./output/quick_test/sft",
        "GRPO模型": "./output/quick_test/grpo"
    }
    
    print("="*80)
    print("完整评估流程")
    print("="*80)
    
    results = {}
    
    for name, model_path in models.items():
        print(f"\n评估 {name}...")
        print(f"  路径: {model_path}")
        
        config = {
            "action": "evaluate",
            "model_path": model_path,
            "max_samples": 100
        }
        
        # 实际评估时取消注释
        # result = tool.run(config)
        # result_dict = json.loads(result)
        # results[name] = result_dict
        # print(f"  准确率: {result_dict['accuracy']}")
    
    print("\n" + "="*80)
    print("评估总结")
    print("="*80)
    
    # 实际评估时取消注释
    # for name, result in results.items():
    #     print(f"{name}: {result['accuracy']}")
    
    print("\n预期结果:")
    print("  基线模型 < SFT模型 < GRPO模型")
    print("  说明强化学习训练有效提升了模型性能")
    
    print("\n💡 提示: 取消注释以运行完整评估")
    
    return models


# ============================================================================
# 示例6: 实际评估示例
# ============================================================================

def practical_evaluation():
    """
    实际评估示例 - 可以直接运行
    
    评估quick_test训练的模型
    """
    tool = RLTrainingTool()
    
    print("="*80)
    print("实际评估示例")
    print("="*80)
    
    # 检查模型是否存在
    import os
    sft_path = "./output/quick_test/sft"
    grpo_path = "./output/quick_test/grpo"
    
    if not os.path.exists(sft_path):
        print(f"\n❌ SFT模型不存在: {sft_path}")
        print("   请先运行 00_quick_test.py 训练模型")
        return None
    
    if not os.path.exists(grpo_path):
        print(f"\n❌ GRPO模型不存在: {grpo_path}")
        print("   请先运行 00_quick_test.py 训练模型")
        return None
    
    print("\n✅ 模型文件存在,开始评估...")
    
    # 评估SFT模型
    print("\n1. 评估SFT模型...")
    sft_config = {
        "action": "evaluate",
        "model_path": sft_path,
        "max_samples": 20  # 使用较少样本快速测试
    }
    
    print("💡 提示: 取消下面的注释以开始评估")
    print("# sft_result = tool.run(sft_config)")
    print("# sft_data = json.loads(sft_result)")
    print("# print(f'SFT准确率: {sft_data[\"accuracy\"]}')")
    
    # 评估GRPO模型
    print("\n2. 评估GRPO模型...")
    grpo_config = {
        "action": "evaluate",
        "model_path": grpo_path,
        "max_samples": 20
    }
    
    print("💡 提示: 取消下面的注释以开始评估")
    print("# grpo_result = tool.run(grpo_config)")
    print("# grpo_data = json.loads(grpo_result)")
    print("# print(f'GRPO准确率: {grpo_data[\"accuracy\"]}')")
    
    # 实际评估时取消注释
    # sft_result = tool.run(sft_config)
    # sft_data = json.loads(sft_result)
    # print(f"\n✅ SFT评估完成: {sft_data['accuracy']}")
    
    # grpo_result = tool.run(grpo_config)
    # grpo_data = json.loads(grpo_result)
    # print(f"✅ GRPO评估完成: {grpo_data['accuracy']}")
    
    return sft_config, grpo_config


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("示例1: 评估SFT模型")
    print("="*80)
    evaluate_sft_model()
    
    print("\n" + "="*80)
    print("示例2: 评估GRPO模型")
    print("="*80)
    evaluate_grpo_model()
    
    print("\n" + "="*80)
    print("示例3: 对比SFT和GRPO模型")
    print("="*80)
    compare_sft_grpo()
    
    print("\n" + "="*80)
    print("示例4: 评估基线模型")
    print("="*80)
    evaluate_baseline()
    
    print("\n" + "="*80)
    print("示例5: 完整评估流程")
    print("="*80)
    complete_evaluation()
    
    print("\n" + "="*80)
    print("示例6: 实际评估示例")
    print("="*80)
    practical_evaluation()

