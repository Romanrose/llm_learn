"""
示例5: GRPO训练完整流程

演示如何使用RLTrainingTool进行GRPO强化学习训练
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# 示例1: 最简单的GRPO训练
# ============================================================================

def minimal_grpo_training():
    """
    最简单的GRPO训练示例
    
    只需要调用RLTrainingTool即可
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_minimal",
        "max_samples": 10,
        "num_epochs": 1,
    }
    
    print("最简单的GRPO训练:")
    print(f"  模型: {config['model_name']}")
    print(f"  样本数: {config['max_samples']}")
    print(f"  训练轮数: {config['num_epochs']}")
    
    # 实际训练时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ 训练完成! 模型保存在: {result_dict['output_dir']}")
    
    return config


# ============================================================================
# 示例2: 标准GRPO训练配置
# ============================================================================

def standard_grpo_training():
    """
    标准的GRPO训练配置
    
    通常在SFT模型基础上进行GRPO训练
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "train",
        "algorithm": "grpo",
        
        # 模型配置 - 可以使用SFT训练后的模型
        "model_name": "Qwen/Qwen3-0.6B",  # 或 "./output/sft_standard"
        "output_dir": "./output/grpo_standard",
        
        # 数据配置
        "max_samples": 500,  # GRPO通常使用较少样本
        
        # 训练配置
        "num_epochs": 3,
        "batch_size": 2,  # GRPO需要更多显存
        "learning_rate": 1e-5,  # 比SFT小10倍
        
        # LoRA配置
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }
    
    print("标准GRPO训练配置:")
    print(f"  模型: {config['model_name']}")
    print(f"  样本数: {config['max_samples']}")
    print(f"  训练轮数: {config['num_epochs']}")
    print(f"  batch_size: {config['batch_size']}")
    print(f"  learning_rate: {config['learning_rate']} (比SFT小)")
    
    # 实际训练时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ GRPO训练完成!")
    
    return config


# ============================================================================
# 示例3: 完整数据集训练
# ============================================================================

def full_dataset_training():
    """
    使用完整数据集进行GRPO训练
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_full",
        
        # 使用全部数据
        "max_samples": None,  # None = 使用全部数据
        
        "num_epochs": 3,
        "batch_size": 2,
        "learning_rate": 1e-5,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }
    
    print("完整数据集GRPO训练:")
    print(f"  模型: {config['model_name']}")
    print(f"  样本数: 全部 (max_samples=None)")
    print(f"  训练轮数: {config['num_epochs']}")
    print(f"  预计样本数: ~7500 (GSM8K训练集)")
    
    # 实际训练时取消注释
    # result = tool.run(config)
    
    return config


# ============================================================================
# 示例4: SFT + GRPO完整流程
# ============================================================================

def complete_sft_grpo_pipeline():
    """
    完整的SFT + GRPO训练流程
    
    步骤:
    1. SFT训练 - 学习基本格式
    2. GRPO训练 - 优化推理能力
    """
    tool = RLTrainingTool()
    
    # 步骤1: SFT训练
    print("步骤1: SFT训练")
    sft_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/pipeline_sft",
        "max_samples": 1000,
        "num_epochs": 3,
        "batch_size": 4,
        "use_lora": True,
    }
    
    print(f"  模型: {sft_config['model_name']}")
    print(f"  样本数: {sft_config['max_samples']}")
    
    # 实际训练时取消注释
    # sft_result = tool.run(sft_config)
    # print(f"✅ SFT训练完成: {sft_config['output_dir']}")
    
    # 步骤2: GRPO训练
    print("\n步骤2: GRPO训练")
    grpo_config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "./output/pipeline_sft",  # 使用SFT模型
        "output_dir": "./output/pipeline_grpo",
        "max_samples": 500,
        "num_epochs": 3,
        "batch_size": 2,
        "learning_rate": 1e-5,
        "use_lora": True,
    }
    
    print(f"  基础模型: {grpo_config['model_name']}")
    print(f"  样本数: {grpo_config['max_samples']}")
    
    # 实际训练时取消注释
    # grpo_result = tool.run(grpo_config)
    # print(f"✅ GRPO训练完成: {grpo_config['output_dir']}")
    
    print("\n💡 推荐使用GRPO模型进行推理")
    
    return sft_config, grpo_config


# ============================================================================
# 示例5: 不同奖励函数的使用
# ============================================================================

def using_different_rewards():
    """
    GRPO默认使用准确性奖励函数
    
    可以通过创建自定义奖励函数来改变行为
    """
    print("GRPO奖励函数:")
    print("\n默认奖励函数: 准确性奖励")
    print("  - 答案正确: 1.0")
    print("  - 答案错误: 0.0")
    
    print("\n其他可用奖励函数:")
    print("  1. 长度惩罚奖励: 鼓励简洁答案")
    print("  2. 步骤奖励: 鼓励详细推理")
    print("  3. 自定义奖励: 根据需求定制")
    
    print("\n创建奖励函数示例:")
    tool = RLTrainingTool()
    
    # 创建准确性奖励函数
    accuracy_config = {
        "action": "create_reward",
        "reward_type": "accuracy"
    }
    print("\n1. 准确性奖励:")
    print(f"   配置: {accuracy_config}")
    
    # 创建长度惩罚奖励函数
    length_config = {
        "action": "create_reward",
        "reward_type": "length_penalty",
        "penalty_weight": 0.001
    }
    print("\n2. 长度惩罚奖励:")
    print(f"   配置: {length_config}")
    
    # 创建步骤奖励函数
    step_config = {
        "action": "create_reward",
        "reward_type": "step",
        "step_bonus": 0.1
    }
    print("\n3. 步骤奖励:")
    print(f"   配置: {step_config}")
    
    return accuracy_config, length_config, step_config


# ============================================================================
# 示例6: 实际训练示例
# ============================================================================

def practical_training_example():
    """
    实际训练示例 - 可以直接运行
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "train",
        "algorithm": "grpo",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/grpo_practical",
        
        # 使用较少样本进行快速测试
        "max_samples": 50,
        "num_epochs": 1,
        "batch_size": 2,
        "learning_rate": 1e-5,
        
        # 使用LoRA
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    }
    
    print("实际训练示例:")
    print(f"  模型: {config['model_name']}")
    print(f"  样本数: {config['max_samples']}")
    print(f"  训练轮数: {config['num_epochs']}")
    print(f"  输出目录: {config['output_dir']}")
    
    print("\n💡 提示: 取消下面的注释以开始训练")
    print("# result = tool.run(config)")
    print("# result_dict = json.loads(result)")
    print("# print(f'✅ 训练完成! 模型保存在: {result_dict[\"output_dir\"]}')")
    
    # 实际训练时取消注释
    # result = tool.run(config)
    # result_dict = json.loads(result)
    # print(f"\n✅ 训练完成!")
    # print(f"📁 模型保存在: {result_dict['output_dir']}")
    
    return config


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("示例1: 最简单的GRPO训练")
    print("="*80)
    minimal_grpo_training()
    
    print("\n" + "="*80)
    print("示例2: 标准GRPO训练配置")
    print("="*80)
    standard_grpo_training()
    
    print("\n" + "="*80)
    print("示例3: 完整数据集训练")
    print("="*80)
    full_dataset_training()
    
    print("\n" + "="*80)
    print("示例4: SFT + GRPO完整流程")
    print("="*80)
    complete_sft_grpo_pipeline()
    
    print("\n" + "="*80)
    print("示例5: 不同奖励函数的使用")
    print("="*80)
    using_different_rewards()
    
    print("\n" + "="*80)
    print("示例6: 实际训练示例")
    print("="*80)
    practical_training_example()

