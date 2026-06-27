import os
import time
import sys
# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "agents")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from agents.outline_agent import OutlineAgent
from agents.chapter_generate_agent import ChapterGenerateAgent
from hello_agents import HelloAgentsLLM

def print_step(step_name):
    print("\n" + "="*60)
    print(f"正在执行步骤: {step_name}")
    print("="*60 + "\n")

def main():
    # Configuration
    novel_id = f"test_novel_{int(time.time())}"
    title = "测试Agent功能小说"
    user_idea = "一个关于AI程序员意外穿越到自己编写的代码世界中的故事，他需要修复这个世界的BUG才能回到现实。"
    
    print(f"测试配置:\n小说ID: {novel_id}\n标题: {title}\n创意: {user_idea}\n")

    # Initialize LLM
    # Assuming environment variables are set correctly for the default provider
    try:
        llm = HelloAgentsLLM()
        print("LLM 初始化成功。")
    except Exception as e:
        print(f"LLM 初始化失败: {e}")
        return

    # ---------------------------------------------------------
    # Test Outline Agent
    # ---------------------------------------------------------
    print_step("1. 初始化 OutlineAgent (大纲生成Agent)")
    try:
        outline_agent = OutlineAgent(name="TestOutlineAgent", llm=llm)
        print("OutlineAgent 初始化完成。")
    except Exception as e:
        print(f"OutlineAgent 初始化失败: {e}")
        return

    print_step("2. 生成大纲 (Generate Outline)")
    print(f"调用 outline_agent.run，输入创意: {user_idea}")
    start_time = time.time()
    
    try:
        outline_content, outline_note_id = outline_agent.run(
            user_input=user_idea,
            novel_id=novel_id,
            title=title,
            tags=["科幻", "穿越", "程序员"],
            target_length=1000 # Keep it short for testing
        )
    except Exception as e:
        print(f"大纲生成失败: {e}")
        # import traceback
        # traceback.print_exc()
        return

    end_time = time.time()
    print(f"大纲生成耗时: {end_time - start_time:.2f} 秒。")
    print(f"生成的大纲 Note ID: {outline_note_id}")
    print("大纲内容预览 (前500字符):")
    print("-" * 30)
    print(outline_content[:500] + "...")
    print("-" * 30)

    # ---------------------------------------------------------
    # Test Chapter Generate Agent
    # ---------------------------------------------------------
    print_step("3. 初始化 ChapterGenerateAgent (章节生成Agent)")
    try:
        chapter_agent = ChapterGenerateAgent(
            name="TestChapterAgent", 
            llm=llm,
            max_steps=3, # Limit steps for testing
            chapter_length=1000 # Keep it short
        )
        print("ChapterGenerateAgent 初始化完成。")
    except Exception as e:
        print(f"ChapterGenerateAgent 初始化失败: {e}")
        return

    print_step("4. 生成第一章 (Generate Chapter 1)")
    print("调用 chapter_agent.run 生成第一章...")
    start_time = time.time()
    
    try:
        # The first run doesn't have previous chapters, so it should start fresh based on outline
        chapter_data, chapter_note_id = chapter_agent.run(
            user_input="第一章：主角醒来发现自己在代码构成的森林里。",
            novel_id=novel_id,
            novel_title=title
        )
    except Exception as e:
        print(f"章节生成失败: {e}")
        # import traceback
        # traceback.print_exc()
        return
    
    end_time = time.time()
    print(f"第一章生成耗时: {end_time - start_time:.2f} 秒。")
    print(f"生成的章节 Note ID: {chapter_note_id}")
    print(f"章节标题: {chapter_data.get('title')}")
    print(f"章节摘要: {chapter_data.get('summary')}")
    print("章节内容预览 (前500字符):")
    print("-" * 30)
    print(chapter_data.get('content', '')[:500] + "...")
    print("-" * 30)

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------
    print_step("5. 验证输出文件 (Verify Output Files)")
    outline_path = os.path.join("outputs", f"{title}-{novel_id}", "outline")
    chapter_path = os.path.join("outputs", f"{title}-{novel_id}", "chapters")
    
    print(f"检查大纲目录: {outline_path}")
    if os.path.exists(outline_path) and os.listdir(outline_path):
        print("PASS: 大纲目录存在且不为空。")
    else:
        print("FAIL: 大纲目录缺失或为空。")

    print(f"检查章节目录: {chapter_path}")
    if os.path.exists(chapter_path) and os.listdir(chapter_path):
        print("PASS: 章节目录存在且不为空。")
    else:
        print("FAIL: 章节目录缺失或为空。")

    print("\n" + "="*60)
    print("测试流程结束")
    print("="*60)

if __name__ == "__main__":
    main()
