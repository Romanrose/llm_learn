# 🎁 GiftGenius: 智能送礼助手

基于 HelloAgents 框架的多智能体协作系统，为你提供精准、走心的礼物推荐方案。

## 📝 项目简介

GiftGenius 是一个智能化的礼物推荐 Agent，旨在解决“送什么礼物”这个千古难题。它不仅仅是一个简单的关键词搜索工具，而是一个模拟人类决策过程的多智能体流水线 (Multi-Agent Pipeline)。

通过 军师 (策略制定) -> 猎人 (全网搜索) -> 编辑 (数据清洗与文案创作) 的分工协作，它能根据用户的 MBTI、星座、预算等个性化画像，从全网检索最新的商品信息，并生成一份图文并茂、价格透明的送礼指南。

- 解决什么问题？

   解决送礼时的选择困难症，以及推荐商品过时、价格超预算、文案枯燥等问题。

- 有什么特色功能？

   支持 MBTI/星座心理分析、自动比价与平替查找、防幻觉数据提取。

- 适用于什么场景？ 

  节日送礼、生日惊喜、纪念日策划等需要个性化推荐的场景。

## ✨ 核心功能

- [x] 精准画像分析：基于 MBTI 人格、星座、年龄等维度，深度解析受礼者的潜在偏好，制定个性化搜索策略。

- [x] 智能预算控制：支持自定义预算范围（如 "500-1000元"），并具备“价格守门员”机制，自动拦截超预算商品并触发降级搜索（找平替）。

- [x]  实时联网搜索：利用 Tavily 搜索引擎获取 2025年最新 的商品信息、价格和图片，拒绝过时推荐。

- [x] 可视化报告：最终生成包含商品图、价格参考、种草文案的 Markdown 表格，直观易读。

## 🛠️ 技术栈

- 框架: HelloAgents

- 智能体范式: 使用HelloAgent框架的SimpleAgent

- 工具与API:

  Tavily Search API (用于联网检索)、百度优选MCP(用于联网检索)

- 其他依赖: `mcp`, `nest_asyncio`, `python-dotenv`, `numpy`

## 🚀 快速开始

### 环境要求

Python 3.10+

Jupyter Notebook / Jupyter Lab

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥

复制配置文件模板：

```bash
# 创建.env文件
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```



### 运行项目

修改 user_profile.json 文件，填入你的送礼对象信息（如 MBTI、预算等）。

启动 Jupyter Notebook：

```bash
jupyter notebook main.ipynb
```
项目默认使用的是百度优选MCP，可修改为Tavily Search API。
```py
# 搜索源配置
# 可选值: "tavily" (通用/海外) 或 "baidu" (电商/国内)
os.environ["SEARCH_PROVIDER"] = "baidu" 
```


点击 "Run All" 运行所有单元格，最终结果将生成在 outputs/gift_plan_output.md 中。

## 📖 使用示例

输入配置 (user_profile.json):

```json
{
    "性别": "男",
    "年龄": "24岁",
    "MBTI": "ISTJ",
    "星座": "白羊座",
    "预算": "200-500",
    "节日": "生日",
    "自定义": "喜欢数码"
}
```

运行结果 (final_gift_plan.md):

![example](https://github.com/datawhalechina/hello-agents/blob/main/Co-creation-projects/jack6249-GiftGeniusAgent/example.png)

## 🎯 项目亮点

- 双流架构 (Dual-Stream)：将“硬数据搜索”（找价格）和“软文案生成”（找卖点）拆分为两条并行流水线，大幅减少了上下文干扰，提升了文案质量。

- 代码级防幻觉 (Code-based Guardrails)：不依赖 LLM 直接生成 JSON，而是通过 Python 正则表达式从搜索结果中暴力提取价格和图片，从根源上杜绝了“编造价格”的幻觉。

- 动态策略修正 (Feedback Loop)：实现了“价格守门员”机制。如果搜到的商品均价超预算，会重新触发“军师”制定“平替”策略，直到找到合适商品为止。

- 支持多数据源：集成了百度优选MCP 和 Tavily Search API 两种搜索源

## 🔮 未来计划

- [ ] 前端交互：新增前端页面，提供更好的用户交互体验

- [ ] 数据源深度集成：完全接入百度优选MCP 的比价与历史价格接口，获取更精准的实时价格和库存信息，实现“全网比价”功能。

- [ ] 丰富选项：增加更多的个人喜好选项，如喜欢的商品类型、品牌等


🤝 贡献指南

欢迎提出 Issue 和 Pull Request！如果你有更好的 Prompt 优化技巧或新的 Agent 模式想法，请随时分享。

📄 许可证

MIT License

👤 作者

GitHub: [@jack6249](https://github.com/jack6249)

🙏 致谢

感谢 Datawhale 社区 和 Hello-Agents 项目提供的优秀框架与教程支持！
