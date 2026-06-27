"""实时查看对话日志"""

import os
import time
from pathlib import Path
from datetime import datetime

# 日志目录
LOGS_DIR = Path(__file__).parent / "logs"
today = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOGS_DIR / f"dialogue_{today}.log"

def tail_log_file(filename, interval=1):
    """实时查看日志文件 (类似tail -f)"""
    
    print("\n" + "="*60)
    print(f"📝 实时查看对话日志")
    print(f"📂 日志文件: {filename}")
    print("="*60)
    print("\n按 Ctrl+C 停止查看\n")
    
    # 如果文件不存在,等待创建
    while not filename.exists():
        print(f"⏳ 等待日志文件创建: {filename}")
        time.sleep(interval)
    
    # 打开文件
    with open(filename, 'r', encoding='utf-8') as f:
        # 移动到文件末尾
        f.seek(0, 2)
        
        try:
            while True:
                line = f.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ 停止查看日志")

def view_full_log(filename):
    """查看完整日志"""
    
    print("\n" + "="*60)
    print(f"📝 查看完整对话日志")
    print(f"📂 日志文件: {filename}")
    print("="*60 + "\n")
    
    if not filename.exists():
        print(f"❌ 日志文件不存在: {filename}")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    print("\n" + "="*60)
    print("✅ 日志查看完成")
    print("="*60 + "\n")

def list_log_files():
    """列出所有日志文件"""
    
    print("\n" + "="*60)
    print(f"📂 日志文件列表")
    print(f"📁 目录: {LOGS_DIR}")
    print("="*60 + "\n")
    
    if not LOGS_DIR.exists():
        print("❌ 日志目录不存在")
        return
    
    log_files = sorted(LOGS_DIR.glob("dialogue_*.log"), reverse=True)
    
    if not log_files:
        print("📭 暂无日志文件")
        return
    
    for i, log_file in enumerate(log_files, 1):
        size = log_file.stat().st_size
        size_kb = size / 1024
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"{i}. {log_file.name}")
        print(f"   大小: {size_kb:.2f} KB")
        print(f"   修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "tail":
            # 实时查看
            tail_log_file(LOG_FILE)
        elif command == "view":
            # 查看完整日志
            view_full_log(LOG_FILE)
        elif command == "list":
            # 列出所有日志
            list_log_files()
        else:
            print(f"❌ 未知命令: {command}")
            print("\n使用方法:")
            print("  python view_logs.py tail   # 实时查看日志")
            print("  python view_logs.py view   # 查看完整日志")
            print("  python view_logs.py list   # 列出所有日志文件")
    else:
        # 默认实时查看
        tail_log_file(LOG_FILE)

