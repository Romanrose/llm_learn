# 2026 年 10 月目录迁移

按用户要求整理实际文件夹，并重写主分支 README。网站、catalog 和 workflow 保留唯一入口，课程源文件按首页四个方向集中保存；第三方项目和其他阅读归入配套资料。

## 路径对照

| 旧路径 | 新路径 |
| --- | --- |
| `infra/cs61a-fall26/` | `courses/foundations/cs61a-fall26/` |
| `infra/cmu-15213-fall26/` | `courses/foundations/cmu-15213-fall26/` |
| `infra/cmu-15213-fall15/` | `courses/foundations/cmu-15213-fall15/` |
| `infra/cs149-fall25/` | `courses/foundations/cs149-fall25/` |
| `llm/cs224n-winter26/` | `courses/models-agents/cs224n-winter26/` |
| `llm/cs336-2026/` | `courses/models-agents/cs336-2026/` |
| `agent/cmu-11768-fall26/` | `courses/models-agents/cmu-11768-fall26/` |
| `agent/cs329z-fall26/` | `courses/models-agents/cs329z-fall26/` |
| `agent/harvard-cs2680-fall26/` | `courses/models-agents/harvard-cs2680-fall26/` |
| `llm/cs224r-sp26/` | `courses/models-agents/cs224r-sp26/` |
| `llm/mit-6s184-2026/` | `courses/models-agents/mit-6s184-2026/` |
| `interest/software-engineering/mit-6102-sp26/` | `courses/software-product/mit-6102-sp26/` |
| `interest/product/uva-digital-product-management/` | `courses/software-product/uva-digital-product-management/` |
| `interest/design/cs147-fall26/` | `courses/software-product/cs147-fall26/` |
| `interest/design/cs329x-fall26/` | `courses/software-product/cs329x-fall26/` |
| `interest/design/berkeley-ux-ai-sp26/` | `courses/software-product/berkeley-ux-ai-sp26/` |
| `infra/jhu-robot-learning-fall26/` | `courses/robotics-hardware/jhu-robot-learning-fall26/` |
| `infra/mit-65940-fall26/` | `courses/robotics-hardware/mit-65940-fall26/` |
| `infra/cornell-ece4760-current/` | `courses/robotics-hardware/cornell-ece4760-current/` |
| `agent/hello-agents/` | `references/agents/hello-agents/` |
| `agent/memory/` | `references/agents/memory/` |
| `agent/tencentdb-agent-memory-tutorial/` | `references/agents/tencentdb-agent-memory-tutorial/` |
| `infra/network/` | `references/engineering/network/` |
| `papers/30-paper-zhCN/` | `references/papers/30-paper-zhCN/` |
| `interest/语言学概论/` | `references/interests/语言学概论/` |

## 更新已有本地克隆

先提交、备份或暂存自己的本地修改，再更新主分支。Git 会迁移受版本控制的文件，但本地未跟踪或被忽略的候选稿、`.env`、下载缓存和音视频不会自动完成归位；按上表核对后自行移动。不要用清理命令删除旧目录里的本地内容。

此次远程迁移基于已发布主分支，在独立工作目录中完成；原本工作目录里的草稿和运行环境保留原位。四套此前仅有 catalog 的课程补建最小 README 入口，不补造课堂内容。

## 校验范围

- 19 套课程的 `paths` 与源码目录、元数据中的本地来源和公开 `outputs`。
- `website/course.yaml` 中的首页课程及历史版本关系。
- GitHub README 的相对链接、生成脚本路径与 PDF 导出来源。
- 构建前后的公开课程路由、资源 URL 与已发布正文数量。

课程 ID、讲次 ID、网站 URL、外链和审核状态保持不变；生成页面和本地运行产物不随迁移提交。维护时运行 `npm run validate:structure` 和 `npm run build`。
