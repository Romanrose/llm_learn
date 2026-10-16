"""
TerminalTool 使用示例

展示 TerminalTool 的典型使用模式：
1. 探索式导航
2. 数据文件分析
3. 日志文件分析
4. 代码库分析
"""

import os
from pathlib import Path
from hello_agents.tools import TerminalTool

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()


def demo_exploratory_navigation():
    """演示探索式导航"""
    print("\n" + "=" * 80)
    print("场景1: 探索式导航")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR))

    # 第一步:查看当前目录
    print("1. 查看当前目录:")
    result = terminal.run({"command": "ls -la"})
    print(result)

    # 第二步:查看Python文件
    print("\n2. 查看Python文件:")
    result = terminal.run({"command": "ls -la *.py"})
    print(result)

    # 第三步:查找特定文件
    print("\n3. 查找特定模式的文件:")
    result = terminal.run({"command": "find . -name '*codebase_maintainer.py'"})
    print(result)

    # 第四步:查看文件内容
    print("\n4. 查看文件内容:")
    result = terminal.run({"command": "head -n 20 codebase_maintainer.py"})
    print(result)


def demo_data_file_analysis():
    """演示数据文件分析"""
    print("\n" + "=" * 80)
    print("场景2: 数据文件分析")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "data"))

    # 查看 CSV 文件的前几行
    print("1. 查看 CSV 文件前5行:")
    result = terminal.run({"command": "head -n 5 sales_2024.csv"})
    print(result)

    # 统计总行数
    print("\n2. 统计文件行数:")
    result = terminal.run({"command": "wc -l *.csv"})
    print(result)

    # 提取和统计产品类别
    print("\n3. 统计产品类别分布:")
    result = terminal.run({"command": "tail -n +2 sales_2024.csv | cut -d',' -f3 | sort | uniq -c"})
    print(result)


def demo_log_analysis():
    """演示日志文件分析"""
    print("\n" + "=" * 80)
    print("场景3: 日志文件分析")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "logs"))

    # 查看最新的错误日志
    print("1. 查看最新的错误日志:")
    result = terminal.run({"command": "tail -n 50 app.log | grep ERROR"})
    print(result)

    # 统计错误类型分布
    print("\n2. 统计错误类型分布:")
    result = terminal.run({"command": "grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn"})
    print(result)

    # 查找特定时间段的日志
    print("\n3. 查找特定时间段的日志:")
    result = terminal.run({"command": "grep '2024-01-19 15:' app.log | tail -n 20"})
    print(result)


def demo_codebase_analysis():
    """演示代码库分析"""
    print("\n" + "=" * 80)
    print("场景4: 代码库分析")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "codebase"))

    # 统计代码行数
    print("1. 统计代码行数:")
    result = terminal.run({"command": "find . -name '*.py' -exec wc -l {} + | tail -n 1"})
    print(result)

    # 查找所有 TODO 注释
    print("\n2. 查找所有 TODO 注释:")
    result = terminal.run({"command": "grep -rn 'TODO' --include='*.py'"})
    print(result)

    # 查找特定函数的定义
    print("\n3. 查找特定函数的定义:")
    result = terminal.run({"command": "grep -rn 'def process_data' --include='*.py'"})
    print(result)


def demo_security_features():
    """演示安全特性"""
    print("\n" + "=" * 80)
    print("安全特性演示")
    print("=" * 80 + "\n")

    terminal = TerminalTool(workspace=str(SCRIPT_DIR / "project"))

    # 尝试执行不允许的命令
    print("1. 尝试执行危险命令 (rm):")
    result = terminal.run({"command": "rm -rf /"})
    print(result)

    # 尝试访问工作目录外的文件
    print("\n2. 尝试访问工作目录外的文件:")
    result = terminal.run({"command": "cat /etc/passwd"})
    print(result)

    # 尝试逃逸工作目录
    print("\n3. 尝试通过 .. 逃逸工作目录:")
    result = terminal.run({"command": "cd ../../../etc"})
    print(result)


def main():
    print("=" * 80)
    print("TerminalTool 使用示例")
    print("=" * 80)

    # 演示各种使用场景
    demo_exploratory_navigation()
    demo_data_file_analysis()
    demo_log_analysis()
    demo_codebase_analysis()
    demo_security_features()

    print("\n" + "=" * 80)
    print("演示完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
