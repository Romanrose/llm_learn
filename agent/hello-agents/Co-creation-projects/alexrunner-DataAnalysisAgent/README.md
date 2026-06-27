# 商品销售数据分析智能体

> 针对商品销售数据分析场景，设计了专业的数据分析智能体，支持自动化数据分析、生成可视化图表并生成专业的商业分析报告。

## 📝 项目简介

- 商品销售场景存在数据分析难度大，人工分析耗时长，总结报告不规范等问题。本项目提出的智能体可以一键自动化分析商品销售数据，并生成图文并茂的深度分析报告，不仅提升了分析质量，还大幅缩短时间成本。
- 商品销售数据分析智能体支持深度捕获数据关联，提出多个关键的分析任务；支持调用数据分析工具，高效计算不同数据的关联，并生成可视化图表；最后综合每个分析任务的结果，给出深度分析报告。
- 使用于包含复杂商品销售数据的深度分析和商业咨询场景。

## ✨ 核心功能

- [x] 功能1：快速捕获关键信息，提出多个关键的分析任务。
- [x] 功能2：使用数据分析工具，深度分析数据关联，给出任务结论。
- [x] 功能3：自动生成高质量的图文并茂的分析报告。

## 🛠️ 技术栈

- 基于HelloAgents框架开发。
- 使用的智能体范式如下：
    - 项目整体采用 ** Plan-and-Solve ** 架构，先构造 Plan 智能体进行数据分析多任务规划，再构造 Analysis 智能体调用工具进行数据分析，最后构造 Report 智能体，综合每个任务结论给出格式化的分析报告。
    - Plan 智能体和 Analysis 智能体都采用 ReAct 架构。对于 Plan 智能体，需要多步思考并调用数据探查工具，最终确定多个子任务。对于 Analysis 智能体，需要多步思考并调用不同的数据分析工具。
    - Report 智能体采用简单无工具调用智能体，根据所有任务结论输出格式化报告。
- 使用的工具和API：
    - 数据探查工具和数据分析工具均为已实现的 Python 封装函数。
    - 无外部工具和API调用。

## 🚀 快速开始

### 环境要求

- Python 3.10+

### 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source ./venv/bin/activate
# 安装依赖
pip install -r requirements.txt
```

### 配置API密钥

```bash
# 创建.env文件
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# OPENAI_API_KEY=your_key_here
```

### 运行项目

```bash
# 启动 main.py
python3 ./main.py
# 输出报告路径为 out/analysis_report.md
```

### 测试单个智能体
```bash
# 在 main.py 同级路径运行测试脚本
python3 -m agents.test_planning_agent
```

## 📖 使用示例

### 代码示例

任务规划智能体示例代码：

```python
from hello_agents import HelloAgentsLLM

from agents.react_agent import NewReActAgent
from agents.agent_prompts import PLAN_AGENT_PROMPT
from tools.data_exploration import create_data_exploration_registry


if __name__ == "__main__":
    llm = HelloAgentsLLM()
    registry = create_data_exploration_registry()
    planning_agent = NewReActAgent(
        name="PlanningAgent",
        llm=llm,
        custom_prompt=PLAN_AGENT_PROMPT,
        tool_registry=registry,
        max_steps=5
    )

    question = "请开始分析"
    try:
        plan_result = planning_agent.run(question)
        print(f"任务规划: {plan_result}")
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
```

### 运行结果

结构化报告（部分删减版本）：

```markdown
# 执行摘要
本报告整合了客户细分、产品表现及订阅忠诚度等多维度分析。核心发现包括：**青少年客户展现出最高的消费能力，而服装品类是各群体的绝对偏好**；**秋季是销售旺季，但当前的订阅计划未能有效提升客户忠诚度与消费水平**。

## 详细分析

### 发现一：客户消费偏好与能力存在显著的年龄与性别差异
客户细分分析揭示了不同群体的独特行为模式。从性别看，女性平均消费（60.25美元）略高于男性（59.54美元），但两者在品类偏好上高度一致，均最青睐服装品类（占比约44.5%）。从年龄看，消费能力和次级偏好差异显著：**青少年（<20岁）平均消费最高（60.53美元）**，而40-49岁群体消费最低（58.49美元）。品类偏好上，20岁以下及20-29岁群体最偏好服装（~46%），而30-39岁及老年（60+）群体则最偏好配饰（~34%），50-59岁群体对鞋类的偏好最高（18.4%）。交叉分析进一步显示，在特定年龄段性别差异明显，例如老年女性消费（61.40美元）显著高于老年男性（58.65美元）。

![图1：各年龄段平均购买金额对比](figures/average_spending_by_age_group.png)
*图1：青少年（<20）平均消费最高，40-49岁群体消费最低。*

![图2：不同性别客户的品类偏好分布](figures/category_preference_by_gender.png)
*图2：男性和女性客户的品类偏好结构高度相似，服装均为首要选择。*

## 结论与建议
**结论**：业务的核心驱动力在于以服装为主的品类结构和具有高消费潜力的年轻客群（尤其是青少年），销售受季节影响显著。然而，旨在提升忠诚度的订阅计划目前并未产生预期效果。

**具体行动建议**：
1.  **深化年轻客群运营**：针对消费能力最强的青少年及20-29岁客群，设计专属的营销活动与产品组合，强化其在核心品类（服装）上的偏好，并尝试引导其对配饰、鞋履等品类的消费。
```

## 🎯 项目亮点

- 亮点1：使用 Plan-and-Solve 和 ReAct 混合架构，其中 Plan-and-Solve 统领全局，ReAct 架构负责底层实现。这种混合架构既将任务规划和任务执行解耦，又增强了每个模块的分析能力。
- 亮点2：重写 ReAct 底层代码，通过 prompt 约束使其输出 json 格式，提高了关键词提取的成功率。在达到最大步数后，要求大模型根据历史信息一次性生成分析结论，而不是直接返回错误，提高了整体分析效率。
- 亮点3：详细设计了 Plan, Analysis 和 Report 智能体的提示词，使其可以高效工作。并且为每个智能体设计了测试文件，方便调试。

## 🔮 未来计划

- [ ] 待实现的功能1：增加 note 工具，记录每个子任务的分析进度和结论，方便问题排查。
- [ ] 待实现的功能2：增加 SQL 数据库工具，支持读取线上数据库信息作为原始输入。
- [ ] 待优化的部分：目前实现的数据分析工具都是基于特定数据集的固定函数，如果数据集变动则无法使用。需要改进数据分析工具，提高泛用性。

## 🤝 贡献指南

欢迎提出Issue和Pull Request！

## 📄 许可证

MIT License

## 👤 作者

- GitHub: [@Alexyali](https://github.com/Alexyali)
- Email: wjhuang188@foxmail.com

## 🙏 致谢

感谢Datawhale社区和Hello-Agents项目！
