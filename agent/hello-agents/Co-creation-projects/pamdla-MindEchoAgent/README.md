# MindEchoAgent · 心境回响

🧠🎵 MindEchoAgent - 情绪驱动的音乐推荐智能体，用AI感知心情，用音乐温暖心灵。
> 目前它是一个基于 hello-agents 框架构建的情绪音乐推荐智能体。

## ✨ 特点
- 🎧 情绪驱动，而非标签驱动：基于深度情绪识别而非简单标签匹配
- 🧠 Agent + Tool 架构：基于Hello-Agents框架，模块化设计，易于扩展
- 🧪 完全模拟，稳定可控：可内置高质量模拟数据，无需API密钥即可体验全部功能
- 🎛 Gradio 快速演示：开箱即用的Web界面，支持实时交互演示
- 🔄 记忆系统（待完善）：具备短期心境记忆，可记录和分析情绪变化模式
- 📱 多端适配（待扩展）：Web界面适配移动端，后续支持智能家居设备

## 🔧 技术栈
- 核心框架: hello-agents >= 0.2.7
- Web界面: gradio >= 4.0
- 语言环境: Python 3.10+
- 数据处理: json, datetime, typing
- 环境管理: python-dotenv

## 启动方式
```bash
# 1. 克隆项目
git clone https://github.com/pamdla/MindEchoAgent.git
cd MindEchoAgent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

## 📁 项目结构

```
MindEchoAgent/
├── main.py                      # Gradio主界面
├── requirements.txt             # 依赖列表
├── README.md                    # 项目说明
├── .env.example                 # 环境变量示例
├── assets/                      # 静态资源
│   ├── architecture.png         # 架构图
│   └── demo-screenshot.png      # 演示截图
├── src/                         # 源代码
│   ├── __init__.py
│   ├── agents/                  # 智能体模块
│   │   ├── __init__.py
│   │   ├── sleep_agent.py       # 子智能体
│   │   └── mind_echo_agent.py   # 主智能体
│   ├── tools/                   # 工具模块
│       ├── __init__.py
│       ├── dialogue_state_tool.py # 对话状态工具
│       ├── mood_music_tool.py   # 音乐推荐工具
│       ├── text_comfort_tool.py # 文字安慰工具
│       └── mood_summary_tool.py # 心情总结工具
│   └── utils                    # 其它工具
│       ├── loader.py            # 工具加载
│       └── state.py             # 状态定义
└── data/                        # 数据目录
    └── mood_history.json        # 心情历史记录
```


## ⭐ 核心功能

1. 情绪识别与响应

- 对话状态识别: 初始状态、情绪识别、情感支持、音乐推荐、情绪反思、问题升级6种状态
- 多维情绪检测：识别开心、悲伤、放松、专注、压力、兴奋等6种核心情绪
- 上下文感知：结合场景（工作、运动、学习、睡前等）提供精准推荐
- 自然语言交互：理解口语化表达，如"今天好累"、"心情美美的"

2. 智能音乐推荐（待完善）

- 个性化播放列表：根据心情和场景生成定制化音乐推荐
- 模拟数据引擎：可内置偏好的曲目，覆盖多种风格和场景
- 播放时长计算：智能计算播放列表总时长，优化聆听体验

3. 情感支持系统

- 双模式安慰引擎：预设回复 + LLM生成，确保稳定性和创造性
- 共情表达：温暖、支持的语气，搭配适当的emoji表情
- 实用建议：提供具体、可操作的情绪调节建议

4. 心境记忆分析

- 历史记录：自动记录每次交互的心情状态
- 模式识别：分析情绪变化趋势和时间分布
- 个性化洞察：提供基于历史数据的个性化建议

## 🏠 Web界面操作

启动应用后，

- 在浏览器打开 http://localhost:7860
- 输入心情描述，如："今天工作压力好大，想听放松的音乐"
- 查看智能响应，包含：
> 情绪识别结果
> 个性化音乐推荐
> 情感支持文字
> 心情分析报告


## 🚀 后续优化计划

1. 功能扩展【近期（~1个月）】

```js
- 记忆系统（记录和分析情绪变化）
- 音乐预览片段（30秒试听功能）
- 增加音乐文件（不同类型1\~2首歌曲）
```

2. 用户体验优化【中期（~2个月）】

```js
# 计划新增功能
- 对话历史管理（支持多轮对话上下文）
- 情感强度调节滑块（用户可调整推荐强度）
- 个性化偏好设置（音乐风格、语言偏好）
- 多端适配（支持家居设备，音箱、灯光、窗帘等）
```

## 🎬 演示效果
### 界面截图、演示录屏

- [B站链接-演示录屏](https://www.bilibili.com/video/BV1FmFpzSELf)

## 🌐 智能家居扩展

### 小米音箱集成方案

阶段1：基础对接

```js
# 技术栈：Python + MiService + WebSocket
# 1. 创建小米音箱技能
- 注册小米开发者账号
- 创建智能家居技能
- 配置语音交互模型

# 2. 实现语音接口
- 语音转文本（ASR）
- 文本转语音（TTS）
- 指令解析与响应

# 3. 设备控制集成
- 播放控制（播放、暂停、切歌）
- 音量调节
- 播放列表管理
```


## 🙏 致谢

感谢以下项目和社区的支持：

- [Datawhale - 开源学习社区](https://github.com/datawhalechina)
- [Datawhale - Hello-Agents课程](https://github.com/datawhalechina/hello-agents)
- [Hello-Agents - 智能体框架](https://github.com/jjyaoao/HelloAgents)
- [Gradio - 机器学习Web演示框架](https://www.gradio.app/)

所有贡献者和用户
