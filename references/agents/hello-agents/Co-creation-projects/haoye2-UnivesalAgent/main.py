from dotenv import load_dotenv
from src.agents.agent_universal import UniversalAgent

load_dotenv()  # 从 .env 读取配置（LLM相关）

def main():
    try:
        agent = UniversalAgent()
        print("🤖 Hello-Agents 通用智能体启动！\n(输入 'exit' 或 'quit' 退出)")

        while True:
            try:
                user_input = input("\n请输入您的问题:").strip()
                
                # 空输入处理
                if not user_input:
                    print("⚠️  请输入有效的问题或命令")
                    continue
                
                # 退出判断
                if user_input.lower() in ("exit", "quit"):
                    print("\n👋 再见！")
                    break
                
                # 调用 Agent
                output = agent.run(user_input)
                print("\nAI >\n", output)
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 处理错误: {e}")
                continue
                
    except Exception as e:
        print(f"❌ 初始化 Agent 失败: {e}")
        print("💡 请检查 .env 配置文件和 LLM API 设置")

if __name__ == "__main__":
    main()
