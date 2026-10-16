"""
示例2: 奖励函数设计和使用
演示如何使用RLTrainingTool创建和测试奖励函数
"""

import sys
from pathlib import Path
import json

# 添加项目路径
project_root = Path(__file__).parent.parent / "HelloAgents"
sys.path.insert(0, str(project_root))

from hello_agents.tools import RLTrainingTool


# ============================================================================
# 示例1: 创建准确性奖励函数
# ============================================================================

def create_accuracy_reward():
    """
    创建准确性奖励函数
    
    奖励规则:
    - 答案正确: 1.0
    - 答案错误: 0.0
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "create_reward",
        "reward_type": "accuracy"
    }
    
    print("创建准确性奖励函数...")
    result = tool.run(config)
    result_dict = json.loads(result)
    
    print(f"✅ 奖励函数类型: {result_dict['reward_type']}")
    print(f"📋 描述: {result_dict['description']}")
    
    return result_dict


# ============================================================================
# 示例2: 创建长度惩罚奖励函数
# ============================================================================

def create_length_penalty_reward():
    """
    创建长度惩罚奖励函数
    
    奖励规则:
    - 基础奖励 (准确性)
    - 减去长度惩罚 (鼓励简洁)
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "create_reward",
        "reward_type": "length_penalty",
        "penalty_weight": 0.001,  # 每个token惩罚0.001
        "max_length": 512
    }
    
    print("创建长度惩罚奖励函数...")
    result = tool.run(config)
    result_dict = json.loads(result)
    
    print(f"✅ 奖励函数类型: {result_dict['reward_type']}")
    print(f"📋 惩罚权重: {result_dict.get('penalty_weight', 0.001)}")
    print(f"📋 最大长度: {result_dict.get('max_length', 512)}")
    
    return result_dict


# ============================================================================
# 示例3: 创建步骤奖励函数
# ============================================================================

def create_step_reward():
    """
    创建步骤奖励函数
    
    奖励规则:
    - 基础奖励 (准确性)
    - 加上步骤奖励 (鼓励详细推理)
    """
    tool = RLTrainingTool()
    
    config = {
        "action": "create_reward",
        "reward_type": "step",
        "step_bonus": 0.1,  # 每个步骤额外奖励0.1
        "max_steps": 10
    }
    
    print("创建步骤奖励函数...")
    result = tool.run(config)
    result_dict = json.loads(result)
    
    print(f"✅ 奖励函数类型: {result_dict['reward_type']}")
    print(f"📋 步骤奖励: {result_dict.get('step_bonus', 0.1)}")
    print(f"📋 最大步骤: {result_dict.get('max_steps', 10)}")
    
    return result_dict


# ============================================================================
# 示例4: 测试奖励函数
# ============================================================================

def test_reward_function():
    """
    测试奖励函数的计算
    
    使用MathRewardFunction直接测试
    """
    from hello_agents.rl import MathRewardFunction
    
    reward_fn = MathRewardFunction(tolerance=1e-4)
    
    # 测试样本
    test_cases = [
        {
            "completion": "Let me calculate: 2+2=4. Final Answer: 4",
            "ground_truth": "4",
            "expected": 1.0
        },
        {
            "completion": "I think 2+2=5. Final Answer: 5",
            "ground_truth": "4",
            "expected": 0.0
        },
        {
            "completion": "The answer is 4",
            "ground_truth": "4",
            "expected": 1.0
        },
        {
            "completion": "2+2 equals four. #### 4",
            "ground_truth": "4",
            "expected": 1.0
        }
    ]
    
    print("测试奖励函数:")
    print("-" * 80)
    
    for i, case in enumerate(test_cases, 1):
        # 计算奖励
        rewards = reward_fn(
            completions=[case["completion"]],
            ground_truth=[case["ground_truth"]]
        )
        reward = rewards[0]
        
        print(f"\n测试 {i}:")
        print(f"  生成: {case['completion'][:50]}...")
        print(f"  真值: {case['ground_truth']}")
        print(f"  奖励: {reward:.2f} (期望: {case['expected']:.2f})")
        print(f"  {'✅ 正确' if abs(reward - case['expected']) < 0.01 else '❌ 错误'}")
    
    return test_cases


# ============================================================================
# 示例5: 答案提取测试
# ============================================================================

def test_answer_extraction():
    """
    测试答案提取功能
    """
    from hello_agents.rl import MathRewardFunction
    
    reward_fn = MathRewardFunction()
    
    test_texts = [
        "Final Answer: 42",
        "The answer is 3.14",
        "#### 100",
        "So the result is 2.5",
        "Let me think... the answer should be 7",
        "42"
    ]
    
    print("答案提取测试:")
    print("-" * 80)
    
    for text in test_texts:
        answer = reward_fn.extract_answer(text)
        print(f"\n文本: {text}")
        print(f"提取: {answer if answer else '(未找到)'}")
    
    return test_texts


# ============================================================================
# 示例6: 答案比较测试
# ============================================================================

def test_answer_comparison():
    """
    测试答案比较功能
    """
    from hello_agents.rl import MathRewardFunction
    
    reward_fn = MathRewardFunction(tolerance=0.01)
    
    test_pairs = [
        ("42", "42", True),
        ("3.14", "3.14159", False),  # 超出容差
        ("3.14", "3.141", True),     # 在容差内
        ("100", "100.0", True),
        ("2.5", "3.0", False),
        ("7", "7.00", True)
    ]
    
    print("答案比较测试:")
    print("-" * 80)
    
    for pred, truth, expected in test_pairs:
        is_correct = reward_fn.compare_answers(pred, truth)
        print(f"\n预测: {pred}, 真值: {truth}")
        print(f"结果: {'正确' if is_correct else '错误'} (期望: {'正确' if expected else '错误'})")
        print(f"{'✅ 通过' if is_correct == expected else '❌ 失败'}")
    
    return test_pairs


# ============================================================================
# 示例7: 不同奖励函数的对比
# ============================================================================

def compare_reward_functions():
    """
    对比不同奖励函数的效果
    """
    from hello_agents.rl import (
        create_accuracy_reward,
        create_length_penalty_reward,
        create_step_reward
    )

    # 创建不同的奖励函数
    accuracy_fn = create_accuracy_reward()
    base_fn = create_accuracy_reward()  # 基础奖励函数
    length_fn = create_length_penalty_reward(base_fn, penalty_weight=0.001)
    step_fn = create_step_reward(base_fn, step_bonus=0.1)
    
    # 测试样本
    test_cases = [
        {
            "completion": "4",
            "ground_truth": "4",
            "desc": "简洁正确答案"
        },
        {
            "completion": "Step 1: 2+2=4\nFinal Answer: 4",
            "ground_truth": "4",
            "desc": "带步骤的正确答案"
        },
        {
            "completion": "Let me think... " * 20 + "Final Answer: 4",
            "ground_truth": "4",
            "desc": "冗长的正确答案"
        }
    ]
    
    print("奖励函数对比:")
    print("=" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['desc']}")
        print(f"长度: {len(case['completion'])} 字符")
        
        # 计算不同奖励
        acc_reward = accuracy_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]
        len_reward = length_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]
        step_reward = step_fn([case["completion"]], ground_truth=[case["ground_truth"]])[0]
        
        print(f"  准确性奖励: {acc_reward:.4f}")
        print(f"  长度惩罚奖励: {len_reward:.4f}")
        print(f"  步骤奖励: {step_reward:.4f}")
    
    print("\n结论:")
    print("  - 准确性奖励: 只关注答案正确性")
    print("  - 长度惩罚: 鼓励简洁答案")
    print("  - 步骤奖励: 鼓励详细推理")
    
    return test_cases


# ============================================================================
# 主函数
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("示例1: 创建准确性奖励函数")
    print("="*80)
    create_accuracy_reward()
    
    print("\n" + "="*80)
    print("示例2: 创建长度惩罚奖励函数")
    print("="*80)
    create_length_penalty_reward()
    
    print("\n" + "="*80)
    print("示例3: 创建步骤奖励函数")
    print("="*80)
    create_step_reward()
    
    print("\n" + "="*80)
    print("示例4: 测试奖励函数")
    print("="*80)
    test_reward_function()
    
    print("\n" + "="*80)
    print("示例5: 答案提取测试")
    print("="*80)
    test_answer_extraction()
    
    print("\n" + "="*80)
    print("示例6: 答案比较测试")
    print("="*80)
    test_answer_comparison()
    
    print("\n" + "="*80)
    print("示例7: 不同奖励函数的对比")
    print("="*80)
    compare_reward_functions()

