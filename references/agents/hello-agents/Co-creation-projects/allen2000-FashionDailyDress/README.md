# 🌤️ 多智能体天气穿衣建议系统

一个基于多智能体协作的天气查询和穿衣建议系统，使用Python和Gradio构建。

## 🎯 项目简介

本项目实现了一个智能的天气穿衣建议系统，通过多个智能体协作处理用户查询：
- **天气查询智能体**：负责获取实时天气数据
- **穿衣建议智能体**：基于天气信息生成专业的穿衣建议
- **协调器智能体**：管理智能体间的协作和任务分配

## ✨ 核心功能

- 🌤️ **实时天气查询**：支持全球主要城市的天气查询
- 🤖 **AI智能建议**：基于天气数据生成专业的穿衣建议
- 🔄 **多智能体协作**：智能体间高效协作处理复杂任务
- 🌐 **Web界面**：友好的Gradio图形界面

## 📁 项目结构

```
bill-FashionDailyDress/
├── fashion_agent.py          # 穿衣建议智能体
├── gradio_app.py            # Gradio Web界面
├── multi_agent_coordinator.py # 多智能体协调器
├── simple_multi_agent.py    # 简化版多智能体系统
├── weather.py               # 天气查询功能
├── weather_mcp.py           # MCP天气服务器
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd bill-FashionDailyDress

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件并配置必要的API密钥：

```env
# LLM配置（必需）
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=your_llm_base_url
LLM_MODEL_ID=your_llm_model_id

# 天气API配置（可选，用于真实天气数据）
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 3. 运行系统

#### 方式一：使用Gradio Web界面（推荐）
python版本3.12.10
```bash
python gradio_app.py
```
访问 http://localhost:8899 使用图形界面

#### 方式二：命令行交互
```bash
python simple_multi_agent.py
```

## 🔧 核心模块说明

### fashion_agent.py
- **功能**：专业的穿衣建议智能体
- **特点**：基于温度、湿度、风速等天气因素提供详细建议
- **输出**：包含服装搭配、配饰建议、注意事项等

### multi_agent_coordinator.py
- **功能**：多智能体协调器
- **特点**：管理天气查询和穿衣建议智能体的协作
- **流程**：接收查询 → 获取天气 → 生成建议 → 整合结果

### gradio_app.py
- **功能**：Web图形界面
- **特点**：用户友好的交互界面，支持示例快速体验
- **端口**：8899

### weather.py
- **功能**：天气查询封装
- **特点**：支持真实API和演示模式
- **API**：OpenWeatherMap API集成

## 📋 使用示例

### 输入示例
- Beijing
- Shanghai
- Tokyo
- London

### 输出示例
```
🏙️ 查询城市: 北京
🌡️ 温度: 25°C
📝 天气: 晴朗
💧 湿度: 60%
🌬️ 风速: 3 m/s

👗 穿衣建议：
基于当前天气状况，建议穿着轻薄透气的衣物...
```

## ⚙️ 配置说明

### 必需配置
- LLM API密钥和端点（用于智能体推理）

### 可选配置
- OpenWeatherMap API密钥（用于真实天气数据）
- 如不配置，系统将使用演示模式提供模拟数据

## 🛠️ 技术栈

- **框架**：hello-agents, fastmcp
- **Web界面**：Gradio
- **HTTP请求**：requests
- **配置管理**：python-dotenv
- **天气API**：OpenWeatherMap

## 🔍 开发指南

### 添加新的智能体
1. 创建新的智能体类（参考fashion_agent.py）
2. 在协调器中注册智能体
3. 更新系统提示词和协作逻辑

### 扩展功能
- 支持更多天气数据源
- 添加历史天气分析
- 集成更多穿衣风格建议

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 项目维护者邮箱

---

**享受智能穿衣建议！** 👗✨