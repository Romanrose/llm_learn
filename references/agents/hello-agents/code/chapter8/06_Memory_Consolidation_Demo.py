#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码示例 06: 记忆整合机制演示
展示从短期记忆到长期记忆的智能转化过程
"""

from dotenv import load_dotenv
load_dotenv()
import time
from datetime import datetime, timedelta
from hello_agents.tools import MemoryTool


class MemoryConsolidationDemo:
    """记忆整合演示类"""
    
    def __init__(self):
        self.memory_tool = MemoryTool(
            user_id="consolidation_demo_user",
            memory_types=["working", "episodic", "semantic", "perceptual"]
        )
    
    def setup_initial_memories(self):
        """设置初始记忆数据"""
        print("📝 设置初始记忆数据")
        print("=" * 50)
        
        # 添加不同重要性的工作记忆
        working_memories = [
            {
                "content": "学习了Transformer架构的基本原理",
                "importance": 0.9,
                "topic": "deep_learning",
                "session": "study_session_1"
            },
            {
                "content": "完成了Python代码调试任务",
                "importance": 0.8,
                "topic": "programming",
                "task_type": "debugging"
            },
            {
                "content": "参加了团队会议讨论项目进展",
                "importance": 0.7,
                "topic": "teamwork",
                "meeting_type": "progress_review"
            },
            {
                "content": "查看了今天的天气预报",
                "importance": 0.3,
                "topic": "daily_life",
                "category": "routine"
            },
            {
                "content": "阅读了关于注意力机制的论文",
                "importance": 0.85,
                "topic": "research",
                "paper_type": "technical"
            },
            {
                "content": "喝了一杯咖啡",
                "importance": 0.2,
                "topic": "daily_life",
                "category": "routine"
            },
            {
                "content": "解决了一个复杂的算法问题",
                "importance": 0.9,
                "topic": "problem_solving",
                "difficulty": "high"
            },
            {
                "content": "整理了桌面文件",
                "importance": 0.4,
                "topic": "organization",
                "category": "maintenance"
            }
        ]
        
        print("添加工作记忆:")
        for i, memory in enumerate(working_memories):
            content = memory.pop("content")
            importance = memory.pop("importance")
            
            result = self.memory_tool.run({"action":"add",
                                            "content":content,
                                            "memory_type":"working",
                                            "importance":importance,
                                            **memory})
            
            print(f"  {i+1}. {content[:40]}... (重要性: {importance})")
        
        print(f"\n✅ 已添加 {len(working_memories)} 条工作记忆")
        
        # 显示当前状态
        stats = self.memory_tool.run({"action":"stats"})
        print(f"\n📊 当前记忆统计:\n{stats}")
    
    def demonstrate_consolidation_criteria(self):
        """演示整合标准和筛选过程"""
        print("\n🎯 记忆整合标准演示")
        print("-" * 50)
        
        print("整合标准:")
        print("• 重要性阈值筛选")
        print("• 按重要性排序")
        print("• 类型转换处理")
        print("• 元数据更新")
        
        # 获取当前工作记忆摘要
        print("\n📋 整合前的工作记忆状态:")
        summary = self.memory_tool.run({"action":"summary", "limit":10})
        print(summary)
        
        # 测试不同阈值的整合效果
        thresholds = [0.5, 0.7, 0.8]
        
        for threshold in thresholds:
            print(f"\n🔍 测试重要性阈值 {threshold}:")
            
            # 模拟整合过程（不实际执行，只是分析）
            working_memories = []
            # 这里应该从实际的工作记忆中获取，简化演示
            
            print(f"  阈值 {threshold} 下符合整合条件的记忆:")
            print(f"  • 重要性 >= {threshold} 的记忆将被整合")
            print(f"  • 整合后类型: working → episodic")
            print(f"  • 重要性提升: importance × 1.1")
    
    def demonstrate_consolidation_process(self):
        """演示实际的整合过程"""
        print("\n🔄 记忆整合过程演示")
        print("-" * 50)
        
        print("整合过程步骤:")
        print("1. 筛选符合条件的记忆")
        print("2. 按重要性排序")
        print("3. 创建新的记忆项")
        print("4. 更新类型和元数据")
        print("5. 添加整合标记")
        
        # 执行不同阈值的整合
        consolidation_tests = [
            (0.6, "低阈值整合 - 整合更多记忆"),
            (0.8, "高阈值整合 - 只整合最重要的记忆")
        ]
        
        for threshold, description in consolidation_tests:
            print(f"\n🔄 {description} (阈值: {threshold}):")
            
            # 获取整合前状态
            stats_before = self.memory_tool.run({"action":"stats"})
            print(f"整合前状态: {stats_before}")
            
            # 执行整合
            start_time = time.time()
            consolidation_result = self.memory_tool.run({"action":"consolidate",
                                                          "from_type":"working",
                                                          "to_type":"episodic",
                                                          "importance_threshold":threshold})
            consolidation_time = time.time() - start_time
            
            print(f"整合结果: {consolidation_result}")
            print(f"整合耗时: {consolidation_time:.3f}秒")
            
            # 获取整合后状态
            stats_after = self.memory_tool.run({"action":"stats"})
            print(f"整合后状态: {stats_after}")
            
            # 查看整合后的情景记忆
            print(f"\n📚 整合后的情景记忆:")
            episodic_search = self.memory_tool.run({"action":"search",
                                                     "query":"",
                                                     "memory_type":"episodic",
                                                     "limit":5})
            print(episodic_search)
    
    def demonstrate_consolidation_metadata(self):
        """演示整合过程中的元数据处理"""
        print("\n📋 整合元数据处理演示")
        print("-" * 50)
        
        print("元数据处理:")
        print("• 保留原始元数据")
        print("• 添加整合标记")
        print("• 记录整合时间")
        print("• 保存原始ID引用")
        
        # 添加一个特殊的工作记忆用于演示
        special_memory_result = self.memory_tool.run({"action":"add",
            "content":"这是一个用于演示整合元数据处理的特殊记忆",
            "memory_type":"working",
            "importance":0.85,
            "special_tag":"metadata_demo",
            "original_context":"demonstration",
            "creation_purpose":"show_consolidation_metadata"
        })
        
        print(f"添加特殊记忆: {special_memory_result}")
        
        # 执行整合
        print(f"\n🔄 执行整合...")
        consolidation_result = self.memory_tool.run({"action":"consolidate",
                                                       "from_type":"working",
                                                       "to_type":"episodic",
                                                       "importance_threshold":0.8})
        
        print(f"整合结果: {consolidation_result}")
        
        # 搜索整合后的记忆查看元数据
        print(f"\n🔍 查看整合后的记忆元数据:")
        search_result = self.memory_tool.run({"action":"search",
                                                "query":"特殊记忆",
                                                "memory_type":"episodic",
                                                "limit":1})
        print(search_result)
    
    def demonstrate_multi_type_consolidation(self):
        """演示多类型记忆整合"""
        print("\n🔀 多类型记忆整合演示")
        print("-" * 50)
        
        print("多类型整合场景:")
        print("• working → episodic (经历记录)")
        print("• working → semantic (知识提取)")
        print("• episodic → semantic (经验总结)")
        
        # 添加一些适合不同整合路径的记忆
        consolidation_candidates = [
            {
                "content": "学习了深度学习中的反向传播算法原理",
                "memory_type": "working",
                "importance": 0.9,
                "learning_type": "concept",
                "suitable_for": "semantic"
            },
            {
                "content": "今天下午参加了AI技术分享会",
                "memory_type": "working", 
                "importance": 0.8,
                "event_type": "meeting",
                "suitable_for": "episodic"
            },
            {
                "content": "通过多次实践掌握了Transformer的实现技巧",
                "memory_type": "episodic",
                "importance": 0.85,
                "experience_type": "skill",
                "suitable_for": "semantic"
            }
        ]
        
        print(f"\n📝 添加整合候选记忆:")
        for memory in consolidation_candidates:
            content = memory.pop("content")
            memory_type = memory.pop("memory_type")
            importance = memory.pop("importance")
            suitable_for = memory.pop("suitable_for")
            
            result = self.memory_tool.run({"action":"add",
                                            "content":content,
                                            "memory_type":memory_type,
                                            "importance":importance,
                                            **memory})
            
            print(f"  • {content[:50]}... → 适合整合为{suitable_for}")
        
        # 执行不同类型的整合
        consolidation_paths = [
            ("working", "episodic", 0.75, "经历记录整合"),
            ("working", "semantic", 0.85, "知识提取整合"),
            ("episodic", "semantic", 0.8, "经验总结整合")
        ]
        
        for from_type, to_type, threshold, description in consolidation_paths:
            print(f"\n🔄 {description} ({from_type} → {to_type}):")
            
            result = self.memory_tool.run({"action":"consolidate",
                                            "from_type":from_type,
                                            "to_type":to_type,
                                            "importance_threshold":threshold})
            
            print(f"整合结果: {result}")
    
    def demonstrate_consolidation_benefits(self):
        """演示记忆整合的益处"""
        print("\n✨ 记忆整合益处演示")
        print("-" * 50)
        
        print("整合益处:")
        print("• 长期保存重要信息")
        print("• 释放工作记忆空间")
        print("• 形成知识体系")
        print("• 提升检索效率")
        
        # 获取最终的记忆系统状态
        print(f"\n📊 最终记忆系统状态:")
        final_stats = self.memory_tool.run({"action":"stats"})
        print(final_stats)
        
        # 获取各类型记忆的摘要
        print(f"\n📋 各类型记忆摘要:")
        
        memory_types = ["working", "episodic", "semantic"]
        for memory_type in memory_types:
            print(f"\n{memory_type.upper()}记忆:")
            type_summary = self.memory_tool.run({"action":"search",
                                                   "query":"",
                                                   "memory_type":memory_type,
                                                   "limit":3})
            print(type_summary)
        
        # 演示整合后的检索效果
        print(f"\n🔍 整合后的检索效果测试:")
        search_queries = [
            ("深度学习", "测试跨类型检索"),
            ("学习经历", "测试整合记忆检索"),
            ("重要概念", "测试语义记忆检索")
        ]
        
        for query, description in search_queries:
            print(f"\n查询: '{query}' ({description})")
            result = self.memory_tool.run({"action":"search",
                                            "query":query,
                                            "limit":3})
            print(result)

def main():
    """主函数"""
    print("🔄 记忆整合机制演示")
    print("展示从短期记忆到长期记忆的智能转化过程")
    print("=" * 60)
    
    try:
        demo = MemoryConsolidationDemo()
        
        # 1. 设置初始记忆数据
        demo.setup_initial_memories()
        
        # 2. 演示整合标准
        demo.demonstrate_consolidation_criteria()
        
        # 3. 演示整合过程
        demo.demonstrate_consolidation_process()
        
        # 4. 演示元数据处理
        demo.demonstrate_consolidation_metadata()
        
        # 5. 演示多类型整合
        demo.demonstrate_multi_type_consolidation()
        
        # 6. 演示整合益处
        demo.demonstrate_consolidation_benefits()
        
        print("\n" + "=" * 60)
        print("🎉 记忆整合机制演示完成！")
        print("=" * 60)
        
        print("\n✨ 记忆整合核心特性:")
        print("1. 🎯 智能筛选 - 基于重要性阈值的自动筛选")
        print("2. 🔄 类型转换 - 灵活的记忆类型转换机制")
        print("3. 📋 元数据保持 - 完整保留原始上下文信息")
        print("4. ⚡ 自动化处理 - 无需人工干预的自动整合")
        print("5. 🔀 多路径支持 - 支持多种整合路径")
        
        print("\n🎯 设计理念:")
        print("• 仿生性 - 模拟人类大脑的记忆固化过程")
        print("• 智能性 - 自动识别和处理重要信息")
        print("• 灵活性 - 支持多种整合策略和路径")
        print("• 完整性 - 保持记忆的完整性和可追溯性")
        
        print("\n💡 应用价值:")
        print("• 知识管理 - 将临时学习转化为长期知识")
        print("• 经验积累 - 保存重要的实践经验")
        print("• 系统优化 - 释放短期记忆空间")
        print("• 智能决策 - 基于历史经验的决策支持")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()