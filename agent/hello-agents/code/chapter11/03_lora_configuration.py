"""
示例3: LoRA配置和使用
演示如何通过RLTrainingTool配置和使用LoRA进行参数高效微调
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# 示例1: 基础LoRA配置
# ============================================================================

def basic_lora_config():
    """
    最基础的LoRA配置
    
    LoRA (Low-Rank Adaptation):
    - 只训练少量额外参数
    - 减少60-80%显存占用
    - 提升2-3倍训练速度
    - 模型文件只有~10MB
    """
    tool = RLTrainingTool()
    
    # 使用RLTrainingTool进行SFT训练,启用LoRA
    config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/lora_basic",
        "max_samples": 100,
        "num_epochs": 1,
        
        # LoRA配置
        "use_lora": True,           # 启用LoRA
        "lora_r": 16,               # LoRA秩(rank)
        "lora_alpha": 32,           # 缩放因子(通常是r的2倍)
    }
    
    print("基础LoRA配置:")
    print(f"  模型: {config['model_name']}")
    print(f"  use_lora: {config['use_lora']}")
    print(f"  lora_r: {config['lora_r']}")
    print(f"  lora_alpha: {config['lora_alpha']}")
    print(f"  目标模块: ['q_proj', 'v_proj'] (默认)")
    
    # 实际训练时取消注释
    # result = tool.run(config)
    # print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    
    return config


# ============================================================================
# 示例2: 不同LoRA秩的对比
# ============================================================================

def compare_lora_ranks():
    """
    对比不同LoRA秩的配置
    
    LoRA秩(r)的选择:
    - r=8: 较小参数量,适合快速实验
    - r=16: 推荐值,平衡性能和效率
    - r=32: 较大参数量,追求更好性能
    """
    configs = {
        "r=8 (快速实验)": {
            "lora_r": 8,
            "lora_alpha": 16,
            "params": "~16K"
        },
        "r=16 (推荐)": {
            "lora_r": 16,
            "lora_alpha": 32,
            "params": "~32K"
        },
        "r=32 (高性能)": {
            "lora_r": 32,
            "lora_alpha": 64,
            "params": "~65K"
        },
    }
    
    print("不同LoRA秩的对比:")
    for name, config in configs.items():
        print(f"\n{name}:")
        print(f"  lora_r: {config['lora_r']}")
        print(f"  lora_alpha: {config['lora_alpha']}")
        print(f"  预估参数量: {config['params']}")
    
    # 实际训练示例
    print("\n训练示例 (r=16):")
    print("""
    tool = RLTrainingTool()
    result = tool.run({
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "max_samples": 100,
        "num_epochs": 1,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
    })
    """)
    
    return configs


# ============================================================================
# 示例3: LoRA vs 完整微调对比
# ============================================================================

def compare_lora_vs_full_finetuning():
    """
    对比LoRA和完整微调的配置
    """
    print("LoRA vs 完整微调对比:")
    print("\nLoRA微调:")
    print("  显存占用: ~4GB (0.5B模型)")
    print("  训练速度: 快(2-3x)")
    print("  模型大小: ~10MB")
    print("  batch_size: 8")
    print("  use_lora: True")
    
    print("\n完整微调:")
    print("  显存占用: ~14GB (0.5B模型)")
    print("  训练速度: 慢")
    print("  模型大小: ~1GB")
    print("  batch_size: 2")
    print("  use_lora: False")
    
    print("\n推荐: 使用LoRA进行微调")


# ============================================================================
# 示例4: 实际训练配置示例
# ============================================================================

def practical_training_configs():
    """
    实际训练中的推荐配置
    """
    tool = RLTrainingTool()
    
    # 快速训练配置
    quick_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/quick_test",
        "max_samples": 100,
        "num_epochs": 1,
        "batch_size": 8,
        "use_lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
    }
    
    # 标准训练配置
    standard_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/standard",
        "max_samples": 1000,
        "num_epochs": 3,
        "batch_size": 4,
        "use_lora": True,
        "lora_r": 16,
        "lora_alpha": 32,
        "learning_rate": 5e-5,
    }
    
    # 高质量训练配置
    high_quality_config = {
        "action": "train",
        "algorithm": "sft",
        "model_name": "Qwen/Qwen3-0.6B",
        "output_dir": "./output/high_quality",
        "max_samples": None,  # 使用全部数据
        "num_epochs": 5,
        "batch_size": 2,
        "use_lora": True,
        "lora_r": 32,
        "lora_alpha": 64,
        "learning_rate": 3e-5,
    }
    
    print("实际训练配置示例:")
    print("\n1. 快速实验配置:")
    print(f"   样本数: {quick_config['max_samples']}")
    print(f"   epochs: {quick_config['num_epochs']}")
    print(f"   lora_r: {quick_config['lora_r']}")
    print(f"   batch_size: {quick_config['batch_size']}")
    
    print("\n2. 标准训练配置:")
    print(f"   样本数: {standard_config['max_samples']}")
    print(f"   epochs: {standard_config['num_epochs']}")
    print(f"   lora_r: {standard_config['lora_r']}")
    print(f"   batch_size: {standard_config['batch_size']}")
    
    print("\n3. 高质量训练配置:")
    print(f"   样本数: 全部 (max_samples=None)")
    print(f"   epochs: {high_quality_config['num_epochs']}")
    print(f"   lora_r: {high_quality_config['lora_r']}")
    print(f"   batch_size: {high_quality_config['batch_size']}")
    
    # 实际训练时取消注释
    # result = tool.run(quick_config)
    # print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    
    return quick_config, standard_config, high_quality_config


# ============================================================================
# 示例5: LoRA参数调优建议
# ============================================================================

def lora_tuning_guidelines():
    """
    LoRA参数调优建议
    """
    guidelines = {
        "lora_r (秩)": {
            "推荐值": 16,
            "范围": "8-32",
            "说明": "越大性能越好,但参数量和训练时间也越多",
            "选择建议": {
                "快速实验": 8,
                "平衡性能": 16,
                "追求性能": 32,
            }
        },
        "lora_alpha (缩放因子)": {
            "推荐值": 32,
            "范围": "16-64",
            "说明": "通常设置为lora_r的2倍",
            "公式": "lora_alpha = 2 * lora_r"
        },
        "max_samples (样本数)": {
            "快速实验": 100,
            "标准训练": 1000,
            "完整训练": "None (全部数据)",
            "说明": "None表示使用全部数据",
        },
    }
    
    print("LoRA参数调优建议:")
    for param, info in guidelines.items():
        print(f"\n{param}:")
        for key, value in info.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  {key}: {value}")
    
    return guidelines


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("示例1: 基础LoRA配置")
    print("="*80)
    basic_lora_config()
    
    print("\n" + "="*80)
    print("示例2: 不同LoRA秩的对比")
    print("="*80)
    compare_lora_ranks()
    
    print("\n" + "="*80)
    print("示例3: LoRA vs 完整微调对比")
    print("="*80)
    compare_lora_vs_full_finetuning()
    
    print("\n" + "="*80)
    print("示例4: 实际训练配置示例")
    print("="*80)
    practical_training_configs()
    
    print("\n" + "="*80)
    print("示例5: LoRA参数调优建议")
    print("="*80)
    lora_tuning_guidelines()

