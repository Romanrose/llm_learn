#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码示例 02: MemoryTool架构设计
展示MemoryTool和MemoryManager的分层架构
"""

from dotenv import load_dotenv
load_dotenv()
from typing import List, Optional, Dict, Any
from datetime import datetime
from hello_agents.tools import MemoryTool
from hello_agents.memory import MemoryConfig

class MemoryToolArchitectureDemo:
    """MemoryTool架构演示类"""
    
    def __init__(self):
        self.memory_config = MemoryConfig()
        self.memory_types = ["working", "episodic", "semantic", "perceptual"]
    
    def demonstrate_memory_tool_init(self):
        """演示MemoryTool初始化过程"""
        print("🏗️ MemoryTool架构设计演示")
        print("=" * 50)
        
        print("📋 MemoryTool初始化过程:")
        print("1. 创建MemoryConfig配置对象")
        print("2. 指定启用的记忆类型")
        print("3. 初始化MemoryManager管理器")
        print("4. 根据配置启用不同记忆模块")
        
        # 演示MemoryTool的初始化
        memory_tool = MemoryTool(
            user_id="architecture_demo_user",
            memory_config=self.memory_config,
            memory_types=self.memory_types
        )
        
        print(f"\n✅ MemoryTool初始化完成")
        print(f"👤 用户ID: {memory_tool.memory_manager.user_id}")
        print(f"🧠 启用的记忆类型: {memory_tool.memory_types}")
        print(f"⚙️ 配置对象: {type(memory_tool.memory_config).__name__}")
        
        return memory_tool
    
    def demonstrate_memory_manager_architecture(self, memory_tool):
        """演示MemoryManager的组合模式架构"""
        print("\n🔧 MemoryManager架构设计")
        print("-" * 40)
        
        print("MemoryManager采用组合模式设计:")
        print("- 统一的记忆操作接口")
        print("- 独立的记忆类型组件")
        print("- 灵活的配置和扩展能力")
        
        # 获取MemoryManager实例
        memory_manager = memory_tool.memory_manager
        
        print(f"\n📊 MemoryManager状态:")
        print(f"用户ID: {memory_manager.user_id}")
        print(f"配置类型: {type(memory_manager.config).__name__}")
        print(f"记忆类型数量: {len(memory_manager.memory_types)}")
        
        # 显示各记忆类型的状态
        print(f"\n🧠 记忆类型组件:")
        for memory_type, memory_instance in memory_manager.memory_types.items():
            print(f"  • {memory_type}: {type(memory_instance).__name__}")
    
    def demonstrate_memory_types_specialization(self, memory_tool):
        """演示四种记忆类型的专业化特点"""
        print("\n🎯 四种记忆类型的专业化设计")
        print("-" * 40)
        
        memory_types_info = {
            "working": {
                "name": "工作记忆",
                "features": ["容量有限", "访问速度快", "自动清理", "临时存储"],
                "storage": "纯内存存储",
                "ttl": "60分钟TTL机制"
            },
            "episodic": {
                "name": "情景记忆", 
                "features": ["事件序列", "时间序列", "上下文丰富", "会话关联"],
                "storage": "SQLite + Qdrant混合存储",
                "ttl": "持久化存储"
            },
            "semantic": {
                "name": "语义记忆",
                "features": ["概念知识", "实体关系", "知识图谱", "语义推理"],
                "storage": "Neo4j + Qdrant混合存储", 
                "ttl": "长期存储"
            },
            "perceptual": {
                "name": "感知记忆",
                "features": ["多模态", "跨模态检索", "感知数据", "内容生成"],
                "storage": "分模态向量存储",
                "ttl": "按重要性管理"
            }
        }
        
        for memory_type, info in memory_types_info.items():
            print(f"\n📚 {info['name']} ({memory_type}):")
            print(f"   特点: {', '.join(info['features'])}")
            print(f"   存储: {info['storage']}")
            print(f"   生命周期: {info['ttl']}")
            
            # 添加示例记忆来演示特点
            if memory_type == "working":
                memory_tool.run({
                    "action":"add",
                    "content":f"演示{info['name']}的临时存储特性",
                    "memory_type":memory_type,
                    "importance":0.6,
                    "demo_feature":"temporary_storage"
                })
            elif memory_type == "episodic":
                memory_tool.run({
                    "action":"add",
                    "content":f"演示{info['name']}的事件记录特性",
                    "memory_type":memory_type,
                    "importance":0.7,
                    "event_type":"demonstration",
                    "session_context":"architecture_demo"
                })
            elif memory_type == "semantic":
                memory_tool.run({
                    "action":"add",
                    "content":f"{info['name']}用于存储概念性知识和实体关系",
                    "memory_type":memory_type,
                    "importance":0.8,
                    "concept":"memory_architecture",
                    "domain":"cognitive_computing"
                })
            elif memory_type == "perceptual":
                memory_tool.run({
                    "action":"add",
                    "content":f"演示{info['name']}的多模态数据处理",
                    "memory_type":memory_type,
                    "importance":0.6,
                    "modality":"text",
                    "data_type":"demonstration"
                })
    
    def demonstrate_unified_interface(self, memory_tool):
        """演示统一接口的设计优势"""
        print("\n🔗 统一接口设计优势")
        print("-" * 40)
        
        print("统一的execute方法提供:")
        print("• 一致的调用方式")
        print("• 灵活的参数传递")
        print("• 统一的错误处理")
        print("• 简化的用户体验")
        
        # 演示统一接口的使用
        operations = [
            ("search", {"query": "演示", "limit": 2}),
            ("summary", {"limit": 3}),
            ("stats", {}),
        ]
        
        print(f"\n🔧 统一接口操作演示:")
        for operation, params in operations:
            print(f"\n操作: {operation}")
            print(f"参数: {params}")
            result = memory_tool.run({"action":operation, **params})
            print(f"结果: {result[:100]}..." if len(str(result)) > 100 else f"结果: {result}")
    
    def demonstrate_extensibility(self):
        """演示系统的扩展性设计"""
        print("\n🚀 系统扩展性设计")
        print("-" * 40)
        
        print("扩展性特点:")
        print("• 插件化的记忆类型")
        print("• 可配置的存储后端") 
        print("• 灵活的记忆策略")
        print("• 模块化的组件设计")
        
        # 演示自定义配置
        custom_config = MemoryConfig()
        custom_config.working_memory_capacity = 100
        custom_config.working_memory_ttl_minutes = 120
        
        print(f"\n⚙️ 自定义配置示例:")
        print(f"工作记忆容量: {custom_config.working_memory_capacity}")
        print(f"工作记忆TTL: {custom_config.working_memory_ttl_minutes}分钟")
        
        # 演示选择性启用记忆类型
        selective_memory_tool = MemoryTool(
            user_id="selective_user",
            memory_config=custom_config,
            memory_types=["working", "semantic"]  # 只启用部分类型
        )
        
        print(f"\n🎯 选择性启用示例:")
        print(f"启用的记忆类型: {selective_memory_tool.memory_types}")
        print("✅ 系统支持根据需求灵活配置")

def main():
    """主函数"""
    print("🏗️ MemoryTool架构设计完整演示")
    print("展示记忆系统的分层架构和设计模式")
    print("=" * 60)
    
    try:
        demo = MemoryToolArchitectureDemo()
        
        # 1. MemoryTool初始化演示
        memory_tool = demo.demonstrate_memory_tool_init()
        
        # 2. MemoryManager架构演示
        demo.demonstrate_memory_manager_architecture(memory_tool)
        
        # 3. 记忆类型专业化演示
        demo.demonstrate_memory_types_specialization(memory_tool)
        
        # 4. 统一接口演示
        demo.demonstrate_unified_interface(memory_tool)
        
        # 5. 扩展性演示
        demo.demonstrate_extensibility()
        
        print("\n" + "=" * 60)
        print("🎉 MemoryTool架构演示完成！")
        print("=" * 60)
        
        print("\n✨ 架构设计亮点:")
        print("1. 🏗️ 分层架构 - 关注点分离，职责清晰")
        print("2. 🔧 组合模式 - 灵活组合，独立管理")
        print("3. 🎯 专业化设计 - 各记忆类型特点鲜明")
        print("4. 🔗 统一接口 - 简化使用，一致体验")
        print("5. 🚀 高扩展性 - 插件化设计，灵活配置")
        
        print("\n🎯 设计原则:")
        print("• 单一职责原则 - 每个组件专注特定功能")
        print("• 开闭原则 - 对扩展开放，对修改封闭")
        print("• 依赖倒置原则 - 依赖抽象，不依赖具体")
        print("• 组合优于继承 - 灵活组合，避免复杂继承")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()