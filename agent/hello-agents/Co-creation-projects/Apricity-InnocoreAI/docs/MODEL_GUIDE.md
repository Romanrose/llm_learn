# InnoCore AI 模型选择指南

## 推荐模型配置

### 1. OpenAI（国际用户推荐）

**优点：** 稳定、API 简单、效果好
**缺点：** 需要国际网络、按 token 计费

```bash
# .env 配置
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo  # 或 gpt-4
```

**模型选择：**
- `gpt-3.5-turbo` - 快速、便宜，适合日常使用
- `gpt-4` - 更强大，适合复杂分析
- `gpt-4-turbo-preview` - 最新版本，上下文更长

---

### 2. 阿里云灵积 DashScope（国内用户推荐）⭐

**优点：** 国内访问快、中文理解好、价格实惠
**缺点：** 需要阿里云账号

```bash
# .env 配置
DASHSCOPE_API_KEY=sk-your-dashscope-key
LLM_PROVIDER=dashscope
LLM_MODEL=qwen-turbo
```

**模型选择：**
- `qwen-turbo` - 快速响应，适合实时交互（推荐）
- `qwen-plus` - 平衡性能和成本
- `qwen-max` - 最强性能，适合复杂任务

**获取 API Key：**
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通灵积服务
4. 创建 API Key

---

### 3. ModelScope（本地部署）

**优点：** 完全免费、数据隐私、可定制
**缺点：** 需要 GPU、部署复杂

#### 推荐模型：

**文本分析（当前需求）：**
- `Qwen2.5-7B-Instruct` - 7B 参数，需要 16GB 显存
- `Qwen2.5-14B-Instruct` - 14B 参数，需要 32GB 显存
- `GLM-4-9B` - 9B 参数，中文理解好

**多模态（图表理解）：**
- `Qwen2-VL-7B-Instruct` - 能理解论文图表
- `InternVL2-8B` - 学术场景表现好

**本地部署步骤：**

```bash
# 1. 安装依赖
pip install modelscope transformers torch

# 2. 下载模型
from modelscope import snapshot_download
model_dir = snapshot_download('qwen/Qwen2.5-7B-Instruct')

# 3. 启动推理服务（使用 vLLM 或 FastChat）
python -m vllm.entrypoints.openai.api_server \
    --model qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8001

# 4. 配置 .env
OPENAI_BASE_URL=http://localhost:8001/v1
OPENAI_API_KEY=dummy  # 本地部署不需要真实 key
LLM_MODEL=qwen/Qwen2.5-7B-Instruct
```

---

## 针对不同场景的推荐

### 场景 1：快速开发测试
**推荐：** OpenAI gpt-3.5-turbo
- 最简单，开箱即用
- 适合原型开发

### 场景 2：生产环境（国内）
**推荐：** DashScope qwen-turbo ⭐⭐⭐
- 访问速度快
- 中文理解好
- 成本可控

### 场景 3：数据隐私要求高
**推荐：** 本地部署 Qwen2.5-7B
- 数据不出本地
- 完全可控

### 场景 4：需要理解论文图表
**推荐：** Qwen2-VL-7B-Instruct
- 多模态能力
- 能理解公式和图表

---

## 性能对比

| 模型 | 中文能力 | 英文能力 | 速度 | 成本 | 推荐度 |
|------|---------|---------|------|------|--------|
| GPT-3.5-turbo | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 快 | 中 | ⭐⭐⭐⭐ |
| GPT-4 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 慢 | 高 | ⭐⭐⭐⭐ |
| Qwen-turbo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 快 | 低 | ⭐⭐⭐⭐⭐ |
| Qwen-max | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中 | 中 | ⭐⭐⭐⭐⭐ |
| Qwen2.5-7B (本地) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中 | 免费 | ⭐⭐⭐⭐ |

---

## 快速开始

### 方案 A：使用 OpenAI（最简单）

1. 获取 API Key: https://platform.openai.com/api-keys
2. 编辑 `.env` 文件：
```bash
OPENAI_API_KEY=sk-your-key-here
```
3. 重启服务器

### 方案 B：使用阿里云灵积（推荐国内用户）⭐

1. 获取 API Key: https://dashscope.console.aliyun.com/
2. 编辑 `.env` 文件：
```bash
DASHSCOPE_API_KEY=sk-your-key-here
LLM_PROVIDER=dashscope
LLM_MODEL=qwen-turbo
```
3. 安装依赖：
```bash
pip install dashscope
```
4. 重启服务器

---

## 常见问题

**Q: 哪个模型最适合科研论文分析？**
A: 推荐 Qwen-max（DashScope）或 GPT-4，它们对学术文本理解最好。

**Q: 如何降低成本？**
A: 使用 qwen-turbo 或本地部署 Qwen2.5-7B。

**Q: 需要处理论文中的图表怎么办？**
A: 使用多模态模型如 Qwen2-VL-7B-Instruct。

**Q: 本地部署需要什么配置？**
A: 最低 16GB 显存的 GPU（如 RTX 4090、A100）。

---

## 技术支持

- ModelScope: https://www.modelscope.cn/
- DashScope: https://help.aliyun.com/zh/dashscope/
- OpenAI: https://platform.openai.com/docs
