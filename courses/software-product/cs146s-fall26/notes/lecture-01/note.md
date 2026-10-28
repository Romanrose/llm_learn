# CS146S 第 1 讲：从对话模型到编程智能体

> 依据 2026-09-22 官方讲义整理核心概念，并补充实现思路与自测练习。未取得本讲录像或字幕，本文不复述课堂口头讲解。下方伪代码和练习由本站编写。

## 本讲讲了什么

第一讲通过小型编程智能体介绍课程主线：理解软件系统、提供有效上下文，以及在人与智能体之间组织开发工作。官方讲义用文件读取、目录枚举和文件编辑说明工具调用循环；课程重视可迁移的工程原则。[官方讲义，第 5、7、11–14 页](https://docs.google.com/presentation/d/1uztIhjHAG6O_9QOD1N_3wdhwhABml1fANXEN2dGwdbg/htmlpresent)

学习这一讲，可以先追问三个问题：模型为什么需要读取文件？工具由谁执行？怎样确认修改达到了需求？

## 1. 把系统拆成三个边界

| 部分 | 输入 | 输出 | 实现时应检查 |
| --- | --- | --- | --- |
| 模型 | 用户目标、上下文、工具说明 | 回答或结构化工具请求 | 请求能否解析，工具是否存在 |
| 工具执行器 | 工具名与参数 | 执行结果或错误 | 参数、权限、文件路径与实际结果 |
| 控制循环 | 模型响应、执行结果与任务状态 | 下一轮输入或停止状态 | 是否继续、是否超出预算、是否需要用户决策 |

模型生成工具请求后，宿主程序执行操作，再把结果交回模型。Claude Code 的官方说明将收集上下文、行动和验证描述为相互衔接的循环。[Claude Code 架构说明](https://code.claude.com/docs/en/how-claude-code-works)

**实现推论：**一次“准备编辑文件”的模型回答，只能证明它提出了行动；文件是否真的改变，必须由执行器结果和最终差异证明。

## 2. 最小循环应留下什么证据

下面是本站编写的概念伪代码，省略具体模型 API；它不是课程源码，也不能直接作为可运行客户端。

```python
messages = [user_goal]

for step in range(step_limit):
    reply = model.generate(messages, tool_definitions)
    messages.append(reply)

    if reply.tool_calls:
        for call in reply.tool_calls:
            if not allowed(call):
                result = error("tool request rejected")
            else:
                result = execute_with_timeout(call)
            messages.append(tool_result(call.id, result))
        continue

    return {"state": "model_finished", "reply": reply.text}

return {"state": "step_limit_reached"}
```

注意最后两种返回状态并不等价。模型结束对话，仍需对照任务的验收条件；步数耗尽，更应保留失败现场。对于支持工具调用的具体 API，还要遵循它的消息格式、请求标识和工具结果配对规则。

## 3. 自测：一次文件修改的证据链

假设练习目标是给一个示例项目的 README 增加安装说明。下面的验收表由本站设计，不是官方作业。

| 观察 | 可以得出的结论 | 尚不能得出的结论 |
| --- | --- | --- |
| 模型请求读取 README | 它试图了解现有文档 | 已理解安装要求 |
| 读取返回“文件不存在” | 当前路径不正确或文件缺失 | 应立即新建文件 |
| 编辑器报告成功 | 编辑动作已执行 | 内容正确、链接有效 |
| 差异仅包含预期说明 | 修改范围符合预期 | 安装命令已经运行成功 |
| 在干净环境验证安装步骤 | 这组步骤在该环境可行 | 所有平台都兼容 |

建议先用一个临时小项目观察完整过程，逐轮记录工具名、执行结果和下一步决策。故意制造一次文件缺失或工具超时，检查错误能否清楚地返回，而不是让模型把失败当成成功。

## 4. 为什么先做小型实现

Anthropic 对工作流与智能体的区分是：前者主要由预设代码路径组织，后者让模型动态决定过程和工具使用。[架构背景阅读](https://www.anthropic.com/research/building-effective-agents)

对本讲练习的启发是：固定的格式检查仍可以是普通脚本；需要根据错误信息选择下一步时，再观察模型如何参与决策。先把这些边界看清楚，更容易解释复杂工具出现故障时究竟是哪一层出了问题。

## 课程练习入口与资料状态

[官方讲义第 9 页](https://docs.google.com/presentation/d/1uztIhjHAG6O_9QOD1N_3wdhwhABml1fANXEN2dGwdbg/htmlpresent)列出六份练习、开源贡献和期末项目，并给出[官方作业 GitHub 仓库](https://github.com/mihail911/modern-software-dev-assignments)。作业版本和截止日期请结合[官方日历](https://docs.google.com/document/d/1W11sWBigWIsi9wVIhhFx3wajIEnP0Qfb-ei8Ecf5VKU/edit)确认。

官网另有 [Completed code 文件](https://drive.google.com/file/d/1DxKa_autBOu9s8DvItodgUAwH_pBg7aR/view)，文件名为 `coding_agent_from_scratch.py`。本次只确认其公开预览入口，未读取到源码正文，也没有运行它。官网未列出第 1 讲逐字稿；第 2 讲及补充视频的文字不能充当本讲逐字稿。
