"""
数据模型模块
定义应用中使用的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """用户模型"""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True
    
    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"
    
    # TODO: 添加用户验证方法


@dataclass
class Product:
    """产品模型"""
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    
    def is_in_stock(self) -> bool:
        """检查是否有库存"""
        return self.stock > 0
    
    def apply_discount(self, percentage: float) -> float:
        """
        应用折扣
        
        Args:
            percentage: 折扣百分比
            
        Returns:
            折后价格
        """
        # TODO: 添加折扣验证
        return self.price * (1 - percentage / 100)


@dataclass
class Order:
    """订单模型"""
    id: int
    user_id: int
    products: List[Product]
    total_amount: float
    status: str
    created_at: datetime
    
    def calculate_total(self) -> float:
        """计算订单总额"""
        # TODO: 考虑折扣和税费
        return sum(p.price for p in self.products)
    
    def is_completed(self) -> bool:
        """检查订单是否完成"""
        return self.status == "completed"


@dataclass
class Transaction:
    """交易模型"""
    id: int
    order_id: int
    amount: float
    payment_method: str
    timestamp: datetime
    status: str
    
    # TODO: 添加退款功能

