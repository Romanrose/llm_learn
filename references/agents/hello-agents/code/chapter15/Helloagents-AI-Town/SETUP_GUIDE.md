# 赛博小镇 - 安装配置指南

## 📋 系统要求

- **操作系统:** Windows 10/11, macOS, Linux
- **Godot:** 4.2+ (推荐4.3)
- **Python:** 3.10+
- **Git:** (可选,用于克隆项目)

## 🚀 安装步骤

### 步骤1: 下载项目

**方法A: 使用Git**
```bash
git clone https://github.com/datawhalechina/hello-agents
cd chapter15
```

**方法B: 下载ZIP**
1. 下载项目ZIP文件
2. 解压到任意目录

### 步骤2: 安装Godot

1. 访问 [Godot官网](https://godotengine.org/download)
2. 下载Godot 4.2+版本
3. 解压并运行Godot

### 步骤3: 配置Python环境

#### 3.1 创建虚拟环境
```bash
cd backend
python -m venv venv
```

#### 3.2 激活虚拟环境
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### 3.3 安装依赖
```bash
pip install -r requirements.txt
```

#### 3.4 安装HelloAgents
```bash
cd ../HelloAgents
pip install -e .
cd ../backend
```

### 步骤4: 配置环境变量

#### 4.1 复制环境变量文件
```bash
cp .env.example .env
```

#### 4.2 编辑.env文件
```env
# API配置
API_HOST=0.0.0.0
API_PORT=8000

# LLM配置 - 请填写你的API密钥
LLM_API_KEY=sk-your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# NPC更新间隔(秒)
NPC_UPDATE_INTERVAL=30
```

**重要:** 请将 `LLM_API_KEY` 替换为你的实际API密钥!

### 步骤5: 启动后端服务

```bash
cd backend
python main.py
```

**预期输出:**
```
📝 对话日志文件: .../backend/logs/dialogue_2025-10-15.log
📂 日志目录: .../backend/logs

============================================================
🎮 赛博小镇后端服务启动中...
============================================================
...
✅ 所有服务已启动!
📡 API地址: http://0.0.0.0:8000
📚 API文档: http://0.0.0.0:8000/docs
============================================================
```

### 步骤6: 打开Godot项目

1. 启动Godot
2. 点击"导入"
3. 选择 `Helloagents-AI-Town/helloagents-ai-town/scenes/main.tscn`
4. 点击"导入并编辑"

### 步骤7: 运行游戏

1. 在Godot编辑器中,点击右上角的"运行"按钮 (或按F5)
2. 游戏窗口应该打开
3. 使用WASD移动,E键与NPC交互

## 🎮 游戏操作

- **WASD** - 移动玩家
- **E** - 与NPC交互
- **Enter** - 发送消息
- **ESC** - 关闭对话框

## 🧪 测试

### 测试后端API
访问: http://localhost:8000/docs

### 查看对话日志
```bash
cd backend
python view_logs.py tail
```

## ❓ 常见问题

### Q1: 后端启动失败?
**A:** 检查:
1. Python版本是否>=3.10
2. 是否激活了虚拟环境
3. 是否安装了所有依赖
4. .env文件是否配置正确

### Q2: Godot无法打开项目?
**A:** 检查:
1. Godot版本是否>=4.2
2. project.godot文件是否存在
3. 是否选择了正确的目录

### Q3: 游戏运行但无法对话?
**A:** 检查:
1. 后端服务是否正在运行
2. 后端地址是否正确 (默认http://localhost:8000)
3. 查看Godot控制台的错误信息

## 🎉 开始体验!

现在你可以在游戏中与NPC对话了!