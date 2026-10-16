"""
InnoCore AI 向量生成工具
"""

import asyncio
from typing import List, Dict, Optional, Any
import numpy as np
from openai import AsyncOpenAI
import hashlib
import json

from ..core.config import get_config
from ..core.exceptions import AgentException

class EmbeddingGenerator:
    """向量生成器"""
    
    def __init__(self):
        self.config = get_config()
        self.client = None
        self.embedding_model = self.config.vector_db.embedding_model
        self.cache = {}  # 简单的内存缓存
    
    async def initialize(self):
        """初始化向量生成器"""
        try:
            self.client = AsyncOpenAI(
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url
            )
        except Exception as e:
            raise AgentException(f"向量生成器初始化失败: {str(e)}")
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """生成文本向量"""
        if not text:
            return [0.0] * 1536  # 返回零向量
        
        # 检查缓存
        if use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        try:
            # 清理文本
            cleaned_text = self._clean_text(text)
            
            # 调用OpenAI API
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=cleaned_text
            )
            
            embedding = response.data[0].embedding
            
            # 缓存结果
            if use_cache:
                cache_key = self._get_cache_key(text)
                self.cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            raise AgentException(f"向量生成失败: {str(e)}")
    
    async def generate_batch_embeddings(self, texts: List[str], 
                                       batch_size: int = 10) -> List[List[float]]:
        """批量生成向量"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # 批量调用API
                cleaned_texts = [self._clean_text(text) for text in batch]
                
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=cleaned_texts
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                # 如果批量失败，逐个生成
                for text in batch:
                    try:
                        embedding = await self.generate_embedding(text)
                        embeddings.append(embedding)
                    except Exception as single_error:
                        print(f"单个向量生成失败: {str(single_error)}")
                        embeddings.append([0.0] * 1536)  # 零向量
        
        return embeddings
    
    async def generate_paper_embedding(self, paper_info: Dict[str, Any]) -> List[float]:
        """为论文生成综合向量"""
        # 组合论文的关键信息
        title = paper_info.get("title", "")
        abstract = paper_info.get("abstract", "")
        authors = " ".join(paper_info.get("authors", []))
        
        # 构建综合文本
        combined_text = f"{title} {abstract} {authors}"
        
        # 如果有结构化内容，也包含进来
        sections = paper_info.get("sections", {})
        if sections:
            section_text = " ".join(sections.values())
            combined_text += " " + section_text
        
        return await self.generate_embedding(combined_text)
    
    async def generate_section_embeddings(self, sections: Dict[str, str]) -> Dict[str, List[float]]:
        """为各个章节生成向量"""
        section_embeddings = {}
        
        for section_name, section_content in sections.items():
            if section_content.strip():
                try:
                    embedding = await self.generate_embedding(section_content)
                    section_embeddings[section_name] = embedding
                except Exception as e:
                    print(f"章节 {section_name} 向量生成失败: {str(e)}")
                    section_embeddings[section_name] = [0.0] * 1536
        
        return section_embeddings
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        # 截断过长的文本（OpenAI有token限制）
        max_length = 8000  # 保守估计
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        try:
            embedding1 = await self.generate_embedding(text1)
            embedding2 = await self.generate_embedding(text2)
            
            return self._cosine_similarity(embedding1, embedding2)
            
        except Exception as e:
            print(f"相似度计算失败: {str(e)}")
            return 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vec1) != len(vec2):
            return 0.0
        
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    async def find_most_similar(self, query_text: str, 
                               candidate_texts: List[str],
                               top_k: int = 5) -> List[Dict[str, Any]]:
        """找到最相似的文本"""
        if not candidate_texts:
            return []
        
        try:
            # 生成查询向量
            query_embedding = await self.generate_embedding(query_text)
            
            # 生成候选文本向量
            candidate_embeddings = await self.generate_batch_embeddings(candidate_texts)
            
            # 计算相似度
            similarities = []
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = self._cosine_similarity(query_embedding, candidate_embedding)
                similarities.append({
                    "text": candidate_texts[i],
                    "similarity": similarity,
                    "index": i
                })
            
            # 按相似度排序
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            print(f"相似文本查找失败: {str(e)}")
            return []
    
    async def cluster_texts(self, texts: List[str], 
                          num_clusters: int = 3) -> Dict[str, Any]:
        """文本聚类（简化实现）"""
        try:
            # 生成所有文本的向量
            embeddings = await self.generate_batch_embeddings(texts)
            
            # 简单的聚类逻辑（基于相似度阈值）
            clusters = {}
            cluster_id = 0
            used_indices = set()
            
            for i, embedding in enumerate(embeddings):
                if i in used_indices:
                    continue
                
                # 创建新聚类
                clusters[f"cluster_{cluster_id}"] = {
                    "texts": [texts[i]],
                    "indices": [i],
                    "center": embedding
                }
                used_indices.add(i)
                
                # 查找相似文本加入同一聚类
                for j, other_embedding in enumerate(embeddings):
                    if j in used_indices:
                        continue
                    
                    similarity = self._cosine_similarity(embedding, other_embedding)
                    if similarity > 0.8:  # 相似度阈值
                        clusters[f"cluster_{cluster_id}"]["texts"].append(texts[j])
                        clusters[f"cluster_{cluster_id}"]["indices"].append(j)
                        used_indices.add(j)
                
                cluster_id += 1
            
            return {
                "clusters": clusters,
                "num_clusters": len(clusters),
                "total_texts": len(texts)
            }
            
        except Exception as e:
            print(f"文本聚类失败: {str(e)}")
            return {"clusters": {}, "num_clusters": 0, "total_texts": len(texts)}
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词（基于TF-IDF的简化实现）"""
        try:
            # 分词
            words = text.lower().split()
            
            # 过滤停用词（简化版）
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # 计算词频
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # 按频率排序
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            # 返回前N个关键词
            return [word for word, freq in sorted_words[:max_keywords]]
            
        except Exception as e:
            print(f"关键词提取失败: {str(e)}")
            return []
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """获取向量生成器信息"""
        return {
            "model": self.embedding_model,
            "cache_size": len(self.cache),
            "vector_dimension": 1536,  # OpenAI embedding维度
            "provider": "openai"
        }