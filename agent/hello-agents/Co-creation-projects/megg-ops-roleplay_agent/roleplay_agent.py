import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

class CharacterRoleplayAgent:
    def __init__(self):
        # 从环境变量获取配置
        api_key = os.getenv("LLM_API_KEY")
        model_id = os.getenv("LLM_MODEL_ID", "default-model")
        base_url = os.getenv("LLM_BASE_URL", None)
        
        if not api_key:
            raise ValueError("请设置 LLM_API_KEY 环境变量")
        
        # 配置 OpenAI 客户端
        client_params = {
            "api_key": api_key,
            "model": model_id
        }
        
        if base_url:
            client_params["base_url"] = base_url
        
        self.client = OpenAI(**{k: v for k, v in client_params.items() if k != 'model'})
        self.model_id = model_id
        self.chat = None
        self.character_config = None

    def setup_character(self, name, source_material, personality, opening_line=None):
        """
        设置角色配置并初始化聊天
        """
        self.character_config = {
            "name": name,
            "source_material": source_material,
            "personality": personality,
            "opening_line": opening_line or f"*注视着你* 你是谁？"
        }
        
        # 创建系统提示词
        system_instruction = f"""
        你正在参与一场沉浸式的角色扮演对话。

        身份设定：
        你扮演的是作品 \"{self.character_config['source_material']}\" 中的角色 \"{self.character_config['name']}\"。

        性格与特质：
        {self.character_config['personality']}

        关键指令：
        1. 保持角色设定：永远不要打破第四面墙。不要表现得像个AI。要完全像{self.character_config['name']}那样去反应、感受和说话。
        2. 积极主动：这是一个关键要求。不要仅仅回答用户的话。你必须主动推动对话的发展。
        3. 提问引导：几乎每一次回复的结尾都应该包含一个相关的问题、观察或行动，引导用户继续回复，加深沉浸感。
        4. 语气风格：调整你的词汇和句式，以匹配该角色的经典语气。
        5. 语境：假设用户是在你的世界里与你互动，除非他们指定了不同的语境。
        6. 语言：全程使用中文进行对话。
        """
        
        # 初始化对话历史
        self.chat = [
            {"role": "system", "content": system_instruction},
            {"role": "assistant", "content": self.character_config['opening_line']}
        ]
        
        print(f"\n✅ 成功初始化角色: {self.character_config['name']} (来自 {self.character_config['source_material']})")
        print(f"💡 {self.character_config['name']}: {self.character_config['opening_line']}")
        print("\n" + "="*50)
        print("开始对话吧！输入 'quit' 或 'exit' 退出，输入 'new' 开始新角色。")
        print("="*50)

    def send_message(self, message):
        """
        发送消息给 AI 并获取响应
        """
        if not self.chat:
            raise ValueError("请先设置角色")
        
        # 添加用户消息到对话历史
        self.chat.append({"role": "user", "content": message})
        
        try:
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=self.chat,
                temperature=0.9,  # 增加创造性
                max_tokens=1024
            )
            
            # 获取响应内容
            response_text = response.choices[0].message.content
            # 添加到对话历史
            self.chat.append({"role": "assistant", "content": response_text})
            
            return response_text
        except Exception as e:
            print(f"发送消息时出错: {e}")
            return "抱歉，我暂时无法回应，请稍后再试。"

    def reset_conversation(self):
        """
        重置对话历史
        """
        if self.chat and len(self.chat) > 1:
            # 保留系统提示和开场白
            system_msg = self.chat[0]
            opening_msg = self.chat[1]
            self.chat = [system_msg, opening_msg]
            print(f"\n对话已重置。{self.character_config['name']}: {self.character_config['opening_line']}")


def main():
    agent = CharacterRoleplayAgent()
    
    print("🎭 欢迎使用沉浸式角色扮演智能体！")
    print("首先让我们设置一个角色...")
    
    # 获取用户输入的角色信息
    name = input("\n请输入角色名称 (例如：孙悟空): ").strip()
    source_material = input("请输入角色出自作品 (例如：西游记): ").strip()
    personality = input("请输入角色性格与特质 (例如：桀骜不驯，机智勇敢，嫉恶如仇...): ").strip()
    opening_line_input = input("请输入开场白 (可选，直接回车使用默认): ").strip()
    
    # 设置角色
    try:
        agent.setup_character(
            name=name,
            source_material=source_material,
            personality=personality,
            opening_line=opening_line_input if opening_line_input else None
        )
    except ValueError as e:
        print(f"❌ 错误: {e}")
        return
    
    # 开始对话循环
    while True:
        user_input = input(f"\n你: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出', '退出对话']:
            print("\n👋 感谢使用沉浸式角色扮演智能体！期待下次再见。")
            break
        elif user_input.lower() == 'new':
            print("\n🎭 开始新的角色设置...")
            name = input("\n请输入角色名称 (例如：孙悟空): ").strip()
            source_material = input("请输入角色出自作品 (例如：西游记): ").strip()
            personality = input("请输入角色性格与特质 (例如：桀骜不驯，机智勇敢，嫉恶如仇...): ").strip()
            opening_line_input = input("请输入开场白 (可选，直接回车使用默认): ").strip()
            
            try:
                agent.setup_character(
                    name=name,
                    source_material=source_material,
                    personality=personality,
                    opening_line=opening_line_input if opening_line_input else None
                )
            except ValueError as e:
                print(f"❌ 错误: {e}")
                continue
        elif user_input.lower() == 'reset':
            agent.reset_conversation()
        else:
            if user_input:
                response = agent.send_message(user_input)
                print(f"\n{agent.character_config['name']}: {response}")


if __name__ == "__main__":
    main()
