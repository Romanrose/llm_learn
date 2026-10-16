# InnoCore AI - Quick Start Guide

## 🚀 快速启动

### 1. 环境准备
确保您已安装 Python 3.8 或更高版本

### 2. 安装依赖
```bash
cd innocore_ai
python setup.py
```

### 3. 配置环境变量
编辑 `.env` 文件，添加您的 OpenAI API Key：
```bash
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 4. 启动应用
```bash
python run.py
```

### 5. 访问应用
- 主页: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 📋 功能特性

### 🤖 智能体系统
- **Hunter Agent**: 文献搜索与监控
- **Miner Agent**: 深度论文分析
- **Coach Agent**: 写作辅助
- **Validator Agent**: 引用验证

### 🔧 核心功能
- 文献自动抓取
- 智能论文分析
- 学术写作助手
- 引用格式管理

## 📁 项目结构

```
innocore_ai/
├── agents/          # 智能体模块
├── api/            # API路由
├── core/           # 核心功能
├── models/         # 数据模型
├── services/       # 业务服务
├── utils/          # 工具函数
├── frontend/       # 前端界面
├── run.py          # 启动脚本
├── setup.py        # 安装脚本
└── .env            # 环境配置
```

## 🛠️ 开发模式

如需开发模式（自动重载），可以修改 `run.py` 中的 `reload=False` 为 `reload=True`

## 📞 故障排除

### 常见问题

1. **端口被占用**
   - 修改 `run.py` 中的端口号
   - 或停止占用8000端口的其他程序

2. **OpenAI API Key 错误**
   - 确保 `.env` 文件中的 API Key 正确
   - 检查 API Key 是否有效且有足够余额

3. **依赖安装失败**
   - 尝试使用 `pip install --upgrade pip` 更新pip
   - 或使用虚拟环境

## 📚 更多信息

- 详细文档: [README.md](README.md)
- API文档: http://localhost:8000/docs
- 配置示例: [.env.example](.env.example)

---

**InnoCore AI - 研创·智核**
让AI助力您的科研创新之旅 🚀