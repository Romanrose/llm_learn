"""主程序入口"""

import sys
from orchestrator import ColumnWriterOrchestrator
from exporter import ColumnExporter
from config import get_settings


def main():
    """主函数"""
    print("\n" + "="*70)
    print("HelloAgents 专栏编写系统")
    print("="*70)
    
    # 获取配置
    settings = get_settings()
    
    # 获取主题
    if len(sys.argv) > 1:
        main_topic = " ".join(sys.argv[1:])
    else:
        print("\n请输入专栏主题（或直接回车使用默认主题）：")
        main_topic = input("> ").strip()
        if not main_topic:
            main_topic = "Python异步编程完全指南"
            print(f"使用默认主题：{main_topic}")
    
    # 选择模式
    print("\n请选择写作模式：")
    print("1. ReActAgent 模式 (默认) - 推理、行动、工具调用 + 独立评审")
    print("2. ReflectionAgent 模式 - 自我反思、自动优化（内置评审）")
    mode_choice = input("> ").strip()
    use_reflection = mode_choice == "2"
    
    # 如果选择 ReAct 模式，询问是否启用评审
    if not use_reflection:
        print("\n是否启用独立评审流程？（评审后可自动修改优化）")
        print("1. 启用评审 (默认) - 生成后评审，不合格自动修改")
        print("2. 禁用评审 - 仅生成内容，不进行评审")
        review_choice = input("> ").strip()
        if review_choice == "2":
            settings.enable_review = False
            print("▸ 已禁用评审流程")
        else:
            print(f"▸ 已启用评审流程（通过阈值: {settings.approval_threshold}分）")
    
    try:
        # 创建编排器
        orchestrator = ColumnWriterOrchestrator(use_reflection_mode=use_reflection)
        
        # 创建专栏
        result = orchestrator.create_column(main_topic)
        
        # 导出结果
        from datetime import datetime
        output_dir = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ColumnExporter.export_to_files(result, output_dir)
        
        # 打印统计
        print(f"\n{'='*70}")
        print(f"▸ 创作统计")
        print(f"{'='*70}")
        stats = result['statistics']
        print(f"文章总数: {stats['total_articles']}")
        print(f"总字数: {stats['total_words']:,}")
        print(f"平均字数: {stats['avg_words_per_article']:,}")
        
        # 显示创作统计
        if 'creation_stats' in result:
            creation = result['creation_stats']
            print(f"\n创作流程:")
            print(f"  生成次数: {creation.get('total_generations', 0)}")
            if creation.get('total_reviews', 0) > 0:
                print(f"  评审次数: {creation.get('total_reviews', 0)}")
                print(f"  一次通过: {creation.get('approved_first_try', 0)}")
            if creation.get('total_revisions', 0) > 0:
                print(f"  修改次数: {creation.get('total_revisions', 0)}")
            if creation.get('total_rewrites', 0) > 0:
                print(f"  重写次数: {creation.get('total_rewrites', 0)}")
        
        if 'agent_modes' in result:
            print(f"\nAgent 模式:")
            print(f"  Planner: {result['agent_modes']['planner']}")
            print(f"  Writer: {result['agent_modes']['writer']}")
            if result['agent_modes'].get('reviewer'):
                print(f"  Reviewer: {result['agent_modes']['reviewer']}")
            if result['agent_modes'].get('revision'):
                print(f"  Revision: {result['agent_modes']['revision']}")
        
        print(f"\n{'='*70}")
        print(f"▸ 专栏创建完成！")
        print(f"   输出目录: {output_dir}")
        print(f"{'='*70}\n")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n▸ 程序出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

