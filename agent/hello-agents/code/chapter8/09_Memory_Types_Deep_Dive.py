#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码示例 09: 四种记忆类型深度解析
详细展示WorkingMemory、EpisodicMemory、SemanticMemory、PerceptualMemory的实现特点
"""

from dotenv import load_dotenv
load_dotenv()
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from hello_agents.tools import MemoryTool

class MemoryTypesDeepDive:
    """四种记忆类型深度解析演示类"""
    
    def __init__(self):
        self.setup_memory_systems()
    
    def setup_memory_systems(self):
        """设置不同的记忆系统"""
        print("🧠 四种记忆类型深度解析")
        print("=" * 60)
        
        # 创建专门的记忆工具实例
        self.working_memory_tool = MemoryTool(
            user_id="working_memory_user",
            memory_types=["working"]
        )
        
        self.episodic_memory_tool = MemoryTool(
            user_id="episodic_memory_user", 
            memory_types=["episodic"]
        )
        
        self.semantic_memory_tool = MemoryTool(
            user_id="semantic_memory_user",
            memory_types=["semantic"]
        )
        
        self.perceptual_memory_tool = MemoryTool(
            user_id="perceptual_memory_user",
            memory_types=["perceptual"]
        )
        
        print("✅ 四种记忆系统初始化完成")
    
    def demonstrate_working_memory(self):
        """演示工作记忆的特点"""
        print("\n💭 工作记忆 (Working Memory) 深度解析")
        print("-" * 60)
        
        print("🔍 工作记忆特点:")
        print("• ⚡ 访问速度极快（纯内存存储）")
        print("• 📏 容量有限（默认50条记忆）")
        print("• ⏰ 自动过期（TTL机制）")
        print("• 🔄 适合临时信息存储")
        
        # 演示容量限制
        print(f"\n1. 容量限制演示:")
        print("添加大量临时记忆，观察容量管理...")
        
        for i in range(8):
            content = f"临时工作记忆 {i+1}: 当前正在处理任务步骤 {i+1}"
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":content,
                                                    "memory_type":"working",
                                                    "importance":0.3 + (i * 0.1),
                                                    "task_step":i+1})
            print(f"  添加记忆 {i+1}: {result}")
        
        # 检查当前状态
        stats = self.working_memory_tool.run({"action":"stats"})
        print(f"\n当前工作记忆状态: {stats}")
        
        # 演示TTL机制
        print(f"\n2. TTL（生存时间）机制演示:")
        
        # 添加一些带时间戳的记忆
        current_time = datetime.now()
        
        # 模拟不同时间的记忆
        time_memories = [
            ("刚刚的想法", 0, 0.8),
            ("5分钟前的任务", 5, 0.6),
            ("10分钟前的提醒", 10, 0.4),
            ("很久以前的笔记", 30, 0.2)
        ]
        
        for content, minutes_ago, importance in time_memories:
            # 这里我们模拟时间差异
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":content,
                                                    "memory_type":"working",
                                                    "importance":importance,
                                                    "simulated_age_minutes":minutes_ago})
            print(f"  添加记忆: {content} (模拟 {minutes_ago} 分钟前)")
        
        # 演示快速检索
        print(f"\n3. 快速检索演示:")
        
        search_queries = ["任务", "想法", "提醒"]
        
        for query in search_queries:
            start_time = time.time()
            results = self.working_memory_tool.run({"action":"search",
                                                     "query":query,
                                                     "memory_type":"working",
                                                     "limit":3})
            search_time = time.time() - start_time
            print(f"  查询 '{query}': {search_time:.4f}秒")
            print(f"    结果: {results[:100]}...")
        
        # 演示自动清理
        print(f"\n4. 自动清理机制:")
        
        # 获取清理前的统计
        before_stats = self.working_memory_tool.run({"action":"stats"})
        print(f"清理前: {before_stats}")
        
        # 触发清理（通过遗忘低重要性记忆）
        forget_result = self.working_memory_tool.run({"action":"forget",
                                                       "strategy":"importance_based",
                                                       "threshold":0.4})
        print(f"清理结果: {forget_result}")
        
        # 获取清理后的统计
        after_stats = self.working_memory_tool.run({"action":"stats"})
        print(f"清理后: {after_stats}")
    
    def demonstrate_episodic_memory(self):
        """演示情景记忆的特点"""
        print("\n📖 情景记忆 (Episodic Memory) 深度解析")
        print("-" * 60)
        
        print("🔍 情景记忆特点:")
        print("• 📅 完整的时间序列记录")
        print("• 🎭 丰富的上下文信息")
        print("• 🔗 支持记忆链条构建")
        print("• 💾 持久化存储")
        
        # 演示完整事件记录
        print(f"\n1. 完整事件记录演示:")
        
        # 模拟一个完整的学习会话
        learning_session = [
            {
                "content": "开始学习Python机器学习",
                "context": "学习开始",
                "location": "家里书房",
                "mood": "专注",
                "importance": 0.7
            },
            {
                "content": "学习了线性回归的数学原理",
                "context": "理论学习",
                "chapter": "第3章",
                "difficulty": "中等",
                "importance": 0.8
            },
            {
                "content": "实现了第一个线性回归模型",
                "context": "实践编程",
                "code_lines": 45,
                "bugs_fixed": 2,
                "importance": 0.9
            },
            {
                "content": "完成了课后练习题",
                "context": "练习巩固",
                "exercises_completed": 5,
                "accuracy": 0.8,
                "importance": 0.6
            },
            {
                "content": "总结今天的学习收获",
                "context": "学习总结",
                "key_concepts": ["线性回归", "梯度下降", "损失函数"],
                "importance": 0.8
            }
        ]
        
        session_id = f"learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for i, event in enumerate(learning_session):
            result = self.episodic_memory_tool.run({"action":"add",
                                                     "content":event["content"],
                                                     "memory_type":"episodic",
                                                     "importance":event["importance"],
                                                     "session_id":session_id,
                                                     "sequence_number":i+1,
                                                     **{k: v for k, v in event.items() if k not in ["content", "importance"]}})
            print(f"  事件 {i+1}: {result}")
        
        # 演示时间序列检索
        print(f"\n2. 时间序列检索演示:")
        
        # 按时间顺序检索
        timeline_search = self.episodic_memory_tool.run({"action":"search",
                                                          "query":"学习",
                                                          "memory_type":"episodic",
                                                          "limit":10})
        print(f"学习时间线: {timeline_search}")
        
        # 按会话检索
        session_search = self.episodic_memory_tool.run({"action":"search",
                                                         "query":"线性回归",
                                                         "memory_type":"episodic",
                                                         "limit":5})
        print(f"会话内容: {session_search}")
        
        # 演示上下文丰富性
        print(f"\n3. 上下文信息演示:")
        
        # 添加带有丰富上下文的记忆
        rich_context_memory = {
            "content": "参加了AI技术分享会",
            "event_type": "conference",
            "location": "北京国际会议中心",
            "speakers": ["张教授", "李博士", "王工程师"],
            "topics": ["深度学习", "自然语言处理", "计算机视觉"],
            "attendees_count": 200,
            "duration_hours": 6,
            "weather": "晴朗",
            "transportation": "地铁",
            "networking_contacts": 3,
            "key_insights": ["Transformer架构的演进", "多模态学习的前景"],
            "follow_up_actions": ["阅读推荐论文", "尝试新框架"],
            "satisfaction_rating": 9
        }
        
        context_result = self.episodic_memory_tool.run({"action":"add",
                                                         "content":rich_context_memory["content"],
                                                         "memory_type":"episodic",
                                                         "importance":0.9,
                                                         **{k: v for k, v in rich_context_memory.items() if k != "content"}})
        print(f"丰富上下文记忆: {context_result}")
        
        # 演示记忆链条
        print(f"\n4. 记忆链条构建:")
        
        # 创建相关联的记忆序列
        memory_chain = [
            ("看到一篇关于GPT的论文", "trigger", None),
            ("决定深入研究Transformer架构", "decision", "trigger"),
            ("下载并阅读Attention is All You Need论文", "action", "decision"),
            ("实现了简化版的自注意力机制", "implementation", "action"),
            ("在项目中应用了学到的知识", "application", "implementation")
        ]
        
        chain_memories = {}
        for content, chain_type, parent_type in memory_chain:
            parent_id = chain_memories.get(parent_type) if parent_type else None
            
            result = self.episodic_memory_tool.run({"action":"add",
                                                     "content":content,
                                                     "memory_type":"episodic",
                                                     "importance":0.7,
                                                     "chain_type":chain_type,
                                                     "parent_memory":parent_id,
                                                     "chain_id":"gpt_learning_chain"})
            
            # 提取记忆ID（简化处理）
            memory_id = f"{chain_type}_memory"
            chain_memories[chain_type] = memory_id
            print(f"  链条记忆: {content} (类型: {chain_type})")
        
        # 检索整个链条
        chain_search = self.episodic_memory_tool.run({"action":"search",
                                                        "query":"GPT Transformer",
                                                        "memory_type":"episodic",
                                                        "limit":8})
        print(f"记忆链条检索: {chain_search}")
    
    def demonstrate_semantic_memory(self):
        """演示语义记忆的特点"""
        print("\n🧠 语义记忆 (Semantic Memory) 深度解析")
        print("-" * 60)
        
        print("🔍 语义记忆特点:")
        print("• 🔗 知识图谱结构化存储")
        print("• 🎯 概念和关系的抽象表示")
        print("• 🔍 语义相似度检索")
        print("• 🧮 支持推理和关联")
        
        # 演示概念存储
        print(f"\n1. 概念知识存储演示:")
        
        # 添加不同类型的概念知识
        concepts = [
            {
                "content": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式",
                "concept_type": "definition",
                "domain": "artificial_intelligence",
                "keywords": ["机器学习", "人工智能", "算法", "数据", "模式"],
                "importance": 0.9
            },
            {
                "content": "监督学习使用标记数据训练模型，包括分类和回归两大类任务",
                "concept_type": "category",
                "domain": "machine_learning",
                "parent_concept": "机器学习",
                "subcategories": ["分类", "回归"],
                "importance": 0.8
            },
            {
                "content": "梯度下降是一种优化算法，通过迭代更新参数来最小化损失函数",
                "concept_type": "algorithm",
                "domain": "optimization",
                "mathematical_basis": "微积分",
                "applications": ["神经网络训练", "线性回归"],
                "importance": 0.8
            },
            {
                "content": "过拟合是指模型在训练数据上表现很好，但在新数据上泛化能力差",
                "concept_type": "problem",
                "domain": "machine_learning",
                "causes": ["模型复杂度过高", "训练数据不足"],
                "solutions": ["正则化", "交叉验证", "早停"],
                "importance": 0.7
            }
        ]
        
        for concept in concepts:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":concept["content"],
                                                     "memory_type":"semantic",
                                                     "importance":concept["importance"],
                                                     **{k: v for k, v in concept.items() if k not in ["content", "importance"]}})
            print(f"  概念存储: {concept['concept_type']} - {result}")
        
        # 演示关系推理
        print(f"\n2. 关系推理演示:")
        
        # 添加关系知识
        relationships = [
            {
                "content": "深度学习是机器学习的子集，使用多层神经网络",
                "relation_type": "is_subset_of",
                "subject": "深度学习",
                "object": "机器学习",
                "strength": 0.9
            },
            {
                "content": "卷积神经网络特别适合处理图像数据",
                "relation_type": "suitable_for",
                "subject": "卷积神经网络",
                "object": "图像处理",
                "strength": 0.8
            },
            {
                "content": "反向传播算法用于训练神经网络",
                "relation_type": "used_for",
                "subject": "反向传播",
                "object": "神经网络训练",
                "strength": 0.9
            }
        ]
        
        for relation in relationships:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":relation["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in relation.items() if k != "content"}})
            print(f"  关系存储: {relation['relation_type']} - {result}")
        
        # 演示语义检索
        print(f"\n3. 语义相似度检索:")
        
        semantic_queries = [
            "什么是人工智能？",
            "如何防止模型过拟合？",
            "神经网络的训练方法",
            "图像识别技术"
        ]
        
        for query in semantic_queries:
            start_time = time.time()
            results = self.semantic_memory_tool.run({"action":"search",
                                                      "query":query,
                                                      "memory_type":"semantic",
                                                      "limit":3})
            search_time = time.time() - start_time
            print(f"  查询: '{query}' ({search_time:.4f}秒)")
            print(f"    结果: {results[:150]}...")
        
        # 演示知识图谱构建
        print(f"\n4. 知识图谱构建:")
        
        # 添加实体和关系
        entities_and_relations = [
            {
                "content": "TensorFlow是Google开发的深度学习框架",
                "entity_type": "framework",
                "developer": "Google",
                "domain": "deep_learning",
                "language": "Python",
                "year": 2015
            },
            {
                "content": "PyTorch是Facebook开发的深度学习框架，以动态图著称",
                "entity_type": "framework", 
                "developer": "Facebook",
                "domain": "deep_learning",
                "feature": "dynamic_graph",
                "language": "Python"
            },
            {
                "content": "BERT是基于Transformer的预训练语言模型",
                "entity_type": "model",
                "architecture": "Transformer",
                "task": "natural_language_processing",
                "training_method": "pre_training"
            }
        ]
        
        for item in entities_and_relations:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":item["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in item.items() if k != "content"}})
            print(f"  实体关系: {item['entity_type']} - {result}")
        
        # 获取语义记忆统计
        semantic_stats = self.semantic_memory_tool.run({"action":"stats"})
        print(f"\n语义记忆统计: {semantic_stats}")
    
    def demonstrate_perceptual_memory(self):
        """演示感知记忆的特点"""
        print("\n👁️ 感知记忆 (Perceptual Memory) 深度解析")
        print("-" * 60)
        
        print("🔍 感知记忆特点:")
        print("• 🎨 多模态数据支持")
        print("• 🔄 跨模态相似性搜索")
        print("• 📊 感知数据的语义理解")
        print("• 🎯 内容生成和检索")
        
        # 演示文本感知记忆
        print(f"\n1. 文本感知记忆:")
        
        text_perceptions = [
            {
                "content": "这是一段优美的诗歌：春江潮水连海平，海上明月共潮生",
                "modality": "text",
                "genre": "poetry",
                "emotion": "peaceful",
                "language": "chinese",
                "aesthetic_value": 0.9
            },
            {
                "content": "技术文档：API接口返回JSON格式数据，包含状态码和响应体",
                "modality": "text",
                "genre": "technical",
                "complexity": "medium",
                "language": "chinese",
                "practical_value": 0.8
            }
        ]
        
        for perception in text_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.7,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  文本感知: {perception['genre']} - {result}")
        
        # 演示图像感知记忆（模拟）
        print(f"\n2. 图像感知记忆（模拟）:")
        
        # 模拟图像数据
        image_perceptions = [
            {
                "content": "一张美丽的日落风景照片",
                "modality": "image",
                "file_path": "/simulated/sunset.jpg",
                "scene_type": "landscape",
                "colors": ["orange", "red", "purple"],
                "objects": ["sun", "clouds", "horizon"],
                "mood": "serene",
                "quality": "high"
            },
            {
                "content": "技术架构图展示了微服务系统设计",
                "modality": "image", 
                "file_path": "/simulated/architecture.png",
                "diagram_type": "technical",
                "components": ["API Gateway", "Services", "Database"],
                "complexity": "high",
                "purpose": "documentation"
            }
        ]
        
        for perception in image_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.8,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  图像感知: {perception['content']} - {result}")
        
        # 演示音频感知记忆（模拟）
        print(f"\n3. 音频感知记忆（模拟）:")
        
        audio_perceptions = [
            {
                "content": "一段优美的古典音乐演奏",
                "modality": "audio",
                "file_path": "/simulated/classical.mp3",
                "genre": "classical",
                "instruments": ["piano", "violin", "cello"],
                "tempo": "andante",
                "emotion": "elegant",
                "duration_seconds": 240
            },
            {
                "content": "技术会议的录音，讨论AI发展趋势",
                "modality": "audio",
                "file_path": "/simulated/conference.wav",
                "content_type": "speech",
                "topic": "artificial_intelligence",
                "speakers": 3,
                "language": "chinese",
                "duration_seconds": 1800
            }
        ]
        
        for perception in audio_perceptions:
            result = self.perceptual_memory_tool.run({"action":"add",
                                                       "content":perception["content"],
                                                       "memory_type":"perceptual",
                                                       "importance":0.7,
                                                       **{k: v for k, v in perception.items() if k != "content"}})
            print(f"  音频感知: {perception['content']} - {result}")
        
        # 演示跨模态检索
        print(f"\n4. 跨模态检索演示:")
        
        cross_modal_queries = [
            ("美丽的风景", "寻找视觉美感相关内容"),
            ("技术文档", "查找技术相关的多模态内容"),
            ("音乐和艺术", "检索艺术相关的感知记忆"),
            ("会议和讨论", "查找交流相关的内容")
        ]
        
        for query, description in cross_modal_queries:
            results = self.perceptual_memory_tool.run({"action":"search",
                                                        "query":query,
                                                        "memory_type":"perceptual",
                                                        "limit":3})
            print(f"  跨模态查询: '{query}' ({description})")
            print(f"    结果: {results[:120]}...")
        
        # 演示感知特征分析
        print(f"\n5. 感知特征分析:")
        
        # 获取感知记忆统计
        perceptual_stats = self.perceptual_memory_tool.run({"action":"stats"})
        print(f"感知记忆统计: {perceptual_stats}")
        
        # 分析不同模态的分布
        modality_analysis = self.perceptual_memory_tool.run({"action":"search",
                                                              "query":"模态分析",
                                                              "memory_type":"perceptual",
                                                              "limit":10})
        print(f"模态分布分析: {modality_analysis}")
    
    def demonstrate_memory_interactions(self):
        """演示四种记忆类型的交互"""
        print("\n🔄 四种记忆类型交互演示")
        print("-" * 60)
        
        print("🔍 记忆交互模式:")
        print("• 🔄 工作记忆 → 情景记忆（重要事件固化）")
        print("• 📚 情景记忆 → 语义记忆（经验抽象化）")
        print("• 👁️ 感知记忆 → 其他记忆（多模态信息整合）")
        print("• 🧠 语义记忆 → 工作记忆（知识激活）")
        
        # 模拟一个完整的学习过程
        print(f"\n完整学习过程模拟:")
        
        # 1. 感知阶段：接收多模态信息
        print(f"\n1. 感知阶段 - 接收信息:")
        
        perceptual_input = self.perceptual_memory_tool.run({"action":"add",
                                                             "content":"观看了一个关于深度学习的视频教程",
                                                             "memory_type":"perceptual",
                                                             "importance":0.8,
                                                             "modality":"video",
                                                             "topic":"deep_learning",
                                                             "duration_minutes":45,
                                                             "quality":"high"})
        print(f"感知记忆: {perceptual_input}")
        
        # 2. 工作记忆阶段：临时处理和思考
        print(f"\n2. 工作记忆阶段 - 临时处理:")
        
        working_thoughts = [
            "理解了卷积神经网络的基本原理",
            "需要记住反向传播的计算步骤",
            "想到了之前学过的线性代数知识",
            "计划实现一个简单的CNN模型"
        ]
        
        for thought in working_thoughts:
            result = self.working_memory_tool.run({"action":"add",
                                                    "content":thought,
                                                    "memory_type":"working",
                                                    "importance":0.6,
                                                    "processing_stage":"active_thinking"})
            print(f"  工作记忆: {thought[:30]}... - {result}")
        
        # 3. 情景记忆阶段：记录完整学习事件
        print(f"\n3. 情景记忆阶段 - 事件记录:")
        
        episodic_event = self.episodic_memory_tool.run({"action":"add",
                                                         "content":"完成了深度学习视频教程的学习，理解了CNN的核心概念",
                                                         "memory_type":"episodic",
                                                         "importance":0.9,
                                                         "event_type":"learning_session",
                                                         "duration_minutes":45,
                                                         "location":"家里",
                                                         "learning_outcome":"理解CNN原理",
                                                         "next_action":"实践编程"})
        print(f"情景记忆: {episodic_event}")
        
        # 4. 语义记忆阶段：抽象知识存储
        print(f"\n4. 语义记忆阶段 - 知识抽象:")
        
        semantic_knowledge = [
            {
                "content": "卷积神经网络通过卷积层提取图像特征，适合计算机视觉任务",
                "concept": "CNN",
                "domain": "deep_learning",
                "application": "computer_vision"
            },
            {
                "content": "反向传播算法通过链式法则计算梯度，用于更新网络参数",
                "concept": "backpropagation",
                "domain": "optimization",
                "mathematical_basis": "chain_rule"
            }
        ]
        
        for knowledge in semantic_knowledge:
            result = self.semantic_memory_tool.run({"action":"add",
                                                     "content":knowledge["content"],
                                                     "memory_type":"semantic",
                                                     "importance":0.8,
                                                     **{k: v for k, v in knowledge.items() if k != "content"}})
            print(f"  语义记忆: {knowledge['concept']} - {result}")
        
        # 5. 记忆整合演示
        print(f"\n5. 记忆整合演示:")
        
        # 从工作记忆整合到情景记忆
        consolidation_result = self.working_memory_tool.run({"action":"consolidate",
                                                              "from_type":"working",
                                                              "to_type":"episodic",
                                                              "importance_threshold":0.6})
        print(f"工作记忆整合: {consolidation_result}")
        
        # 跨记忆类型检索
        print(f"\n6. 跨记忆类型检索:")
        
        query = "深度学习CNN"
        
        # 在所有记忆类型中搜索
        memory_tools = [
            ("工作记忆", self.working_memory_tool),
            ("情景记忆", self.episodic_memory_tool),
            ("语义记忆", self.semantic_memory_tool),
            ("感知记忆", self.perceptual_memory_tool)
        ]
        
        for memory_name, tool in memory_tools:
            results = tool.run({"action":"search", "query":query, "limit":2})
            print(f"  {memory_name}检索: {results[:80]}...")
        
        # 获取所有记忆系统的统计
        print(f"\n7. 系统整体状态:")
        
        for memory_name, tool in memory_tools:
            stats = tool.run({"action":"stats"})
            print(f"  {memory_name}: {stats}")

def main():
    """主函数"""
    print("🧠 四种记忆类型深度解析演示")
    print("详细展示WorkingMemory、EpisodicMemory、SemanticMemory、PerceptualMemory")
    print("=" * 80)
    
    try:
        demo = MemoryTypesDeepDive()
        
        # 1. 工作记忆演示
        demo.demonstrate_working_memory()
        
        # 2. 情景记忆演示
        demo.demonstrate_episodic_memory()
        
        # 3. 语义记忆演示
        demo.demonstrate_semantic_memory()
        
        # 4. 感知记忆演示
        demo.demonstrate_perceptual_memory()
        
        # 5. 记忆交互演示
        demo.demonstrate_memory_interactions()
        
        print("\n" + "=" * 80)
        print("🎉 四种记忆类型深度解析完成！")
        print("=" * 80)
        
        print("\n✨ 记忆类型特性总结:")
        print("1. 💭 工作记忆 - 快速临时存储，容量有限，自动过期")
        print("2. 📖 情景记忆 - 完整事件记录，时间序列，丰富上下文")
        print("3. 🧠 语义记忆 - 抽象知识存储，概念关系，语义推理")
        print("4. 👁️ 感知记忆 - 多模态支持，跨模态检索，感知理解")
        
        print("\n🔄 记忆交互模式:")
        print("• 感知 → 工作 → 情景 → 语义（信息处理流程）")
        print("• 语义 → 工作（知识激活和应用）")
        print("• 跨类型检索和整合（智能记忆管理）")
        
        print("\n💡 设计价值:")
        print("• 模拟人类认知过程")
        print("• 支持多层次信息处理")
        print("• 实现智能记忆管理")
        print("• 提供丰富的检索能力")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()