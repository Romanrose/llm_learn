#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能邮件助手 - Python脚本版本
EmailSmartAssistant - Python Script Version

这是Jupyter Notebook的简化Python脚本版本，可以直接运行。
"""

import json
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """主函数"""
    console.print(Panel.fit(
        "🤖 智能邮件助手 (EmailSmartAssistant)\n"
        "Python脚本版本\n\n"
        "功能包括：\n"
        "• 邮件自动分类\n"
        "• 智能回复草稿生成\n"
        "• 重要事项智能提醒\n"
        "• 邮件关键信息提取\n"
        "• 邮件归档整理",
        title="欢迎使用",
        style="blue"
    ))
    
    # 检查配置文件
    try:
        with open('config/email_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        console.print("✅ 配置文件加载成功", style="green")
    except FileNotFoundError:
        console.print("❌ 配置文件未找到", style="red")
        console.print("请先配置 config/email_config.json 文件", style="yellow")
        return
    
    # 检查模板文件
    try:
        with open('templates/reply_templates.json', 'r', encoding='utf-8') as f:
            templates = json.load(f)
        console.print("✅ 模板文件加载成功", style="green")
    except FileNotFoundError:
        console.print("❌ 模板文件未找到", style="red")
        return
    
    console.print("\n📋 使用说明:", style="bold yellow")
    console.print("1. 完整功能请使用 EmailSmartAssistant.ipynb")
    console.print("2. 该脚本仅用于快速验证配置和依赖")
    console.print("3. 修改配置文件后可运行此脚本检查")
    
    # 显示配置摘要
    console.print(f"\n📧 邮箱账户数量: {len(config['email_accounts'])}", style="cyan")
    console.print(f"🏷️  分类规则: {len(config['classification_rules'])} 类", style="cyan")
    console.print(f"📝 回复模板: {len(templates)} 个", style="cyan")
    
    console.print("\n🚀 准备就绪！请使用 Jupyter Notebook 运行完整功能。", style="bold green")

if __name__ == "__main__":
    main()