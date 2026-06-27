"""
第十二章示例7：数据生成完整评估流程

对应文档：12.4.6 完整评估流程

这个示例展示了数据生成的完整评估流程：
1. 生成AIME题目
2. LLM Judge评估
3. Win Rate评估
4. 人工验证

运行方式：
python 07_data_generation_complete_flow.py 30 3.0

参数说明：
- 30: 生成30道题目
- 3.0: 每道题目之间延迟3秒（避免速率限制）
"""

import sys
import os

# 添加HelloAgents路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "HelloAgents"))

from data_generation.run_complete_evaluation import main

if __name__ == "__main__":
    # 默认参数
    num_problems = 30
    delay_seconds = 3.0
    
    # 从命令行获取参数
    if len(sys.argv) > 1:
        num_problems = int(sys.argv[1])
    if len(sys.argv) > 2:
        delay_seconds = float(sys.argv[2])
    
    print("="*80)
    print("🚀 AIME数据生成与评估完整流程")
    print("="*80)
    print(f"\n配置:")
    print(f"  生成数量: {num_problems}道题目")
    print(f"  延迟设置: {delay_seconds}秒/题")
    print(f"  生成模型: gpt-4o")
    print(f"  评估模型: gpt-4o")
    print()
    
    # 运行完整流程
    main(num_problems, delay_seconds)

# 运行输出示例：
# ================================================================================
# 🚀 AIME数据生成与评估完整流程
# ================================================================================
# 
# 配置:
#   生成数量: 30道题目
#   延迟设置: 3.0秒/题
#   生成模型: gpt-4o
#   评估模型: gpt-4o
# 
# ✅ 已加载 963 道参考题目
# 
# 🎯 开始生成AIME题目
#    目标数量: 30
#    生成模型: gpt-4o
#    延迟设置: 3.0秒/题
# 
# 生成AIME题目: 100%|██████████| 30/30 [02:30<00:00,  5.01s/题]
# 
# ✅ 生成完成
#    成功: 30/30
#    保存位置: ./data_generation/generated_data/aime_problems_20241211_143022.json
# 
# ========== LLM Judge评估 ==========
# 
# 📊 开始LLM Judge评估
#    评估模型: gpt-4o
#    样本数: 30
# 
# LLM Judge评估: 100%|██████████| 30/30 [01:30<00:00,  3.01s/题]
# 
# ✅ LLM Judge评估完成
#    平均分: 3.5/5.0
#    评估维度:
#      - 正确性: 3.8/5.0
#      - 清晰度: 3.6/5.0
#      - 难度匹配: 3.4/5.0
#      - 完整性: 3.2/5.0
# 
# ========== Win Rate评估 ==========
# 
# 📊 开始Win Rate评估
#    评估模型: gpt-4o
#    对比数量: 20
#    参考数据集: AIME 2025 (963道题目)
# 
# Win Rate评估: 100%|██████████| 20/20 [01:00<00:00,  3.01s/对比]
# 
# ✅ Win Rate评估完成
#    Win Rate: 45.0%
#    Tie Rate: 10.0%
#    Loss Rate: 45.0%
# 
# ========== 人工验证 ==========
# 
# 🎯 启动人工验证界面
#    访问地址: http://127.0.0.1:7860
# 
# ✅ 完整评估流程完成！
# 
# 📊 评估总结:
#    生成数量: 30道题目
#    LLM Judge平均分: 3.5/5.0
#    Win Rate: 45.0%
#    建议: 生成质量接近AIME真题水平

