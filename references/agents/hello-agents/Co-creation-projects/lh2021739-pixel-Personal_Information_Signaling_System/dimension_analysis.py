"""
维度分析模块 - V1 简化版
提供维度数据的收集、分析、建议生成和用户交互功能
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict

# 设置控制台编码为UTF-8（Windows）
# 注意：只在作为主脚本运行时重定向，避免在被导入时冲突
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# ==================== 数据收集功能 ====================

def collect_daily_records(archive_dir: Path) -> List[Dict]:
    """从 archive/youtube/ 目录读取所有日报 JSON"""
    records = []
    if not archive_dir.exists():
        return records
    
    for json_file in archive_dir.glob("*.json"):
        # 跳过 research 报告
        if json_file.name.endswith("_research.json"):
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保有 dimensions 字段（向后兼容）
                if 'dimensions' not in data:
                    data['dimensions'] = []
                records.append(data)
        except Exception as e:
            print(f"⚠️  读取文件失败 {json_file.name}: {e}")
    
    return records


def collect_weekly_records(weekly_dir: Path) -> List[Dict]:
    """从指定目录读取周报 JSON"""
    records = []
    if not weekly_dir.exists():
        return records
    
    for json_file in weekly_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'dimensions' not in data:
                    data['dimensions'] = []
                records.append(data)
        except Exception as e:
            print(f"⚠️  读取周报文件失败 {json_file.name}: {e}")
    
    return records


def collect_monthly_records(monthly_dir: Path) -> List[Dict]:
    """从指定目录读取月报 JSON"""
    records = []
    if not monthly_dir.exists():
        return records
    
    for json_file in monthly_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'dimensions' not in data:
                    data['dimensions'] = []
                records.append(data)
        except Exception as e:
            print(f"⚠️  读取月报文件失败 {json_file.name}: {e}")
    
    return records


def load_all_records(base_dir: Path) -> Dict[str, List[Dict]]:
    """统一加载所有类型的记录"""
    archive_dir = base_dir / "archive" / "youtube"
    weekly_dir = base_dir / "archive" / "weekly"
    monthly_dir = base_dir / "archive" / "monthly"
    
    return {
        "daily": collect_daily_records(archive_dir),
        "weekly": collect_weekly_records(weekly_dir),
        "monthly": collect_monthly_records(monthly_dir)
    }


# ==================== 维度分析功能 ====================

def parse_date(date_str: str) -> Optional[datetime]:
    """解析日期字符串为 datetime 对象"""
    try:
        # 支持多种日期格式
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def count_dimension_frequency(records: List[Dict]) -> Dict[str, Dict]:
    """统计每个维度的出现频率"""
    dimension_stats = defaultdict(lambda: {
        'frequency': 0,
        'dates': [],
        'first_seen': None,
        'last_seen': None
    })
    
    total_records = len(records)
    
    for record in records:
        date_str = record.get('date', '')
        dimensions = record.get('dimensions', [])
        
        if not dimensions:
            continue
        
        record_date = parse_date(date_str)
        
        for dim in dimensions:
            if dim:  # 跳过空字符串
                dimension_stats[dim]['frequency'] += 1
                if record_date:
                    dimension_stats[dim]['dates'].append(record_date)
                    if dimension_stats[dim]['first_seen'] is None or record_date < dimension_stats[dim]['first_seen']:
                        dimension_stats[dim]['first_seen'] = record_date
                    if dimension_stats[dim]['last_seen'] is None or record_date > dimension_stats[dim]['last_seen']:
                        dimension_stats[dim]['last_seen'] = record_date
    
    # 计算频率率和格式化日期
    result = {}
    for dim, stats in dimension_stats.items():
        result[dim] = {
            'frequency': stats['frequency'],
            'frequency_rate': stats['frequency'] / total_records if total_records > 0 else 0.0,
            'first_seen': stats['first_seen'].strftime("%Y-%m-%d") if stats['first_seen'] else None,
            'last_seen': stats['last_seen'].strftime("%Y-%m-%d") if stats['last_seen'] else None,
            'dates': [d.strftime("%Y-%m-%d") for d in stats['dates']]
        }
    
    return result


def find_missing_dimensions(records: List[Dict], candidate_dimensions: List[str], days_threshold: int = 30) -> List[str]:
    """查找缺失的维度（超过N天未出现）"""
    now = datetime.now()
    missing = []
    
    for dim in candidate_dimensions:
        # 查找该维度最后一次出现的时间
        last_seen = None
        for record in records:
            dimensions = record.get('dimensions', [])
            if dim in dimensions:
                date_str = record.get('date', '')
                record_date = parse_date(date_str)
                if record_date and (last_seen is None or record_date > last_seen):
                    last_seen = record_date
        
        # 如果从未出现或超过阈值天数，加入缺失列表
        if last_seen is None:
            missing.append(dim)
        else:
            days_diff = (now - last_seen).days
            if days_diff > days_threshold:
                missing.append(dim)
    
    return missing


# ==================== 优先级计算功能 ====================

def calculate_dimension_priority(records: List[Dict]) -> Dict[str, float]:
    """计算维度优先级分数（仅基于出现频率）"""
    stats = count_dimension_frequency(records)
    priorities = {}
    
    for dim, dim_stats in stats.items():
        priorities[dim] = dim_stats['frequency_rate']
    
    return priorities


# ==================== 建议生成功能 ====================

def suggest_add_dimensions(records: List[Dict], candidate_dimensions: List[str], threshold_days: int = 30) -> List[Dict]:
    """建议添加缺失但重要的维度"""
    missing = find_missing_dimensions(records, candidate_dimensions, threshold_days)
    suggestions = []
    
    for dim in missing:
        # 计算建议的优先级（如果该维度曾经出现过，使用历史频率；否则使用默认值 0.5）
        stats = count_dimension_frequency(records)
        suggested_priority = stats.get(dim, {}).get('frequency_rate', 0.5)
        
        suggestions.append({
            "suggestion_id": f"add_{dim}_{datetime.now().strftime('%Y%m%d')}",
            "type": "add",
            "dimension": dim,
            "reason": f"已有{threshold_days}天未在记录中出现，但候选维度列表中",
            "recommendation": "建议添加该维度",
            "suggested_priority": round(suggested_priority, 2)
        })
    
    return suggestions


def suggest_remove_dimensions(records: List[Dict], active_dimensions: List[str], threshold_days: int = 60) -> List[Dict]:
    """建议删除长期未出现的维度"""
    stats = count_dimension_frequency(records)
    suggestions = []
    
    now = datetime.now()
    
    for dim in active_dimensions:
        dim_stat = stats.get(dim, {})
        last_seen_str = dim_stat.get('last_seen')
        
        if not last_seen_str:
            # 从未出现过
            suggestions.append({
                "suggestion_id": f"remove_{dim}_{datetime.now().strftime('%Y%m%d')}",
                "type": "remove",
                "dimension": dim,
                "reason": "从未在记录中出现",
                "recommendation": "建议删除该维度"
            })
        else:
            last_seen = parse_date(last_seen_str)
            if last_seen:
                days_diff = (now - last_seen).days
                if days_diff > threshold_days:
                    suggestions.append({
                        "suggestion_id": f"remove_{dim}_{datetime.now().strftime('%Y%m%d')}",
                        "type": "remove",
                        "dimension": dim,
                        "reason": f"已有{days_diff}天未在记录中出现",
                        "recommendation": "建议删除该维度"
                    })
    
    return suggestions


def suggest_priority_adjustment(records: List[Dict], dimension_config: Dict) -> List[Dict]:
    """建议调整频繁出现维度的优先级"""
    stats = count_dimension_frequency(records)
    priorities = calculate_dimension_priority(records)
    suggestions = []
    
    active_dimensions = dimension_config.get('active_dimensions', [])
    
    for dim_info in active_dimensions:
        dim_name = dim_info.get('name')
        current_priority = dim_info.get('priority', 0.0)
        dim_stat = stats.get(dim_name, {})
        frequency_rate = dim_stat.get('frequency_rate', 0.0)
        
        # 如果频率 > 70% 且当前优先级 < 频率，建议提升
        if frequency_rate > 0.7 and current_priority < frequency_rate:
            suggestions.append({
                "suggestion_id": f"priority_{dim_name}_{datetime.now().strftime('%Y%m%d')}",
                "type": "priority_adjustment",
                "dimension": dim_name,
                "reason": f"最近出现频率达{frequency_rate*100:.1f}%，但当前优先级仅为{current_priority:.2f}",
                "current_priority": current_priority,
                "suggested_priority": round(frequency_rate, 2),
                "recommendation": "建议提高该维度的优先级"
            })
    
    return suggestions


def generate_all_suggestions(records: List[Dict], dimension_config: Dict) -> Dict[str, List[Dict]]:
    """生成所有建议的综合报告"""
    all_records = records
    
    # 获取当前配置
    active_dimensions = [d['name'] for d in dimension_config.get('active_dimensions', [])]
    candidate_dimensions = dimension_config.get('candidate_dimensions', [])
    
    # 生成各类建议
    add_suggestions = suggest_add_dimensions(all_records, candidate_dimensions, threshold_days=30)
    remove_suggestions = suggest_remove_dimensions(all_records, active_dimensions, threshold_days=60)
    priority_suggestions = suggest_priority_adjustment(all_records, dimension_config)
    
    return {
        "add": add_suggestions,
        "remove": remove_suggestions,
        "priority_adjustment": priority_suggestions
    }


# ==================== 维度与Themes对比功能 ====================

def count_dimension_frequency_from_extractions(extraction_results: List[Dict]) -> Dict[str, Dict]:
    """从提取结果中统计维度频率"""
    dimension_stats = defaultdict(lambda: {
        'frequency': 0,
        'dates': [],
        'first_seen': None,
        'last_seen': None
    })
    
    total_extractions = len(extraction_results)
    
    for result in extraction_results:
        dimensions = result.get('dimensions', [])
        extraction_date_str = result.get('extraction_date', result.get('report_date', ''))
        extraction_date = parse_date(extraction_date_str.split('T')[0])  # 只取日期部分
        
        for dim in dimensions:
            if dim:
                dimension_stats[dim]['frequency'] += 1
                if extraction_date:
                    dimension_stats[dim]['dates'].append(extraction_date)
                    if dimension_stats[dim]['first_seen'] is None or extraction_date < dimension_stats[dim]['first_seen']:
                        dimension_stats[dim]['first_seen'] = extraction_date
                    if dimension_stats[dim]['last_seen'] is None or extraction_date > dimension_stats[dim]['last_seen']:
                        dimension_stats[dim]['last_seen'] = extraction_date
    
    # 计算频率率和格式化日期
    result = {}
    for dim, stats in dimension_stats.items():
        result[dim] = {
            'frequency': stats['frequency'],
            'frequency_rate': stats['frequency'] / total_extractions if total_extractions > 0 else 0.0,
            'first_seen': stats['first_seen'].strftime("%Y-%m-%d") if stats['first_seen'] else None,
            'last_seen': stats['last_seen'].strftime("%Y-%m-%d") if stats['last_seen'] else None,
        }
    
    return result


def analyze_theme_dimension_match(themes: List[str], extraction_results: List[Dict], days_window: int = 30) -> Dict[str, Dict]:
    """分析themes与维度的匹配度"""
    now = datetime.now()
    
    # 统计维度频率
    dim_stats = count_dimension_frequency_from_extractions(extraction_results)
    
    # 过滤最近N天的提取结果
    recent_results = []
    for result in extraction_results:
        extraction_date_str = result.get('extraction_date', result.get('report_date', ''))
        extraction_date = parse_date(extraction_date_str.split('T')[0])
        if extraction_date:
            days_diff = (now - extraction_date).days
            if days_diff <= days_window:
                recent_results.append(result)
    
    # 统计最近N天内的维度
    recent_dim_stats = count_dimension_frequency_from_extractions(recent_results)
    
    theme_match = {}
    
    for theme in themes:
        # 计算theme在提取维度中的匹配情况
        match_count = 0
        total_count = len(recent_results)
        
        for result in recent_results:
            dimensions = result.get('dimensions', [])
            # 简单匹配：theme是否在维度列表中（可以考虑更复杂的相似度匹配）
            if theme in dimensions:
                match_count += 1
        
        match_rate = match_count / total_count if total_count > 0 else 0.0
        
        # 计算最近一次匹配的时间
        last_match_date = None
        for result in recent_results:
            dimensions = result.get('dimensions', [])
            if theme in dimensions:
                extraction_date_str = result.get('extraction_date', result.get('report_date', ''))
                extraction_date = parse_date(extraction_date_str.split('T')[0])
                if extraction_date:
                    if last_match_date is None or extraction_date > last_match_date:
                        last_match_date = extraction_date
        
        theme_match[theme] = {
            'match_rate': match_rate,
            'match_count': match_count,
            'total_count': total_count,
            'last_match_date': last_match_date.strftime("%Y-%m-%d") if last_match_date else None,
            'days_without_match': (now - last_match_date).days if last_match_date else days_window
        }
    
    return theme_match


def suggest_add_themes(dim_stats: Dict[str, Dict], themes: List[str], threshold_frequency: float = 0.5, min_recent_count: int = 3, days_window: int = 30) -> List[Dict]:
    """建议添加新themes（维度中出现但themes中没有的）"""
    suggestions = []
    now = datetime.now()
    
    for dim, stats in dim_stats.items():
        # 如果维度不在themes中
        if dim not in themes:
            frequency_rate = stats.get('frequency_rate', 0.0)
            last_seen_str = stats.get('last_seen')
            
            # 检查最近出现次数
            recent_count = 0
            if last_seen_str:
                last_seen = parse_date(last_seen_str)
                if last_seen:
                    days_diff = (now - last_seen).days
                    if days_diff <= days_window:
                        # 估算最近出现次数（简化：假设频率一致）
                        recent_count = int(frequency_rate * (days_window / 7))  # 粗略估算
            
            # 如果频率达到阈值且最近有出现
            if frequency_rate >= threshold_frequency and recent_count >= min_recent_count:
                suggestions.append({
                    "suggestion_id": f"add_theme_{dim}_{datetime.now().strftime('%Y%m%d')}",
                    "type": "add_theme",
                    "theme": dim,
                    "reason": f"从报告中提取的维度'{dim}'出现频率{frequency_rate*100:.1f}%，最近{days_window}天出现{recent_count}次",
                    "source_dimensions": [dim],
                    "frequency": frequency_rate,
                    "recent_count": recent_count
                })
    
    return suggestions


def suggest_remove_themes(theme_match: Dict[str, Dict], threshold_frequency: float = 0.1, min_days: int = 60) -> List[Dict]:
    """建议删除themes（长期与维度不匹配的）"""
    suggestions = []
    
    for theme, match_info in theme_match.items():
        match_rate = match_info.get('match_rate', 0.0)
        days_without_match = match_info.get('days_without_match', 0)
        
        # 如果匹配率低于阈值且持续时间超过阈值
        if match_rate < threshold_frequency and days_without_match >= min_days:
            suggestions.append({
                "suggestion_id": f"remove_theme_{theme}_{datetime.now().strftime('%Y%m%d')}",
                "type": "remove_theme",
                "theme": theme,
                "reason": f"过去{min_days}天内，'{theme}'在提取维度中的匹配率仅{match_rate*100:.1f}%，且已有{days_without_match}天未匹配",
                "match_rate": match_rate,
                "days_without_match": days_without_match
            })
    
    return suggestions


def generate_theme_suggestions(extraction_results: List[Dict], themes: List[str]) -> Dict[str, List[Dict]]:
    """生成themes修正建议"""
    # 统计维度频率
    dim_stats = count_dimension_frequency_from_extractions(extraction_results)
    
    # 分析themes匹配度（使用30天窗口）
    theme_match = analyze_theme_dimension_match(themes, extraction_results, days_window=30)
    
    # 生成建议
    add_suggestions = suggest_add_themes(dim_stats, themes, threshold_frequency=0.5, min_recent_count=3, days_window=30)
    remove_suggestions = suggest_remove_themes(theme_match, threshold_frequency=0.1, min_days=60)
    
    return {
        "add": add_suggestions,
        "remove": remove_suggestions,
        "theme_match_analysis": theme_match
    }


# ==================== 配置文件管理 ====================

def load_dimension_config(config_file: Path) -> Dict:
    """加载维度配置文件"""
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {e}")
    
    # 返回默认配置
    return {
        "active_dimensions": [],
        "candidate_dimensions": [],
        "removed_dimensions": []
    }


def save_dimension_config(config_file: Path, config: Dict):
    """保存维度配置文件"""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_dimension_history(history_file: Path) -> List[Dict]:
    """加载维度历史记录"""
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('history', [])
        except Exception as e:
            print(f"⚠️  加载历史记录失败: {e}")
    
    return []


def save_dimension_history(history_file: Path, history: List[Dict]):
    """保存维度历史记录"""
    history_file.parent.mkdir(parents=True, exist_ok=True)
    data = {"history": history}
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_dimension_event(event_type: str, dimension: str, timestamp: str = None, metadata: Dict = None) -> Dict:
    """记录维度事件（ADD/REMOVE/PRIORITY_CHANGE）"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d")
    
    event = {
        "date": timestamp,
        "event": event_type,
        "dimension": dimension
    }
    
    if metadata:
        event.update(metadata)
    
    return event


# ==================== 用户交互功能 ====================

def present_suggestions(suggestions: Dict[str, List[Dict]]) -> None:
    """展示系统建议给用户（简单文本）"""
    print("\n" + "=" * 70)
    print("📋 维度调整建议")
    print("=" * 70)
    
    all_count = sum(len(v) for v in suggestions.values())
    if all_count == 0:
        print("✅ 暂无建议")
        return
    
    # 展示新增建议
    if suggestions.get('add'):
        print("\n【新增维度建议】")
        for i, sug in enumerate(suggestions['add'], 1):
            print(f"  {i}. {sug['dimension']}")
            print(f"     原因: {sug['reason']}")
            print(f"     建议优先级: {sug['suggested_priority']}")
    
    # 展示删除建议
    if suggestions.get('remove'):
        print("\n【删除维度建议】")
        for i, sug in enumerate(suggestions['remove'], 1):
            print(f"  {i}. {sug['dimension']}")
            print(f"     原因: {sug['reason']}")
    
    # 展示优先级调整建议
    if suggestions.get('priority_adjustment'):
        print("\n【优先级调整建议】")
        for i, sug in enumerate(suggestions['priority_adjustment'], 1):
            print(f"  {i}. {sug['dimension']}")
            print(f"     原因: {sug['reason']}")
            print(f"     当前优先级: {sug['current_priority']:.2f} → 建议: {sug['suggested_priority']:.2f}")
    
    print("\n" + "=" * 70)


def get_user_confirmation(suggestion: Dict) -> str:
    """获取用户确认（接受/拒绝，简单输入）"""
    print(f"\n建议: {suggestion['recommendation']}")
    print(f"维度: {suggestion['dimension']}")
    print(f"原因: {suggestion['reason']}")
    
    while True:
        user_input = input("接受 (y) / 拒绝 (n): ").strip().lower()
        if user_input in ['y', 'yes', '是', '接受']:
            return 'accepted'
        elif user_input in ['n', 'no', '否', '拒绝']:
            return 'rejected'
        else:
            print("⚠️  请输入 y 或 n")


def format_history_text(history: List[Dict]) -> str:
    """格式化历史记录为简单文本"""
    if not history:
        return "暂无历史记录"
    
    lines = ["维度演化历史:"]
    lines.append("-" * 70)
    
    for event in history:
        date = event.get('date', '')
        event_type = event.get('event', '')
        dimension = event.get('dimension', '')
        
        if event_type == "ADD":
            info = f"新增维度"
        elif event_type == "REMOVE":
            info = f"删除维度"
        elif event_type == "PRIORITY_CHANGE":
            old_priority = event.get('old_priority', '')
            new_priority = event.get('new_priority', '')
            info = f"优先级调整: {old_priority} → {new_priority}"
        else:
            info = event_type
        
        lines.append(f"{date} | {event_type} | {dimension} | {info}")
    
    return "\n".join(lines)

