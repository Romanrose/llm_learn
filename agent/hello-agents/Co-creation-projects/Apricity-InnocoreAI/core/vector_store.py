"""
InnoCore AI 向量存储管理模块
"""

import asyncio
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.models import CollectionInfo
import hashlib
import json

from .config import get_config
from .exceptions import VectorStoreException

class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self):
        self.config = get_config().vector_db
        self.client = None
        self.l1_collection = f"{self.config.collection_name_prefix}_l1_preset"
        self.l2_collection = f"{self.config.collection_name_prefix}_l2_user"
    
    async def initialize(self):
        """初始化向量数据库连接"""
        try:
            self.client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                api_key=self.config.api_key
            )
            await self._create_collections()
        except Exception as e:
            raise VectorStoreException(f"向量数据库初始化失败: {str(e)}")
    
    async def _create_collections(self):
        """创建向量集合"""
        collections = [
            (self.l1_collection, "L1预置库"),
            (self.l2_collection, "L2用户库")
        ]
        
        for collection_name, description in collections:
            try:
                self.client.get_collection(collection_name)
            except Exception:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding维度
                        distance=Distance.COSINE
                    )
                )
    
    def _generate_point_id(self, content: str) -> str:
        """生成向量点ID"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def add_to_l1(self, paper_id: str, title: str, abstract: str, 
                       content: str, metadata: Dict = None) -> str:
        """添加到L1预置库"""
        try:
            # 生成embedding (这里需要调用实际的embedding服务)
            embedding = await self._generate_embedding(f"{title} {abstract} {content}")
            
            point_id = self._generate_point_id(f"{paper_id}_l1")
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "paper_id": paper_id,
                    "title": title,
                    "abstract": abstract,
                    "content": content[:1000],  # 截取前1000字符
                    "metadata": metadata or {},
                    "collection_type": "l1",
                    "created_at": str(asyncio.get_event_loop().time())
                }
            )
            
            self.client.upsert(
                collection_name=self.l1_collection,
                points=[point]
            )
            
            return point_id
            
        except Exception as e:
            raise VectorStoreException(f"添加到L1库失败: {str(e)}")
    
    async def add_to_l2(self, user_id: str, paper_id: str, title: str, 
                       abstract: str, content: str, metadata: Dict = None) -> str:
        """添加到L2用户库"""
        try:
            embedding = await self._generate_embedding(f"{title} {abstract} {content}")
            
            point_id = self._generate_point_id(f"{user_id}_{paper_id}_l2")
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "paper_id": paper_id,
                    "title": title,
                    "abstract": abstract,
                    "content": content[:1000],
                    "metadata": metadata or {},
                    "collection_type": "l2",
                    "created_at": str(asyncio.get_event_loop().time())
                }
            )
            
            self.client.upsert(
                collection_name=self.l2_collection,
                points=[point]
            )
            
            return point_id
            
        except Exception as e:
            raise VectorStoreException(f"添加到L2库失败: {str(e)}")
    
    async def hybrid_search(self, query: str, user_id: str = None, 
                           top_k: int = 5, include_l1: bool = True,
                           include_l2: bool = True) -> List[Dict]:
        """混合搜索"""
        try:
            query_embedding = await self._generate_embedding(query)
            results = []
            
            config = get_config()
            vector_weight = config.hybrid_search_weights.get("vector", 0.7)
            keyword_weight = config.hybrid_search_weights.get("keyword", 0.3)
            
            # L1库搜索
            if include_l1:
                l1_results = self.client.search(
                    collection_name=self.l1_collection,
                    query_vector=query_embedding,
                    limit=top_k,
                    with_payload=True
                )
                
                for result in l1_results:
                    results.append({
                        "id": result.id,
                        "score": result.score * vector_weight,
                        "payload": result.payload,
                        "collection_type": "l1"
                    })
            
            # L2库搜索
            if include_l2 and user_id:
                # 构建用户过滤条件
                user_filter = Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
                
                l2_results = self.client.search(
                    collection_name=self.l2_collection,
                    query_vector=query_embedding,
                    query_filter=user_filter,
                    limit=top_k,
                    with_payload=True
                )
                
                for result in l2_results:
                    results.append({
                        "id": result.id,
                        "score": result.score * vector_weight,
                        "payload": result.payload,
                        "collection_type": "l2"
                    })
            
            # 关键词匹配加分
            for result in results:
                payload = result["payload"]
                keyword_score = self._calculate_keyword_score(
                    query, 
                    f"{payload.get('title', '')} {payload.get('abstract', '')}"
                )
                result["score"] += keyword_score * keyword_weight
            
            # 按分数排序并返回top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            raise VectorStoreException(f"混合搜索失败: {str(e)}")
    
    def _calculate_keyword_score(self, query: str, content: str) -> float:
        """计算关键词匹配分数"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本向量"""
        # 这里应该调用实际的embedding服务
        # 暂时返回随机向量作为示例
        import random
        return [random.random() for _ in range(1536)]
    
    async def get_user_vectors(self, user_id: str, limit: int = 100) -> List[Dict]:
        """获取用户的向量数据"""
        try:
            user_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
            
            results = self.client.scroll(
                collection_name=self.l2_collection,
                scroll_filter=user_filter,
                limit=limit,
                with_payload=True
            )
            
            return [
                {
                    "id": point.id,
                    "payload": point.payload
                }
                for point in results[0]
            ]
            
        except Exception as e:
            raise VectorStoreException(f"获取用户向量失败: {str(e)}")
    
    async def delete_user_vectors(self, user_id: str) -> bool:
        """删除用户的所有向量数据"""
        try:
            user_filter = Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            )
            
            self.client.delete(
                collection_name=self.l2_collection,
                points_selector=user_filter
            )
            
            return True
            
        except Exception as e:
            raise VectorStoreException(f"删除用户向量失败: {str(e)}")
    
    async def get_collection_info(self, collection_type: str = "l1") -> CollectionInfo:
        """获取集合信息"""
        collection_name = self.l1_collection if collection_type == "l1" else self.l2_collection
        return self.client.get_collection(collection_name)
    
    async def close(self):
        """关闭向量数据库连接"""
        if self.client:
            self.client.close()

# 全局向量存储管理器实例
vector_store_manager = VectorStoreManager()