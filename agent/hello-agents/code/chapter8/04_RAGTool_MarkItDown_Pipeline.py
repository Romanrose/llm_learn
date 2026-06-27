#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码示例 04: RAGTool的MarkItDown处理管道
展示Any格式→Markdown→分块→向量化的完整流程
"""

import os
import time
import tempfile
from hello_agents.tools import RAGTool
from dotenv import load_dotenv
load_dotenv()

class MarkItDownPipelineDemo:
    """MarkItDown处理管道演示类"""
    
    def __init__(self):
        self.rag_tool = RAGTool(
            knowledge_base_path="./demo_rag_kb",
            rag_namespace="markitdown_demo"
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def create_sample_documents(self):
        """创建多格式示例文档"""
        print("📄 创建多格式示例文档")
        print("=" * 50)
        
        # 创建Markdown文档
        markdown_content = """# Python编程指南

## 基础语法
Python是一种解释型、高级编程语言。

### 变量和数据类型
- 整数：`42`
- 字符串：`"Hello World"`
- 列表：`[1, 2, 3]`

### 函数定义
```python
def greet(name):
    return f"Hello, {name}!"
```

## 面向对象编程
Python支持面向对象编程范式。

### 类定义
```python
class Person:
    def __init__(self, name):
        self.name = name
    
    def say_hello(self):
        return f"Hello, I'm {self.name}"
```
"""
        
        # 创建HTML文档
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Web开发基础</title>
</head>
<body>
    <h1>HTML基础</h1>
    <p>HTML是超文本标记语言，用于创建网页结构。</p>
    
    <h2>常用标签</h2>
    <ul>
        <li>h1-h6: 标题标签</li>
        <li>p: 段落标签</li>
        <li>div: 容器标签</li>
        <li>span: 行内标签</li>
    </ul>
    
    <h2>CSS样式</h2>
    <p>CSS用于控制网页的样式和布局。</p>
    <code>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; }
    </code>
</body>
</html>"""
        
        # 创建JSON文档
        json_content = """{
    "project": "HelloAgents",
    "version": "1.0.0",
    "description": "AI Agent开发框架",
    "features": [
        "记忆系统",
        "RAG检索",
        "工具集成",
        "多模态支持"
    ],
    "components": {
        "memory": {
            "types": ["working", "episodic", "semantic", "perceptual"],
            "storage": ["SQLite", "Qdrant", "Neo4j"]
        },
        "rag": {
            "formats": ["PDF", "Word", "Excel", "HTML", "Markdown"],
            "pipeline": ["MarkItDown", "Chunking", "Embedding", "Storage"]
        }
    }
}"""
        
        # 创建CSV文档
        csv_content = """名称,类型,重要性,描述
工作记忆,临时存储,0.7,存储当前会话的临时信息
情景记忆,事件记录,0.8,记录具体的事件和经历
语义记忆,知识存储,0.9,存储概念性知识和规则
感知记忆,多模态,0.6,处理图像音频等感知数据
向量检索,技术组件,0.8,基于语义相似度的检索
知识图谱,技术组件,0.9,实体关系的结构化表示"""
        
        # 保存文档到临时目录
        documents = {
            "python_guide.md": markdown_content,
            "web_basics.html": html_content,
            "project_info.json": json_content,
            "memory_types.csv": csv_content
        }
        
        file_paths = {}
        for filename, content in documents.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_paths[filename] = file_path
            print(f"✅ 创建文档: {filename}")
        
        return file_paths
    
    def demonstrate_markitdown_conversion(self, file_paths):
        """演示MarkItDown转换过程"""
        print("\n🔄 MarkItDown转换过程演示")
        print("-" * 50)
        
        print("MarkItDown处理流程:")
        print("1. 📄 检测文档格式")
        print("2. 🔄 转换为Markdown")
        print("3. 📝 保持结构信息")
        print("4. ✨ 统一格式输出")
        
        conversion_results = {}
        
        for filename, file_path in file_paths.items():
            print(f"\n处理文档: {filename}")
            print(f"原始格式: {os.path.splitext(filename)[1]}")
            
            start_time = time.time()
            
            # 使用RAGTool添加文档，内部会调用MarkItDown
            result = self.rag_tool.run({"action":"add_document", 
                                         "file_path":file_path})
            
            process_time = time.time() - start_time
            
            print(f"处理结果: {result}")
            print(f"处理时间: {process_time:.3f}秒")
            print(f"✅ {filename} → Markdown → 分块 → 向量化")
            
            conversion_results[filename] = {
                "result": result,
                "time": process_time
            }
        
        return conversion_results
    
    def demonstrate_markdown_chunking(self):
        """演示基于Markdown的智能分块"""
        print("\n📊 基于Markdown的智能分块演示")
        print("-" * 50)
        
        print("Markdown分块策略:")
        print("• 🏷️ 标题层次感知 - 利用#、##、###结构")
        print("• 📝 段落语义保持 - 保持内容完整性")
        print("• 🔢 Token精确控制 - 适配嵌入模型")
        print("• 🔗 智能重叠策略 - 避免信息丢失")
        
        # 添加一个复杂的Markdown文档来演示分块
        complex_markdown = """# 人工智能技术栈

## 机器学习基础

### 监督学习
监督学习使用标注数据训练模型，包括分类和回归任务。

#### 分类算法
- 逻辑回归：用于二分类和多分类问题
- 决策树：基于特征分割的树形结构
- 随机森林：多个决策树的集成方法
- 支持向量机：寻找最优分离超平面

#### 回归算法
- 线性回归：建立特征与目标的线性关系
- 多项式回归：处理非线性关系
- 岭回归：添加L2正则化的线性回归

### 无监督学习
无监督学习从无标注数据中发现模式和结构。

#### 聚类算法
- K-means：基于距离的聚类方法
- 层次聚类：构建聚类树状结构
- DBSCAN：基于密度的聚类算法

#### 降维算法
- PCA：主成分分析，线性降维
- t-SNE：非线性降维，适合可视化
- UMAP：保持局部和全局结构的降维

## 深度学习

### 神经网络基础
神经网络是深度学习的基础，模拟人脑神经元结构。

#### 基本组件
- 神经元：基本计算单元
- 激活函数：引入非线性
- 损失函数：衡量预测误差
- 优化器：更新网络参数

### 常见架构
- CNN：卷积神经网络，适合图像处理
- RNN：循环神经网络，处理序列数据
- LSTM：长短期记忆网络，解决梯度消失
- Transformer：注意力机制，处理长序列

## 自然语言处理

### 文本预处理
- 分词：将文本分割为词汇单元
- 词性标注：识别词汇的语法角色
- 命名实体识别：提取人名、地名等实体
- 情感分析：判断文本的情感倾向

### 语言模型
- N-gram：基于统计的语言模型
- Word2Vec：词向量表示学习
- BERT：双向编码器表示
- GPT：生成式预训练模型
"""
        
        print(f"\n📝 添加复杂Markdown文档进行分块测试...")
        result = self.rag_tool.run({"action":"add_text",
                                     "text":complex_markdown,
                                     "document_id":"ai_tech_stack",
                                     "chunk_size":800,
                                     "chunk_overlap":100})
        
        print(f"分块结果: {result}")
        
        # 测试基于结构的检索
        print(f"\n🔍 测试基于Markdown结构的检索:")
        
        search_queries = [
            ("监督学习算法", "测试二级标题内容检索"),
            ("神经网络基础", "测试跨层级内容检索"),
            ("BERT GPT", "测试具体技术检索"),
            ("聚类降维", "测试相关概念检索")
        ]
        
        for query, description in search_queries:
            print(f"\n查询: '{query}' ({description})")
            search_result = self.rag_tool.run({"action":"search",
                                                "query":query,
                                                "limit":2})
            print(f"检索结果: {search_result[:200]}...")
    
    def demonstrate_embedding_optimization(self):
        """演示面向嵌入的Markdown预处理"""
        print("\n🎯 面向嵌入的Markdown预处理演示")
        print("-" * 50)
        
        print("Markdown预处理优化:")
        print("• 🏷️ 移除格式标记，保留语义内容")
        print("• 🔗 处理链接格式，保留链接文本")
        print("• 💻 清理代码块，保留代码内容")
        print("• 🧹 清理多余空白，优化向量表示")
        
        # 演示预处理前后的对比
        raw_markdown = """## 代码示例

这是一个**重要的**Python函数：

```python
def process_data(data):
    \"\"\"处理数据的函数\"\"\"
    return [item.strip() for item in data if item]
```

更多信息请参考[官方文档](https://docs.python.org)。

*注意*：这个函数会`自动过滤`空值。
"""
        
        print(f"\n📝 原始Markdown内容:")
        print(raw_markdown)
        
        # 添加到RAG系统，内部会进行预处理
        result = self.rag_tool.run({"action":"add_text",
                                     "text":raw_markdown,
                                     "document_id":"preprocessing_demo"})
        
        print(f"\n✅ 预处理并添加完成: {result}")
        
        # 测试预处理后的检索效果
        print(f"\n🔍 测试预处理后的检索效果:")
        search_result = self.rag_tool.run({"action":"search",
                                            "query":"Python函数处理数据",
                                            "limit":1})
        print(f"检索结果: {search_result}")
    
    def demonstrate_pipeline_performance(self):
        """演示处理管道性能"""
        print("\n⚡ 处理管道性能演示")
        print("-" * 50)
        
        print("性能测试指标:")
        print("• 📄 文档转换速度")
        print("• 📊 分块处理效率")
        print("• 🎯 向量化时间")
        print("• 💾 存储操作耗时")
        
        # 批量处理性能测试
        batch_texts = [
            f"批量处理测试文档 {i+1}：这是一个用于测试MarkItDown处理管道性能的示例文档。"
            f"文档包含了多种格式的内容，包括标题、段落、列表等结构化信息。"
            f"通过批量处理可以评估系统的整体性能表现。" 
            for i in range(10)
        ]
        
        print(f"\n⏱️ 批量处理性能测试 (10个文档):")
        start_time = time.time()
        
        batch_result = self.rag_tool.batch_add_texts(
            batch_texts,
            document_ids=[f"perf_test_{i+1}" for i in range(10)]
        )
        
        batch_time = time.time() - start_time
        
        print(f"批量处理结果: {batch_result}")
        print(f"总耗时: {batch_time:.3f}秒")
        print(f"平均每文档: {batch_time/10:.3f}秒")
        
        # 获取最终统计
        stats = self.rag_tool.run({"action":"stats"})
        print(f"\n📊 最终统计: {stats}")

def main():
    """主函数"""
    print("🔄 RAGTool的MarkItDown处理管道演示")
    print("展示Any格式→Markdown→分块→向量化的完整流程")
    print("=" * 70)
    
    try:
        demo = MarkItDownPipelineDemo()
        
        # 1. 创建多格式示例文档
        file_paths = demo.create_sample_documents()
        
        # 2. 演示MarkItDown转换过程
        conversion_results = demo.demonstrate_markitdown_conversion(file_paths)
        
        # 3. 演示基于Markdown的智能分块
        demo.demonstrate_markdown_chunking()
        
        # 4. 演示面向嵌入的预处理优化
        demo.demonstrate_embedding_optimization()
        
        # 5. 演示处理管道性能
        demo.demonstrate_pipeline_performance()
        
        print("\n" + "=" * 70)
        print("🎉 MarkItDown处理管道演示完成！")
        print("=" * 70)
        
        print("\n✨ 处理管道核心特性:")
        print("1. 🔄 格式统一 - Any格式→Markdown标准化")
        print("2. 🏗️ 结构保持 - 保留文档逻辑结构")
        print("3. 📊 智能分块 - 基于Markdown结构的语义分割")
        print("4. 🎯 嵌入优化 - 针对向量化的预处理")
        print("5. ⚡ 高效处理 - 批量处理和性能优化")
        
        print("\n🎯 技术优势:")
        print("• 统一处理 - 一套流程处理所有格式")
        print("• 结构感知 - 充分利用Markdown结构信息")
        print("• 语义保持 - 在格式转换中保持语义完整性")
        print("• 检索优化 - 为向量检索优化的文本表示")
        
        # 清理临时文件
        import shutil
        shutil.rmtree(demo.temp_dir)
        print(f"\n🧹 清理临时文件: {demo.temp_dir}")
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()