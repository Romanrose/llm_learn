# data_exploration.py
import os
import numpy as np
import pandas as pd
from hello_agents import ToolRegistry

# 读取数据集
work_path = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(f"{work_path}/../data/shopping_behavior_updated.csv")

def get_basic_metadata(input: str) -> dict:
    """获取基本元数据"""
    metadata = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum()
    }
    return metadata

def assess_data_quality(input: str) -> dict:
    """综合数据质量评估"""
    quality_report = {
        "completeness": {},
        "consistency": {},
        "validity": {},
        "anomalies": {}
    }

    for col in df.columns:
        # 完整性
        missing_rate = df[col].isna().mean()
        quality_report["completeness"][col] = {
            "missing_rate": missing_rate,
            "level": "high" if missing_rate < 0.05 else "medium" if missing_rate < 0.2 else "low"
        }

        # 有效性（基于数据类型）
        if pd.api.types.is_numeric_dtype(df[col]):
            # 数值型检查
            quality_report["anomalies"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max())
            }
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            # 时间型检查
            future_dates = df[col] > pd.Timestamp.now()
            quality_report["validity"][col] = {
                "future_dates_count": future_dates.sum(),
                "date_range": [df[col].min().strftime('%Y-%m-%d'),
                              df[col].max().strftime('%Y-%m-%d')]
            }

    return quality_report

def get_statistical_summary(input: str) -> dict:
    """核心数据统计摘要"""
    summary = {}

    for col in df.select_dtypes(include=[np.number]).columns:
        series = df[col].dropna()
        summary[col] = {
            "basic": {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "25%": float(series.quantile(0.25)),
                "50%": float(series.quantile(0.50)),
                "75%": float(series.quantile(0.75)),
                "max": float(series.max())
            },
            "advanced": {
                "skewness": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
                "cv": float(series.std() / series.mean()) if series.mean() != 0 else None,
                "zeros_count": int((series == 0).sum()),
                "negative_count": int((series < 0).sum())
            }
        }

    return summary

def create_data_exploration_registry():
    """创建包含数据探查工具的注册表"""
    registry = ToolRegistry()

    # 注册获取基本元数据函数
    registry.register_function(
        name="get_basic_metadata",
        description="获取基本元数据，包括形状、列名、数据类型和内存使用情况",
        func=get_basic_metadata
    )

    # 注册数据质量评估函数
    registry.register_function(
        name="assess_data_quality",
        description="综合评估数据质量，包括完整性、一致性、有效性和异常检测",
        func=assess_data_quality
    )

    # 注册统计摘要函数
    registry.register_function(
        name="get_statistical_summary",
        description="获取数值型列的核心统计摘要，包括基本统计量和高级统计量",
        func=get_statistical_summary
    )

    return registry

if __name__ == "__main__":
    registry = create_data_exploration_registry()
    result = registry.execute_tool("get_basic_metadata", input_text=None)
    print(result)
