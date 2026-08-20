---
title: 计算机科学学习资源地图
description: 面向中文学习者的算法、系统、网络、数据库、编译器与工程实践资源
---

# 计算机科学学习资源地图

这是一份面向中文学习者的计算机科学资源清单，优先收录具备在线文档、源码、实验、自动评测或可复现实验的项目。它不试图替代教材，而是帮助你找到“读完之后可以动手做什么”的下一站。

资源大致分为三类：

- **课程实验**：适合按章节推进，通常有作业、测试和验收要求。
- **开源教程**：适合自学，内容持续更新，但需要自己安排节奏。
- **工程项目**：直接阅读真实系统或教学系统的源码，适合完成基础课程后深入。

## 先看这张路线图

| 目标 | 起点 | 进阶项目 | 主要产出 |
| --- | --- | --- | --- |
| 算法基础 | [OI Wiki](https://oi-wiki.org/) | 洛谷 / Codeforces 题库 | 题解、模板和复杂度分析 |
| 计算机系统 | [NJU 计算机系统基础](https://cs.nju.edu.cn/sufeng/course/ics/) | [NEMU / PA](https://ysyx.oscc.cc/docs/) | 模拟器、运行时和系统实验 |
| 操作系统 | [rCore Tutorial](https://rcore-os.cn/rCore-Tutorial-Book-v3/) | [ChCore Lab](https://sjtu-ipads.github.io/OS-Course-Lab/) | 可运行的教学内核 |
| 网络 | [清华 TCP Lab](https://lab.cs.tsinghua.edu.cn/tcp/doc/) | [清华 Router Lab](https://lab.cs.tsinghua.edu.cn/router/doc/) | TCP 协议栈、软件路由器 |
| 数据库 | [清华数据库实验](https://thu-db.github.io/dbs-tutorial/) | [MiniOB](https://oceanbase.github.io/miniob/db_course_lab/) / TinyKV | 存储、查询、事务和分布式 KV |
| 编译器 | [北大 Minic](https://pku-minic.github.io/online-doc/) | [中科大编译原理](https://ustc-compiler-principles.github.io/textbook/) | 从 SysY 到 RISC-V 的编译器 |
| 计算机组成 | [清华 COD Lab](https://lab.cs.tsinghua.edu.cn/cod-lab-docs/labs/) | [一生一芯](https://ysyx.oscc.cc/docs/) | CPU、SoC、RTL 和仿真 |
| 软件工程 | [清华软件工程文档](https://lab.cs.tsinghua.edu.cn/software-engineering/deploy/gitlab-ci) | Git4Edu / CI/CD 项目 | Git、测试、协作和部署流水线 |

## 算法与数据结构

### 首选资源

- [OI Wiki](https://oi-wiki.org/)：覆盖数据结构、图论、动态规划、字符串、数学、计算几何和竞赛工具；[学习路线](https://oi-wiki.org/contest/roadmap/)适合从基础开始安排顺序。
- [labuladong 算法教程](https://labuladong.online/zh/)：偏面试和题型框架，适合在掌握基本数据结构后集中训练。
- [洛谷](https://www.luogu.com.cn/)：题库和社区，适合把 OI Wiki 中的知识转化为可验证的代码。

### 学习方式

先理解数据结构和算法的正确性、复杂度与适用条件，再使用题库验证；不要把刷题模板当成算法理论本身。

## 计算机系统基础与 CSAPP

- [南京大学《计算机系统基础》](https://cs.nju.edu.cn/sufeng/course/ics/)：从数据的机器级表示、汇编、链接、程序执行到存储系统和 I/O；[实验页](https://cs.nju.edu.cn/sufeng/course/ics/lab.htm)包含配套编程实验。
- [一生一芯 / NEMU 文档](https://ysyx.oscc.cc/docs/)：从调试器、ISA 和 NEMU 开始，逐步进入运行时、RTL CPU、SoC 和系统软件。
- [NEMU ISA API 文档](https://ysyx.oscc.cc/docs/ics-pa/nemu-isa-api.html)：适合已经开始做 PA、需要查接口和调试行为时使用。

推荐顺序：`C 语言 → 汇编与链接 → NEMU/PA → 组成原理 → 操作系统`。

## 操作系统

- [rCore Tutorial Book v3](https://rcore-os.cn/rCore-Tutorial-Book-v3/)：Rust + RISC-V，从裸机启动、特权级、进程、虚拟内存到文件系统。
- [SJTU IPADS OS Course Lab](https://sjtu-ipads.github.io/OS-Course-Lab/)：基于 ChCore 微内核，偏 AArch64、微内核、多核、进程和 IPC。
- [uCore-Tutorial-Guide 2023S](https://learningos.cn/uCore-Tutorial-Guide-2023S/chapter0/index.html)：覆盖启动、物理/虚拟内存、进程、调度、文件系统和并发。
- [NJU OS Workbench](https://github.com/lxmwust/os-workbench)：以 xv6 为基础，包含虚拟化、持久化、文件系统和并发实验。
- [uCore 实验指导书](https://chyyuu.gitbooks.io/ucore_os_docs/content/)：清华早期 uCore 实验资料，适合补充 x86 和经典内核实现。

推荐顺序：`rCore 或 uCore → ChCore → Linux 内核子系统`。

## 计算机网络

- [清华 TCP 实验文档](https://lab.cs.tsinghua.edu.cn/tcp/doc/)：实现 TCP 网络栈，结合 RFC、日志、抓包和自动化测试。
- [清华 Router Lab](https://lab.cs.tsinghua.edu.cn/router/doc/)：软件路由器、IPv6、OSPF/RIPng、P4 和数据平面/控制平面。
- [清华计网联合硬件路由器实验](https://lab.cs.tsinghua.edu.cn/router/doc/joint/)：同时实现 CPU 和硬件转发引擎，适合做软硬件贯通实践。
- [中科大信息网络实验室课程](https://if.ustc.edu.cn/course/)：包含网络原理、组网、Linux 网络命令和 Internet 应用分析。

推荐顺序：`协议分层 → TCP Lab → Router Lab → P4 / DPDK / eBPF`。

## 数据库系统

- [清华数据库系统概论实验](https://thu-db.github.io/dbs-tutorial/)：从页式文件、缓存、记录、B+ 树到 SQL 解析和查询优化，逐步实现单用户关系数据库。
- [HuaDB 数据库内核课程实验](https://thu-db.github.io/huadb-doc/1-prepare/)：覆盖页面存储、缓存、故障恢复、查询解析、查询优化和查询处理。
- [OceanBase MiniOB](https://oceanbase.github.io/miniob/db_course_lab/overview/)：包含 LSM-Tree、查询引擎、事务引擎和性能测试，适合高年级本科生或初学数据库内核者。
- [PingCAP Talent Plan](https://github.com/pingcap/talent-plan)：覆盖 Rust/Go、分布式系统、分布式数据库和开源协作。
- [TinyKV 课程](https://github.com/talent-plan/tinykv)：从单机 KV、Raft 到分布式事务，适合进入数据库 infra。

推荐顺序：`SQL 与关系模型 → MiniOB/HuaDB → TinyKV → TiKV/TiDB 源码`。

## 编译原理

- [北大编译实践 Minic](https://pku-minic.github.io/online-doc/)：将 SysY 编译到 RISC-V 汇编，按词法、语法、IR、代码生成和优化逐步推进。
- [中科大《编译原理和技术》](https://ustc-compiler-principles.github.io/textbook/)：配套在线实验和评测，适合系统学习编译器构造。
- [南京大学编译原理课程](https://cs.nju.edu.cn/tiantan/courses/compiler-2023/index.html)：实现一个类 C 语言编译器，包含语义分析和优化实验。

推荐顺序：`形式语言 → Minic → LLVM IR → LLVM Pass / 后端`。

## 计算机组成原理与体系结构

- [清华计算机组成原理实验指导](https://lab.cs.tsinghua.edu.cn/cod-lab-docs/labs/)：SystemVerilog/Chisel、CPU 设计、仿真、测试和硬件调试。
- [一生一芯](https://ysyx.oscc.cc/docs/)：从 RV32/RV64 NEMU 到 RTL CPU、SoC 和流片准备。
- [中科大 COD Lab](https://soc.ustc.edu.cn/COD/)：课程理论与实验资料。
- [清华 CPU + Router 联合实验](https://lab.cs.tsinghua.edu.cn/router/doc/joint/)：将 CPU 设计和硬件网络转发结合起来。

推荐顺序：`数字逻辑 → 单周期 CPU → 流水线 → Cache/存储层次 → SoC`。

## 软件工程与工程实践

这个方向通常不是“实现一个内核”，而是把需求、设计、编码、测试、评审和部署组织成可重复的工程流程。

- [清华软件工程课程文档](https://lab.cs.tsinghua.edu.cn/software-engineering/deploy/gitlab-ci)：包含 GitLab、CI/CD、项目构建和部署配置。
- [南京大学软件工程实验](https://seg.nju.edu.cn/curriculums/Software_Engineering_%28Fall_2018%29/Experiment03)：覆盖需求、设计、协同开发和测试等课程实践。
- [Git4Edu](https://www.gitlink.org.cn/cmy4399/Git4Edu)：以 Course as Code 为核心，将讲义、实验、Issue、PR、Review 和 CI 组织成可演进的课程资产。
- [希冀软件工程实践平台](https://www.educg.net/se.html)：集成 GitLab、Docker、Kubernetes、代码审查、自动测试和持续部署。

推荐顺序：`Git/GitLab → 单元测试 → CI/CD → Docker → Kubernetes → 开源协作`。

## 分布式系统与云计算

- [PingCAP Talent Plan](https://github.com/pingcap/talent-plan)：国内较完整的分布式系统和分布式数据库学习路径。
- [TinyKV](https://github.com/talent-plan/tinykv)：适合通过实现 Raft、KV 服务和调度器理解分布式存储。
- [南京大学分布式计算实验室](https://dislab.nju.edu.cn/)：云边协同、分布式机器学习、云网络和大数据系统。
- [清华 MADSys](https://madsys.cs.tsinghua.edu.cn/)：并行/分布式系统、存储系统和 AI/大数据系统。

推荐顺序：`网络与 OS → RPC/一致性 → Raft → KV/事务 → 云原生系统`。

## 网络安全

- [CTF Wiki](https://ctf-wiki.org/)：覆盖 Web、Pwn、Reverse、Crypto、Misc、取证等方向。
- [CTF All in One](https://firmianay.gitbooks.io/ctf-all-in-one/content/)：从二进制、ELF、Linux 安全机制到常见 CTF 方向。
- [CUC CTF Wiki](https://cuccs.github.io/ctf-wiki/)：适合入门和配合题目练习。

安全实验只应在 CTF、靶场或明确授权的环境中进行。

## 计算机图形学

- [GAMES 在线课程平台](https://games-cn.org/kkk/)：集中收录 GAMES101、GAMES102、GAMES103、GAMES104 等课程，以及课件、视频和作业。
- [GAMES101 官方主页](https://sites.cs.ucsb.edu/~lingqi/teaching/games101.html)：从光栅化、几何表示、光线传播到动画与模拟，适合系统入门现代图形学。

推荐顺序：`线性代数/几何 → GAMES101 → GAMES102/103 → 实时渲染或离线渲染`。

## 机器学习与深度学习

- [动手学深度学习](https://zh.d2l.ai/)：数学、公式、图示、代码和 Jupyter 实验结合，适合建立机器学习和深度学习基础。
- [GAMES 课程平台](https://games-cn.org/kkk/)：除图形学外，也可作为视觉、动画和几何方向的公开课程入口。

如果目标是 AI Infra，建议不要只学模型 API，而是继续补齐 `组成原理 → OS → 网络 → 分布式系统 → GPU/并行计算`。

## 编程语言与系统编程

- [Rust 程序设计语言](https://course.rs/)：中文 Rust 学习路线，适合在 rCore、ChCore 或 TinyKV 前补齐语言基础。
- [The Rust Programming Language](https://doc.rust-lang.org/book/)：官方英文语言参考；中文学习可配合 [Rust 语言圣经](https://course.rs/) 使用。
- 编程语言理论、形式化方法和类型系统的中文开源实验资源相对分散；建议先从编译器、Rust 类型系统或 Lean/Coq 的官方文档进入。

## 建议的计算机专业主线

如果目标是底层系统或 AI Infra，可以按下面的顺序推进：

1. C/C++、Git、Linux、数据结构与算法。
2. CSAPP/NJU 计算机系统基础和 NEMU/PA。
3. 计算机组成原理：CPU、Cache、内存和 I/O。
4. 操作系统：rCore、uCore 或 ChCore。
5. 计算机网络：TCP、路由器、P4/eBPF。
6. 数据库：MiniOB/HuaDB，再到 TinyKV/TiKV。
7. 编译原理：Minic、LLVM 和编译优化。
8. 软件工程：测试、CI/CD、容器、代码评审和开源协作。

这条路线的关键不是把所有课程都“看完”，而是每个阶段至少留下一个能运行、能测试、能解释设计取舍的项目。

## 使用与维护说明

- 外部课程、代码和文档的版权归原作者或课程方所有；本页只做学习导航。
- 课程网址、版本和作业要求可能变化，开始学习前以项目官方页面为准。
- 本页适合作为网站中的资源索引；个人笔记、实验记录和复现结果应放在对应专题目录下。
- 建议为每个长期学习项目保留：`README`、运行环境、实验记录、测试结果和参考资料链接。

最后更新：2026-08-18
