---
title: "agent 工程学习总结"
date: 2026-03-31
categories:
  - agent
description: "记录我对 agent、多 agent 和 harness 的理解"
---

## AGENTS.md 是什么？
在 Codex 和 Claude Code 中，AGENTS.md 会在会话启动时自动注入上下文，因此通常无需显式要求 agent 先阅读；但最终生效内容取决于目录层级、覆盖关系和大小限制。

## agent的问题是什么？
- 上下文太长会导致焦虑
- 对自己的评价不够客观

## 多 agent 的相比单 agent 的优势是什么？
- 通过任务划分减少上下文的干扰，让每个 agent “窄而专”而不是“万能”
- 使用一个 agent 评价其他 agent 会更客观（如开发和测试）
- 任务是有层次的，可以让不同agent处理不同层次的任务（如管理和开发）
- 没有相互依赖关系的子任务可以并行处理（如多个开发之间）

## 利用多 agent 进行开发的原则有哪些？
- 把仓库变成 agent 能读懂的“系统事实源”。AGENTS.md 应该是目录，不该是百科全书；深层知识要拆到架构文档（ARCHITECTURE.md）、设计文档（DESIGN.md）、产品规格（product-specs/）、可靠性（RELIABILITY.md）/安全（SECURITY.md）规则、执行计划（exec-plans/）里，并且全部版本化、可链接。
- 协作模式优先用“agent-as-tool / hub-and-spoke”模式，让一个主 agent 统一规划、分派和汇总；handoff 更适合开放式对话流，但全局控制会更弱。
- 把上下文当稀缺资源管理。多 agent 最大风险不是“算力不够”，而是上下文污染/腐化。主线程只保留需求、约束、决策和最终结论；探索日志、测试输出、堆栈、检索过程交给子 agent 消化后再摘要返回。
- 把长任务先写成“活文档”。ExecPlan/PLANS.md 的最佳做法是：自包含、对新手可执行、持续更新、记录决策、按 milestone 推进，并且验证步骤不是可选项。
- 子任务必须“有界”，一个好的 subagent prompt 要明确怎么拆分、是否等待全部完成、最后返回什么格式的摘要；否则主线程会被噪音淹没。
- 并行开发要做隔离。多个活跃线程不要在同一工作副本上改同一批文件；用 git worktrees 把任务隔离开，必要时再 handoff 到本地主工作区。
- 把重复流程沉淀成技能和自动化。原则很清楚：skills 定义“方法”，automations 定义“调度”。先把流程手工跑稳定，再自动化；不要反过来。
- 多 agent 系统要有“垃圾回收”。agent 会复制仓库里已有模式，所以要把团队偏好和质量标准编码成 golden principles，并定期让后台 agent 扫描偏差、修复技术债、更新质量评分。
- 要警惕过度工程化，只在 agent 确实犯过的错误上投入 Harness，不要预防性的解决还未出现的问题。
- 评估器要把主观的好坏变为可打分的具体维度。通过文件的方式让生成器和评估器协商迭代达到一致，输出迭代合同（功能 + 验收标准），生成器按照合同构建，评估器按合同验收
- Harness 中的每一个组件都应该是可拆卸的，Harness 中的每一个组件都编码了一个假设，“模型自身做不好这件事”，这些假设需要被压力测试，因为它们可能是错的，也可能随着模型进步而过时

## 一个基于多 agent 的开发项目一般采用什么目录结构？
```text
repo/
├── AGENTS.md
├── ARCHITECTURE.md
├── DESIGN.md
├── SECURITY.md
├── RELIABILITY.md
├── product-specs/
│   ├── feature-a.md
│   └── feature-b.md
├── exec-plans/
│   ├── feature-a-plan.md
│   └── migration-b-plan.md
├── docs/
│   ├── decisions/
│   ├── runbooks/
│   └── code-review.md
├── evals/
│   ├── cases/
│   └── rubrics/
├── .agents/
│   └── skills/
│       ├── pr-review/
│       │   └── SKILL.md
│       ├── bug-triage/
│       │   └── SKILL.md
│       └── release-note/
│           └── SKILL.md
└── .codex/
    ├── config.toml
    └── agents/
        ├── coordinator.toml
        ├── explorer.toml
        ├── reviewer.toml
        └── implementer.toml
```

## 如何在 codex 中让一个 agent 调用 subagent ？
只需要对agent说“使用 spawn 生成 subagent”即可生成一个子对话窗口

## 如何才能让 agent 独立运行更久？
关键不是单纯把任务一股脑丢给它，而是把任务组织好。agent 想要稳定地独立运行更久，通常需要执行计划、会话管理、子任务拆分、工作区隔离和结果验证这些配套方法；这些事很多本身也可以由 agent 来做，但前提是系统先把这些能力设计出来。否则任务一旦变长，上下文、噪音和偏航风险也会一起增长。
