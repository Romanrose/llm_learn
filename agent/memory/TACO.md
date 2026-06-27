TACO/
├── src/harbor/          # 主要CLI源码
│   ├── agents/          # 代理实现
│   ├── environments/    # 执行环境
│   ├── cli/            # 命令行界面
│   └── ...
├── adapters/           # 基准测试适配器
├── apps/viewer/        # 结果查看器
├── docs/              # 文档网站
├── examples/          # 示例配置
└── tests/             # 测试套件


TACO/
├── src/harbor/agents/terminus_2/    # TACO核心实现
│   ├── compression/                   # 压缩框架模块
│   ├── terminus_2.py                 # 主代理实现
│   ├── output_filter.py              # 输出过滤器
│   └── tmux_session.py              # 终端会话管理
├── scripts/                          # 运行脚本
├── examples/                         # 示例配置和任务
└── tests/                            # 测试套件


CompressionRule (数据模型)
    ↓
CompressionPlanner (规划器) → CompressionPlan
    ↓
DynamicCompressionFilter (过滤器) → 过滤输出
    ↓
FeedbackCollector (反馈收集) → FeedbackSignal
    ↓
RuleEvolver (规则进化) → 新/替换规则
    ↓
RuleCache (规则缓存) → 跨任务持久化



压缩规则数据模型
	正则表达式
	压缩策略
	进化追踪

压缩规划器工作机制
	有缓存状态
	无缓存状态

动态过滤器
	初始化
	跳过判断
	过滤执行

反馈收集和规则进化
	反馈检测
		显式反馈
		分析文本启发式
		重试命令启发式
	规则进化机制
		生成替换规则
		生成新规则
		提升置信度
		新规则注入过滤器链

规则缓存和跨任务复用

AAAI 改进方向建议                                                                                                                                 

  我认为最有潜力的方向有以下几个，按可行性和新颖性排列：                                                                                            

  方向 A：压缩感知的层次化上下文管理                                                                                                                

  核心想法：TACO 的观测压缩和 Terminus 的 summarization 是独立的两套系统。将它们统一为层次化的上下文管理框架：                                      

  - L0: 单步观测压缩 (现有 TACO)                                                                                                                    

  - L1: 多步 episode 级摘要 (现有 summarization 但可以利用压缩信号优化)                                                                             

  - L2: 跨任务知识蒸馏 (规则缓存升级为结构化知识库)                                                                                                 

  论文价值：从"压缩单个输出"升维到"管理整个上下文生命周期"，故事更完整。                                                                            

  方向 B：基于任务奖励的压缩策略强化学习                                                                                                            

  核心想法：当前 self-evo 靠启发式反馈 (agent 是否抱怨)。改为用任务完成率作为奖励信号，训练一个轻量策略网络来决定：                                 

  - 每条输出的压缩激进程度                                                                                                                          

  - 是否需要 LLM 压缩                                                                                                                               

  - 哪些 pattern 该 keep/strip                                                                                                                      

  论文价值：从规则演化变成可学习的策略，理论上更优，且可以用 Harbor 现有框架做大规模实验。                                                          

  方向 C：输出预测 + 主动压缩                                                                                                                       

  核心想法：当前压缩是被动的                                                                                                                        

  (输出产生后再压缩)。加一个预测模块，在命令执行前预测输出类型和长度，主动选择压缩策略，甚至可以决定是否执行某些冗余命令。                          

  论文价值：从 reactive 到 proactive，减少不必要的 LLM 压缩调用，降低延迟和成本。                                                                   

  方向 D：信息论视角的安全压缩边界                                                                                                                  

  核心想法：给出数学形式化：定义观测 O、压缩后观测 O'、最优动作 A 之间的互信息关系，证明在什么条件下压缩不影响任务结果。用此理论指导压缩策略设计。  

  论文价值：AAAI 偏好有理论贡献的工作，这个方向可以提升论文的学术深度。