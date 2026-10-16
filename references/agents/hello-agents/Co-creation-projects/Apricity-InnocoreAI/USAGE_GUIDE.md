# InnoCore AI 使用指南

## 快速开始

### 1. 启动服务器

```bash
python run.py
```

服务器将在 `http://localhost:8000` 启动。

### 2. 访问界面

在浏览器中打开：
- **主页**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 3. 验证系统

运行验证脚本确保所有功能正常：

```bash
python verify_system.py
```

## 工作模式

InnoCore AI 支持两种工作模式：

### 🔹 单独模式（Individual Mode）
独立使用每个智能体，适合：
- 单一任务需求
- 需要精细控制
- 快速测试功能

### 🔹 协调模式（Workflow Mode）⭐ 推荐
自动协调所有智能体完成完整工作流，适合：
- 完整的研究流程
- 自动化批量处理
- 生成综合报告

**完整工作流程**：
1. Hunter 搜索相关论文
2. Miner 深度分析每篇论文
3. Validator 生成标准引用
4. Coach 撰写综合报告

## 功能使用

### 📚 Hunter - 论文搜索

**功能**: 从 ArXiv 搜索学术论文

**使用方法**:
1. 在"Hunter - 论文搜索"卡片中输入关键词
2. 选择数据源（默认 ArXiv）
3. 设置返回数量（1-50）
4. 点击"开始搜索"

**示例关键词**:
- `machine learning`
- `deep learning`
- `natural language processing`
- `computer vision`

**返回信息**:
- 论文标题
- 作者列表
- 摘要
- 发表日期
- ArXiv ID
- PDF 下载链接

### 🔍 Miner - 论文分析

**功能**: 深度分析论文内容，支持完整的 PDF 解析

**使用方法**:
1. **方式一：ArXiv URL**
   - 输入 ArXiv URL（如 `https://arxiv.org/abs/2301.00001`）
   - 系统自动获取论文信息

2. **方式二：上传 PDF 文件**
   - 点击或拖拽上传 PDF 文件
   - 系统自动解析并提取：
     * 论文标题
     * 作者信息
     * 摘要内容
     * 全文文本
     * 页数和字数
   - 解析完成后自动填充 URL 字段

3. 选择分析类型：
   - **摘要 (summary)**: 生成论文概要
   - **创新点 (innovation)**: 分析技术创新
   - **对比 (comparison)**: 与现有方法对比
   - **综合 (comprehensive)**: 全面深度分析

4. 点击"开始分析"

**支持的输入格式**:
- ArXiv URL: `https://arxiv.org/abs/XXXX.XXXXX`
- ArXiv ID: `2301.00001`
- PDF 文件: 任何标准 PDF 文档（推荐文字版）

**PDF 解析功能**:
- ✅ 自动提取标题和作者
- ✅ 智能识别摘要部分
- ✅ 提取完整文本内容
- ✅ 统计页数和字数
- ✅ 基于完整内容进行 AI 分析

**注意事项**:
- 扫描版 PDF 可能无法提取文本
- 建议使用文字版 PDF 以获得最佳效果
- 单个文件建议不超过 50MB

### ✍️ Coach - 写作助手

**功能**: 学术写作辅助

**使用方法**:
1. 在文本框中输入需要处理的文本
2. 选择写作风格：
   - **学术**: 正式学术风格
   - **技术**: 技术文档风格
   - **通俗**: 易懂的科普风格
3. 选择任务类型：
   - **改进**: 提升文本质量
   - **润色**: 优化表达
   - **翻译**: 多语言翻译
   - **检查**: 语法和拼写检查
4. 点击"开始处理"

**应用场景**:
- 论文摘要润色
- 技术文档改进
- 学术翻译
- 语法检查

### ✅ Validator - 引用校验

**功能**: 学术引用格式化和验证

**使用方法**:
1. 输入引用信息（支持多种格式）
2. 选择目标格式：
   - **BibTeX**: LaTeX 文档引用
   - **APA**: 美国心理学会格式
   - **IEEE**: 电气电子工程师学会格式
   - **MLA**: 现代语言学会格式
3. 点击"开始校验"

**支持的输入**:
- 包含 DOI 的引用
- ArXiv URL 或 ID
- 自由格式的引用文本

**自动识别**:
- DOI 自动验证（通过 Crossref API）
- ArXiv ID 自动提取
- AI 辅助解析引用信息

### 🔄 完整工作流（推荐）

**功能**: 一键完成从搜索到报告的全流程

**使用方法**:
1. 切换到"协调模式"
2. 输入研究关键词
3. 选择搜索数量（3/5/10篇）
4. 选择分析类型
5. 选择引用格式
6. 勾选"生成综合报告"（可选）
7. 点击"启动完整工作流"

**自动执行步骤**:
- ✅ 步骤1: 搜索相关论文
- ✅ 步骤2: 分析前3篇论文
- ✅ 步骤3: 生成标准引用
- ✅ 步骤4: 撰写综合报告（可选）

**优势**:
- 节省时间，一键完成
- 自动协调，无需手动切换
- 结果整合，便于查看
- 适合批量研究

## API 使用

### 论文搜索 API

```bash
curl -X POST "http://localhost:8000/api/v1/papers/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "machine learning",
    "source": "arxiv",
    "limit": 10
  }'
```

### 论文分析 API

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_url": "https://arxiv.org/abs/2301.00001",
    "analysis_type": "summary"
  }'
```

### 写作助手 API

```bash
curl -X POST "http://localhost:8000/api/v1/writing/coach" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "style": "academic",
    "task": "improve"
  }'
```

### 引用校验 API

```bash
curl -X POST "http://localhost:8000/api/v1/citations/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "citation": "Your citation here",
    "format": "bibtex"
  }'
```

### 完整工作流 API

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "deep learning",
    "limit": 5,
    "analysis_type": "summary",
    "citation_format": "bibtex",
    "writing_task": "improve"
  }'
```

### 简化工作流 API（仅搜索+分析）

```bash
curl -X POST "http://localhost:8000/api/v1/workflow/search-and-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "machine learning",
    "limit": 3,
    "analysis_type": "summary"
  }'
```

## 常见问题

### Q: 论文搜索没有结果？
A: 尝试使用更通用的关键词，或检查网络连接到 ArXiv。

### Q: 论文分析失败？
A: 确保输入的是有效的 ArXiv URL 或 ID，格式如 `https://arxiv.org/abs/2301.00001`。

### Q: 写作助手响应慢？
A: AI 模型处理需要时间，请耐心等待。可以在 `.env` 文件中配置更快的模型。

### Q: 引用校验无法验证？
A: 尝试提供包含 DOI 的引用，或使用 ArXiv URL，这样可以自动验证。

## 配置

### 环境变量

在 `.env` 文件中配置：

```env
# AI 模型配置
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-3.5-turbo

# 数据库配置（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/innocore

# 向量数据库配置（可选）
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 模型选择

支持的模型：
- OpenAI: `gpt-3.5-turbo`, `gpt-4`
- ModelScope: 通过配置 `base_url`
- 其他兼容 OpenAI API 的模型

## 技术支持

- 查看日志: 服务器控制台输出
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 系统状态: 运行 `python verify_system.py`

## 更新日志

### 最新修复 (2025-11-23)
- ✅ 修复了所有 API 端点
- ✅ 集成真实 ArXiv API
- ✅ 添加 Crossref DOI 验证
- ✅ 实现 AI 辅助引用解析
- ✅ 优化前端 Markdown 渲染
- ✅ 添加复制功能
- ✅ 改进错误处理

## 下一步

1. 配置数据库以启用持久化存储
2. 配置向量数据库以启用语义搜索
3. 自定义 AI 模型配置
4. 探索 API 文档了解更多功能
