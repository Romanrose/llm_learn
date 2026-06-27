# DataAnalysisAgent - 智能数据分析助手

> 基于HelloAgents框架的智能数据分析工具

## 📝 项目简介

DataAnalysisAgent是一个智能数据分析助手,能够自动分析数据、生成可视化图表、撰写分析报告。

### 核心功能

- ✅ 数据分析：统计数据变化趋势，选用合适图表等
- ✅ 智能建议：基于LLM提供可视化图表代码和分析报告
- ✅ 报告生成：生成Markdown格式的分析

## 🛠️ 技术栈

- HelloAgents框架（SimpleAgent）
- Python AST模块（代码解析）
- OpenAI API（智能分析）

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置LLM参数

**方式1: 使用.env文件(推荐)**

```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件,填入你的配置
# LLM_MODEL_ID=Qwen/Qwen2.5-72B-Instruct
# LLM_API_KEY=your_api_key_here
# LLM_BASE_URL=https://api-inference.modelscope.cn/v1/
```

**方式2: 直接在Notebook中设置(已配置)**

项目已在`main.ipynb`中预配置了ModelScope的API,可以直接使用。如需修改,编辑第1部分的配置代码:

```python
os.environ["LLM_MODEL_ID"] = "your_model"
os.environ["LLM_API_KEY"] = "your_key"
os.environ["LLM_BASE_URL"] = "your_api_url"
```

### 运行项目

```bash
jupyter lab
# 打开main.ipynb并运行所有单元格
```

## 📖 使用示例

### 快速体验

打开`main.ipynb`,运行「第0部分：快速演示」,即可快速了解项目功能。

### 完整功能

1. 将待分析数据表格放入`data`
2. 依次运行`main.ipynb`
3. 查看生成的图表`outputs/echarts.html`
4. 查看生成的数据分析报告`outputs/report.md`



## 📂 项目结构

```
jjyaoao-CodeReviewAgent/
├── README.md              # 项目说明文档
├── requirements.txt       # 依赖列表
├── .gitignore            # Git忽略文件
├── .env.example          # 环境变量示例
├── main.ipynb            # 主程序(包含快速演示和完整功能)
├── data/
│   └──    # 示例代码
└── outputs/
    └── report.md  # 数据分析报告
    └── echarts.html  # 图表html
```

## 🔧 技术实现

### 工具系统

1. **DataCleaningTool**: 数据清洗工具 - 基于用户指定规则清洗表格数据
2. **DataStatisticsTool**: 数据统计工具 - 提供描述性统计分析

### 智能体设计

使用HelloAgents的SimpleAgent,配合自定义工具实现智能代码审查。

```

## 🙏 致谢

感谢Datawhale社区和Hello-Agents项目！

