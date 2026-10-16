#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码示例 03: WorkingMemory实现详解
展示工作记忆的混合检索策略和TTL机制
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from hello_agents.tools import MemoryTool
from hello_agents.memory import MemoryItem
from dotenv import load_dotenv
load_dotenv()

class WorkingMemoryDemo:
    """工作记忆演示类"""
    
    def __init__(self):
        self.memory_tool = MemoryTool(
            user_id="working_memory_demo",
            memory_types=["working"]  # 只启用工作记忆
        )
    
    def demonstrate_capacity_management(self):
        """演示容量管理和TTL机制"""
        print("🧠 工作记忆容量管理演示")
        print("=" * 50)
        
        print("工作记忆特点:")
        print("• 容量有限（默认50条）")
        print("• TTL机制（默认60分钟）")
        print("• 自动清理过期记忆")
        print("• 优先级管理（重要性排序）")
        
        # 添加多条记忆来演示容量管理
        print(f"\n📝 添加测试记忆...")
        for i in range(10):
            importance = 0.3 + (i * 0.07)  # 递增重要性
            self.memory_tool.run({
                "action":"add",
                "content":f"工作记忆测试项目 {i+1} - 重要性 {importance:.2f}",
                "memory_type":"working",
                "importance":importance,
                "test_id":i+1,
                "category":"capacity_test"
            })
        
        # 查看当前状态
        stats = self.memory_tool.run({"action":"stats"})
        print(f"当前状态: {stats}")
        
        # 演示重要性排序
        print(f"\n🔍 按重要性搜索:")
        result = self.memory_tool.run({
            "action":"search", 
            "query":"测试项目", 
            "memory_type":"working",
            "limit":5
        })
        print(result)
    
    def demonstrate_mixed_retrieval_strategy(self):
        """演示混合检索策略"""
        print("\n🔍 混合检索策略演示")
        print("-" * 40)
        
        print("混合检索策略包括:")
        print("• TF-IDF向量化语义检索")
        print("• 关键词匹配检索")
        print("• 时间衰减因子")
        print("• 重要性权重调整")
        
        # 添加不同类型的记忆用于检索测试
        test_memories = [
            {
                "content": "Python是一种高级编程语言，语法简洁清晰",
                "importance": 0.8,
                "topic": "programming",
                "language": "python"
            },
            {
                "content": "机器学习是人工智能的重要分支，包括监督学习和无监督学习",
                "importance": 0.9,
                "topic": "ai",
                "domain": "machine_learning"
            },
            {
                "content": "数据结构包括数组、链表、栈、队列等基本结构",
                "importance": 0.7,
                "topic": "computer_science",
                "category": "data_structures"
            },
            {
                "content": "算法复杂度分析使用大O记号来描述时间和空间复杂度",
                "importance": 0.8,
                "topic": "algorithms",
                "analysis": "complexity"
            }
        ]
        
        print(f"\n📝 添加测试记忆...")
        for i, memory in enumerate(test_memories):
            content = memory.pop("content")
            importance = memory.pop("importance")
            self.memory_tool.run({
                "action":"add",
                "content":content,
                "memory_type":"working",
                "importance":importance,
                **memory
            })
        
        # 测试不同类型的检索
        search_tests = [
            ("Python编程", "测试语义匹配"),
            ("学习", "测试关键词匹配"),
            ("复杂度", "测试部分匹配"),
            ("人工智能机器学习", "测试多词匹配")
        ]
        
        print(f"\n🔍 混合检索测试:")
        for query, description in search_tests:
            print(f"\n查询: '{query}' ({description})")
            result = self.memory_tool.run({
                "action":"search",
                "query":query,
                "memory_type":"working",
                "limit":2
            })
            print(f"结果: {result}")
    
    def demonstrate_time_decay_mechanism(self):
        """演示时间衰减机制"""
        print("\n⏰ 时间衰减机制演示")
        print("-" * 40)
        
        print("时间衰减机制:")
        print("• 新记忆权重更高")
        print("• 旧记忆权重衰减")
        print("• 模拟人类记忆特点")
        print("• 平衡新旧信息重要性")
        
        # 添加不同时间的记忆（模拟）
        time_test_memories = [
            ("最新的重要信息 - 刚刚学习的概念", 0.7, "newest"),
            ("较新的信息 - 昨天学习的内容", 0.7, "recent"), 
            ("较旧的信息 - 上周学习的内容", 0.7, "older"),
            ("最旧的信息 - 很久以前的内容", 0.7, "oldest")
        ]
        
        print(f"\n📝 添加不同时期的记忆...")
        for content, importance, age_category in time_test_memories:
            self.memory_tool.run({
                "action":"add",
                "content":content,
                "memory_type":"working",
                "importance":importance,
                "age_category":age_category,
                "timestamp_category":age_category
            })
        
        # 搜索测试时间衰减效果
        print(f"\n🔍 时间衰减效果测试:")
        result = self.memory_tool.run({
            "action":"search",
            "query":"学习的内容",
            "memory_type":"working",
            "limit":4
        })
        print("搜索结果（注意时间因素对排序的影响）:")
        print(result)
    
    def demonstrate_automatic_cleanup(self):
        """演示自动清理机制"""
        print("\n🧹 自动清理机制演示")
        print("-" * 40)
        
        print("自动清理机制:")
        print("• 过期记忆自动清理")
        print("• 容量超限时清理低优先级记忆")
        print("• 保持系统性能和响应速度")
        print("• 模拟工作记忆的有限容量")
        
        # 获取清理前的状态
        stats_before = self.memory_tool.run({"action":"stats"})
        print(f"\n清理前状态: {stats_before}")
        
        # 添加一些低重要性的记忆
        print(f"\n📝 添加低重要性记忆...")
        for i in range(5):
            self.memory_tool.run({
                "action":"add",
                "content":f"低重要性临时记忆 {i+1}",
                "memory_type":"working",
                "importance":0.1 + i * 0.05,
                "temporary":True,
                "cleanup_test":True
            })
        
        # 触发基于重要性的清理
        print(f"\n🧹 执行基于重要性的清理...")
        cleanup_result = self.memory_tool.run({
            "action":"forget",
            "strategy":"importance_based",
            "threshold":0.3
        })
        print(f"清理结果: {cleanup_result}")
        
        # 获取清理后的状态
        stats_after = self.memory_tool.run({"action":"stats"})
        print(f"\n清理后状态: {stats_after}")
    
    def demonstrate_performance_characteristics(self):
        """演示性能特征"""
        print("\n⚡ 性能特征演示")
        print("-" * 40)
        
        print("工作记忆性能特点:")
        print("• 纯内存存储，访问速度极快")
        print("• 无需磁盘I/O，响应时间短")
        print("• 适合频繁访问的临时数据")
        print("• 系统重启后数据丢失（符合设计）")
        
        # 性能测试
        print(f"\n⏱️ 性能测试:")
        
        # 批量添加测试
        start_time = time.time()
        for i in range(20):
            self.memory_tool.run({
                "action":"add",
                "content":f"性能测试记忆 {i+1}",
                "memory_type":"working",
                "importance":0.5,
                "performance_test":True
            })
        add_time = time.time() - start_time
        print(f"批量添加20条记忆耗时: {add_time:.3f}秒")
        
        # 批量搜索测试
        start_time = time.time()
        for i in range(10):
            self.memory_tool.run({
                "action":"search",
                "query":f"性能测试",
                "memory_type":"working",
                "limit":3
            })
        search_time = time.time() - start_time
        print(f"批量搜索10次耗时: {search_time:.3f}秒")
        
        # 获取最终统计
        final_stats = self.memory_tool.run("stats")
        print(f"\n📊 最终统计: {final_stats}")

def main():
    """主函数"""
    print("🧠 WorkingMemory实现详解")
    print("展示工作记忆的核心特性和实现机制")
    print("=" * 60)
    
    try:
        demo = WorkingMemoryDemo()
        
        # 1. 容量管理演示
        demo.demonstrate_capacity_management()
        
        # 2. 混合检索策略演示
        demo.demonstrate_mixed_retrieval_strategy()
        
        # 3. 时间衰减机制演示
        demo.demonstrate_time_decay_mechanism()
        
        # 4. 自动清理机制演示
        demo.demonstrate_automatic_cleanup()
        
        # 5. 性能特征演示
        demo.demonstrate_performance_characteristics()
        
        print("\n" + "=" * 60)
        print("🎉 WorkingMemory实现演示完成！")
        print("=" * 60)
        
        print("\n✨ 工作记忆核心特性:")
        print("1. 🧠 有限容量 - 模拟人类工作记忆限制")
        print("2. ⚡ 高速访问 - 纯内存存储，响应迅速")
        print("3. 🔍 混合检索 - 语义+关键词+时间+重要性")
        print("4. ⏰ 时间衰减 - 新信息优先，旧信息衰减")
        print("5. 🧹 自动清理 - TTL机制+优先级管理")
        
        print("\n🎯 设计理念:")
        print("• 临时性 - 存储当前会话的临时信息")
        print("• 高效性 - 快速访问和处理能力")
        print("• 智能性 - 自动管理和优化策略")
        print("• 仿生性 - 模拟人类工作记忆特点")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()