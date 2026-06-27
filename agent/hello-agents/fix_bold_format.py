#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复Markdown文件中的加粗格式
将 **文本** 替换为 <strong>文本</strong>
"""

import re
import os
import glob

def fix_bold_format_in_file(file_path):
    """修复单个文件中的加粗格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 先找出所有代码块的位置
        code_blocks = []
        code_pattern = r'```[\s\S]*?```'
        for match in re.finditer(code_pattern, content):
            code_blocks.append((match.start(), match.end()))
        
        # 使用正则表达式匹配 **文本** 并替换为 <strong>文本</strong>
        # 确保不匹配已经是HTML标签的情况和代码块内的情况
        pattern = r'\*\*([^*]+?)\*\*'
        
        def replacement_func(match):
            # 检查匹配位置是否在代码块内
            match_start = match.start()
            for block_start, block_end in code_blocks:
                if block_start <= match_start < block_end:
                    return match.group(0)  # 在代码块内，不替换
            return f'<strong>{match.group(1)}</strong>'  # 不在代码块内，进行替换
        
        # 执行替换
        new_content = re.sub(pattern, replacement_func, content)
        
        # 如果内容有变化，写回文件
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            print(f"ℹ️  无需修改: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 处理文件出错 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 查找所有Markdown文件
    docs_dir = "xxx/xxx"
    
    # 递归查找所有.md文件
    md_files = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"找到 {len(md_files)} 个Markdown文件")
    print("=" * 50)
    
    modified_count = 0
    for file_path in md_files:
        if fix_bold_format_in_file(file_path):
            modified_count += 1
    
    print("=" * 50)
    print(f"处理完成！共修改了 {modified_count} 个文件")

if __name__ == "__main__":
    main()
