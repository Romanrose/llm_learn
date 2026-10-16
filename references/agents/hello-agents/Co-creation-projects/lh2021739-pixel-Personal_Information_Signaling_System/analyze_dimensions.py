"""
维度分析主脚本 - 从报告中提取维度并修正themes
整合报告加载、维度提取、分析和themes修正建议
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# 设置控制台编码为UTF-8（Windows）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import dimension_analysis as da
import extract_dimensions as ed
import manage_themes as mt


def load_themes(themes_file: Path) -> List[str]:
    """加载themes"""
    return mt.load_themes(themes_file)


def save_themes(themes_file: Path, themes: List[str]):
    """保存themes"""
    return mt.save_themes(themes_file, themes)


def apply_theme_suggestions(suggestions: Dict[str, List[Dict]], themes: List[str], themes_file: Path, selected_indices: Dict[str, List[int]]) -> List[str]:
    """应用用户选择的themes建议
    
    Args:
        suggestions: 建议字典
        themes: 当前themes列表
        themes_file: themes文件路径
        selected_indices: 用户选择的序号字典，格式：{'add': [1, 3], 'remove': [2]}
    """
    updated_themes = themes.copy()
    
    # 处理添加建议（序号从1开始）
    add_suggestions = suggestions.get('add', [])
    for idx in selected_indices.get('add', []):
        if 1 <= idx <= len(add_suggestions):
            sug = add_suggestions[idx - 1]  # 转换为0-based索引
            theme = sug.get('theme')
            if theme and theme not in updated_themes:
                updated_themes.append(theme)
                print(f"✅ 已添加theme: {theme}")
    
    # 处理删除建议（序号从1开始）
    remove_suggestions = suggestions.get('remove', [])
    for idx in selected_indices.get('remove', []):
        if 1 <= idx <= len(remove_suggestions):
            sug = remove_suggestions[idx - 1]  # 转换为0-based索引
            theme = sug.get('theme')
            if theme and theme in updated_themes:
                updated_themes.remove(theme)
                print(f"✅ 已删除theme: {theme}")
    
    # 保存
    if updated_themes != themes:
        save_themes(themes_file, updated_themes)
        return updated_themes
    
    return themes


def present_theme_suggestions(suggestions: Dict[str, List[Dict]]):
    """展示themes建议"""
    print("\n" + "=" * 70)
    print("📋 Themes修正建议")
    print("=" * 70)
    
    all_count = sum(len(v) for k, v in suggestions.items() if k != 'theme_match_analysis')
    if all_count == 0:
        print("✅ 暂无themes修正建议")
        return
    
    # 展示添加建议
    if suggestions.get('add'):
        print("\n【添加Theme建议】")
        for i, sug in enumerate(suggestions['add'], 1):
            print(f"  {i}. {sug['theme']}")
            print(f"     原因: {sug['reason']}")
            print(f"     频率: {sug.get('frequency', 0)*100:.1f}%")
    
    # 展示删除建议
    if suggestions.get('remove'):
        print("\n【删除Theme建议】")
        for i, sug in enumerate(suggestions['remove'], 1):
            print(f"  {i}. {sug['theme']}")
            print(f"     原因: {sug['reason']}")
            print(f"     匹配率: {sug.get('match_rate', 0)*100:.1f}%")
    
    print("\n" + "=" * 70)


def get_batch_user_confirmation(add_suggestions: List[Dict], remove_suggestions: List[Dict]) -> Dict[str, List[int]]:
    """批量获取用户确认
    
    Args:
        add_suggestions: 添加建议列表
        remove_suggestions: 删除建议列表
    
    Returns:
        Dict包含 'add' 和 'remove' 两个列表，列表中是用户选择的序号（从1开始）
    """
    selected = {'add': [], 'remove': []}
    
    # 获取添加建议的确认
    if add_suggestions:
        print("\n" + "=" * 70)
        print("📥 添加Theme确认")
        print("=" * 70)
        print("请输入要添加的Theme序号（多个序号用逗号或空格分隔，如：1,3,5 或 1 3 5）")
        print("直接回车表示不添加任何Theme")
        
        while True:
            user_input = input("添加序号: ").strip()
            if not user_input:
                break
            
            # 解析输入（支持逗号或空格分隔）
            try:
                # 尝试用逗号分隔
                if ',' in user_input:
                    numbers = [int(x.strip()) for x in user_input.split(',') if x.strip()]
                else:
                    # 用空格分隔
                    numbers = [int(x.strip()) for x in user_input.split() if x.strip()]
                
                # 验证序号范围
                valid_numbers = [n for n in numbers if 1 <= n <= len(add_suggestions)]
                if len(valid_numbers) != len(numbers):
                    invalid = [n for n in numbers if n < 1 or n > len(add_suggestions)]
                    print(f"⚠️  序号 {invalid} 超出范围（1-{len(add_suggestions)}），已忽略")
                
                selected['add'] = valid_numbers
                break
            except ValueError:
                print("⚠️  输入格式错误，请输入数字序号（用逗号或空格分隔）")
    
    # 获取删除建议的确认
    if remove_suggestions:
        print("\n" + "=" * 70)
        print("📤 删除Theme确认")
        print("=" * 70)
        print("请输入要删除的Theme序号（多个序号用逗号或空格分隔，如：1,2 或 1 2）")
        print("直接回车表示不删除任何Theme")
        
        while True:
            user_input = input("删除序号: ").strip()
            if not user_input:
                break
            
            # 解析输入（支持逗号或空格分隔）
            try:
                # 尝试用逗号分隔
                if ',' in user_input:
                    numbers = [int(x.strip()) for x in user_input.split(',') if x.strip()]
                else:
                    # 用空格分隔
                    numbers = [int(x.strip()) for x in user_input.split() if x.strip()]
                
                # 验证序号范围
                valid_numbers = [n for n in numbers if 1 <= n <= len(remove_suggestions)]
                if len(valid_numbers) != len(numbers):
                    invalid = [n for n in numbers if n < 1 or n > len(remove_suggestions)]
                    print(f"⚠️  序号 {invalid} 超出范围（1-{len(remove_suggestions)}），已忽略")
                
                selected['remove'] = valid_numbers
                break
            except ValueError:
                print("⚠️  输入格式错误，请输入数字序号（用逗号或空格分隔）")
    
    return selected


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="维度分析工具 - 从报告中提取维度并修正themes")
    parser.add_argument(
        "--extract",
        action="store_true",
        help="重新提取维度（从报告文件中）"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互模式：展示建议并获取用户确认"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="基础目录路径（默认为脚本所在目录）"
    )
    args = parser.parse_args()
    
    # 确定基础目录
    if args.base_dir:
        base_dir = Path(args.base_dir)
    else:
        base_dir = Path(__file__).parent
    
    print("=" * 70)
    print("维度分析工具 - 从报告中提取维度并修正themes")
    print("=" * 70)
    
    # 1. 加载或提取维度
    print("\n📊 正在处理维度提取结果...")
    
    extraction_results = []
    
    if args.extract:
        # 重新提取维度
        print("🔄 从报告文件中提取维度...")
        llm = ed.init_llm()
        if not llm:
            print("❌ LLM未初始化，无法提取维度")
            return
        
        # 加载themes作为参考
        themes_file = base_dir / "themes.yaml"
        existing_themes = mt.load_themes(themes_file)
        
        extraction_results = ed.batch_extract_dimensions(base_dir, report_type=None, llm=llm, existing_themes=existing_themes)
        print(f"✅ 从报告中提取了 {len(extraction_results)} 个维度的提取结果")
    else:
        # 加载已有的提取结果
        extraction_results = ed.load_extraction_results(base_dir)
        print(f"✅ 加载了 {len(extraction_results)} 个提取结果")
        
        if len(extraction_results) == 0:
            print("⚠️  未找到提取结果，使用 --extract 参数可以重新提取")
            print("💡 提示: 运行 'python extract_dimensions.py' 来提取维度")
    
    if len(extraction_results) == 0:
        print("❌ 没有维度提取结果，无法进行分析")
        return
    
    # 2. 加载themes
    themes_file = base_dir / "themes.yaml"
    themes = load_themes(themes_file)
    
    if not themes:
        print("⚠️  当前没有themes，请先设置themes")
        print("💡 提示: 运行 'python manage_themes.py' 来管理themes")
        # 使用空列表继续，以便生成添加建议
    
    print(f"📋 当前themes: {themes}")
    
    # 3. 统计维度
    dim_stats = da.count_dimension_frequency_from_extractions(extraction_results)
    print(f"\n📈 维度统计: 发现 {len(dim_stats)} 个不同维度")
    if dim_stats:
        print("   维度频率（Top 5）:")
        sorted_dims = sorted(dim_stats.items(), key=lambda x: x[1]['frequency'], reverse=True)[:5]
        for dim, stats in sorted_dims:
            print(f"   - {dim}: {stats['frequency']}次 ({stats['frequency_rate']*100:.1f}%)")
    
    # 4. 生成themes修正建议
    print("\n💡 正在生成themes修正建议...")
    suggestions = da.generate_theme_suggestions(extraction_results, themes)
    
    total_suggestions = len(suggestions.get('add', [])) + len(suggestions.get('remove', []))
    print(f"✅ 生成 {total_suggestions} 条themes修正建议")
    
    # 5. 生成分析报告
    today = datetime.now().strftime("%Y-%m-%d")
    
    analysis_report = {
        "analysis_date": today,
        "total_extractions": len(extraction_results),
        "dimension_statistics": dim_stats,
        "current_themes": themes,
        "theme_suggestions": {
            "add": suggestions.get('add', []),
            "remove": suggestions.get('remove', [])
        },
        "theme_match_analysis": suggestions.get('theme_match_analysis', {})
    }
    
    # 6. 保存分析报告
    analysis_dir = base_dir / "archive" / "dimension_analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    analysis_file = analysis_dir / f"{today}_analysis.json"
    
    try:
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 分析报告已保存到: {analysis_file}")
    except Exception as e:
        print(f"❌ 保存分析报告失败: {e}")
    
    # 7. 交互模式：展示建议并获取用户确认
    if args.interactive and total_suggestions > 0:
        present_theme_suggestions(suggestions)
        
        # 批量获取用户确认
        add_suggestions = suggestions.get('add', [])
        remove_suggestions = suggestions.get('remove', [])
        selected_indices = get_batch_user_confirmation(add_suggestions, remove_suggestions)
        
        # 应用用户选择的建议
        updated_themes = apply_theme_suggestions(suggestions, themes, themes_file, selected_indices)
        
        if updated_themes != themes:
            print(f"\n✅ Themes已更新: {updated_themes}")
        else:
            print("\n✅ 未应用任何更改")
    elif total_suggestions > 0:
        # 非交互模式，只展示建议
        present_theme_suggestions(suggestions)
        print("\n💡 提示: 使用 --interactive 参数可以查看并处理建议")
    
    print("\n✅ 分析完成！")


if __name__ == "__main__":
    main()
