"""
Gradio前端界面 - 多智能体天气穿衣建议系统
在本地8899端口提供服务
"""
import gradio as gr
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_weather_and_fashion_advice(city_name):
    """
    获取指定城市的天气和穿衣建议
    :param city_name: 城市名称
    :return: 完整的响应文本
    """
    try:
        # 导入多智能体协调器
        from multi_agent_coordinator import MultiAgentCoordinator
        
        # 创建协调器实例
        coordinator = MultiAgentCoordinator()
        
        # 构建查询
        query = f"查询{city_name}的天气并给出穿衣建议"
        
        # 处理查询
        result = coordinator.process_query(query)
        
        # 返回完整的响应文本
        response_text = f"""
🏙️ **查询城市**: {city_name}
🔍 **查询内容**: {query}

📊 **多智能体协作结果**:
{result}

💡 **系统说明**:
- 本系统使用多智能体协作架构
- 天气查询智能体负责获取天气数据
- 穿衣建议智能体基于天气数据生成专业建议
- 协调器负责智能体间的通信和任务分配
"""
        
        return response_text
        
    except Exception as e:
        # 如果多智能体系统不可用，使用简化版本
        try:
            from simple_multi_agent import get_real_weather, get_llm_fashion_advice
            
            # 获取天气信息
            weather_info, weather_details = get_real_weather(city_name)
            
            # 获取LLM穿衣建议
            fashion_advice = get_llm_fashion_advice(weather_details, city_name)
            
            response_text = f"""
🏙️ **查询城市**: {city_name}

📊 **天气信息**:
{weather_info}

🤖 **LLM智能穿衣建议**:
{fashion_advice}

💡 **系统说明**:
- 使用简化版多智能体系统
- 基于真实天气数据生成建议
- LLM智能处理穿衣建议
"""
            return response_text
            
        except Exception as e2:
            # 如果所有方法都失败，返回错误信息
            error_text = f"""
❌ **系统错误**: 无法获取{city_name}的天气和穿衣建议

**错误信息**:
- 主要错误: {str(e)}
- 备用错误: {str(e2)}

💡 **解决方案**:
1. 检查网络连接
2. 确保天气API服务可用
3. 检查系统依赖是否完整安装

🔧 **备用建议**:
您可以尝试以下城市：北京、上海、广州、深圳、杭州、成都等
"""
            return error_text

def create_gradio_interface():
    """创建Gradio界面"""
    
    # 界面描述
    description = """
    # 🌤️ 多智能体天气穿衣建议系统
    
    输入您想查询的城市名称，系统将为您提供：
    - 📊 实时天气信息
    - 🤖 LLM智能穿衣建议
    - 💡 专业穿搭指导
    
    **支持功能**:
    - 多智能体协作处理
    - 真实天气数据查询
    - AI智能穿衣建议
    - 多轮对话支持
    """
    
    # 创建界面
    with gr.Blocks(
        title="多智能体天气穿衣建议系统",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 900px !important;
        }
        .output-text {
            font-size: 14px;
            line-height: 1.6;
        }
        """
    ) as demo:
        
        gr.Markdown(description)
        
        with gr.Row():
            with gr.Column(scale=1):
                city_input = gr.Textbox(
                    label="🌍 请输入城市名称",
                    placeholder="例如：北京、上海、广州、深圳...",
                    info="支持中文和英文城市名"
                )
                
                submit_btn = gr.Button(
                    "🚀 获取穿衣建议",
                    variant="primary",
                    size="lg"
                )
                
                clear_btn = gr.Button("🗑️ 清空", variant="secondary")
                
            with gr.Column(scale=2):
                output_text = gr.Textbox(
                    label="📋 完整响应结果",
                    lines=20,
                    max_lines=30,
                    show_copy_button=True,
                    elem_classes="output-text"
                )
        
        # 示例城市
        examples = gr.Examples(
            examples=[["beijing"], ["tokoy"], ["london"], ["new york"], ["paris"], ["seoul"], ["bangkok"], ["harbin"]],
            inputs=city_input,
            label="💡 点击示例快速体验"
        )
        
        # 按钮事件
        submit_btn.click(
            fn=get_weather_and_fashion_advice,
            inputs=city_input,
            outputs=output_text
        )
        
        clear_btn.click(
            fn=lambda: "",
            inputs=[],
            outputs=output_text
        )
        
        # 回车键提交
        city_input.submit(
            fn=get_weather_and_fashion_advice,
            inputs=city_input,
            outputs=output_text
        )
        
        # 页脚信息
        gr.Markdown("""
        ---
        
        ### 🔧 系统信息
        - **版本**: v1.0.0
        - **架构**: 多智能体协作系统
        - **技术栈**: Python + Gradio + 多智能体框架
        - **端口**: 8899
        
        ### 📖 使用说明
        1. 在左侧输入框输入城市名称
        2. 点击"获取穿衣建议"按钮或按回车键
        3. 查看右侧的完整响应结果
        4. 可以点击示例快速体验不同城市
        
        ### 🎯 功能特点
        - 🌤️ 实时天气数据查询
        - 🤖 AI智能穿衣建议
        - 🔄 多智能体协作处理
        - 📱 响应式Web界面
        - 🎨 美观的用户体验
        """)
    
    return demo

def main():
    """启动Gradio应用"""
    print("🚀 启动多智能体天气穿衣建议系统 - Gradio前端")
    print("🌐 服务地址: http://localhost:8899")
    print("⏳ 正在启动服务...")
    
    # 创建界面
    demo = create_gradio_interface()
    
    # 启动服务
    demo.launch(
        server_name="0.0.0.0",
        server_port=8899,
        share=False,
        show_error=True,
        debug=True,
        quiet=False
    )

if __name__ == "__main__":
    main()