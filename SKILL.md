---
name: cooperation-skill
description: 多 agent 协作框架(Architect 出卡/裁决/审核 + Implementer 红线内自主实现 + 可选 Reviewer 合入前实测验收与合入)。用于部署协作协议、派卡、处理阻塞与实施发现、审核、验收合入;支持共享目录、独立 clone、本地并行 worktree 及 Multica 托管任务的每轮起点保护。
---

# 多 agent 协作框架

一句话:**开发环节只有 Architect 与 Implementer 两方**——Architect 出卡(目标 + DoD + 红线,不写实现步骤)、裁决阻塞、审核交付;Implementer 在红线内自主实现。**Reviewer(可选)守合入口**:审核通过后实际跑起来验收,通过则合入主干。Owner(人类)决策与触发。全员通过仓库内消息异步协作。

```
出卡 → 实现 ⇄ 裁决(L1) → 交付 → Architect 审核(通过/打回) → Reviewer 实测验收 → 合入
       └──────────── 开发环节:Architect + Implementer ────────────┘   └─ 合入口:Reviewer ─┘
```

**每轮先确认工作区,再执行角色手册。** 本地并行 worktree 为形态 C;Multica 的目录、分支和本轮起点由宿主分配。遇到 C 或 Multica,先读 [本地 worktree 工作流](references/local-worktrees.md),并在任何 Git 写操作前执行其中的 guard `start`。沿起点追加提交,不 amend 宿主 checkpoint、不按旧模板重建分支。已部署项目也要走这一步。

**Reviewer 是可选角色**——两个 agent 的项目不部署它,验收与合入回落 Architect,框架退化为双 agent 原形。两个 agent 若异源且都具 Architect 能力,可互为代行者(protocol §1.1)。

## 文件地图

| 文件 | 内容 | 谁读 |
| --- | --- | --- |
| `protocol.md` | 共同协议:角色、代行、生命周期、审核与验收止损、验收强度、信道、形态 A/B/C 与宿主约束、L1-L3、绿区/红区、打回与退回依据、工程规约 | 全员必读 |
| `references/local-worktrees.md` | C 模式与 Multica:每轮起点、消息收发、确定 SHA 审核/验收、串行集成、失败恢复、旧部署迁移 | C / 托管任务必读 |
| `scripts/worktree_guard.py` | Python 3 标准库工具:只读探测、一次性记录起点、交付前检查 | C / 托管任务开工与交付时 |
| `architect.md` | 出卡(写目标与红线)、出卡自查、派卡、信道分流、裁决、审核、移交验收、退回定性 | Architect |
| `implementer.md` | 领卡、红线内自主实现、自检、交付报告、打回处理 | Implementer |
| `reviewer.md` | 验收测试(按强度分档)、退回依据、合入收口序列、漏检回流 | Reviewer;双 agent 时由 Architect 执行 |
| `anti-patterns.md` | 反模式池(历史教训,持续追加) | 全员 |
| `templates/` | channel 骨架、开发/内容任务卡模板、Implementer / Reviewer 启动提示词模板 | 部署时用 |

## 新项目部署流程(Architect 侧执行)

关键认知:**其他 agent 读不到本 skill 目录**——它们只读项目仓库和自己的启动提示词。所以部署 = 把协作基础设施**实例化进项目仓库**;本 skill 是母本 + 部署器。

1. **定角色数与模型来源**:问 Owner 有几个 agent、**分别是什么模型**。两个 → 双 agent 原形(Architect 兼验收合入);三个 → 加 Reviewer 守合入口。角色分工与各方模型来源记入信道存档——Reviewer 与开发两方是否同源,决定验收的独立程度(protocol §1.2);
2. **定配置**(按已授权上下文与项目实情):信道位置、分支来源、项目门禁命令表(protocol §8)、体量预算基线、注释/文案语言、**唯一集成人**(三方为 Reviewer,双方为 Architect);C 模式还需登记发送分支、主干更新入口;
3. **定工作区形态与管理者**:按 protocol §4 的只读拓扑探测区分 A(共享目录)、B(独立 clone)、C(本地并行 worktree),并记录 manual / multica。不能把「看不到未提交消息」直接判为 B。Reviewer 的独立 worktree 同样按 C 收发消息;
4. **实例化进仓库**:A/B 使用 `templates/channel.md`;C 使用 `templates/channel-worktrees.md` 建部署配置,消息使用 `templates/message.md`。拷贝 `protocol.md`、`implementer.md`、`reviewer.md`(双 agent 时由 Architect 执行验收合入)、`anti-patterns.md` 进项目(如 `docs/collab/`),填掉项目配置;推荐同时拷贝 `architect.md`。C / 托管部署还要拷贝 `references/local-worktrees.md`、`scripts/worktree_guard.py` 及其引用的两个模板,保持相对目录结构,并在项目配置明确实际脚本路径;
5. **给 Owner 出启动提示词**:按 `templates/implementer-bootstrap.md`(三方再加 `templates/reviewer-bootstrap.md`)填空,交 Owner 配置给对应 agent——只指路径不复制内容;
6. **写部署宣告**,按已选通路送达并收显式确认,完成消息通路验证;
7. 建 backlog(若无)→ 出第一张卡(`architect.md` §1)→ 协作开始。

**部署时要讲清楚的三件事**(不讲清楚必出事):

1. **卡面写什么、不写什么**:写目标、DoD、红线;不写实现步骤。Implementer 在红线内自主决定,值得知道的决策交付时披露——**放权靠的是红线清楚,不是卡面写满**(architect.md §1.2、protocol §6);
2. **开发环节两方闭环**:L1 直达 Architect,交付由 Architect 审核;Reviewer 不预审、不跟进、不需要抄送裁决,移交验收时拿最终卡面与裁决清单(architect.md §5);
3. **退回走 Architect**:Reviewer 的退回须有依据 + 复现,发给 Architect 定性(返工还是改卡),不直接指挥 Implementer;Reviewer 有 merge 权,无契约修改权(protocol §6)。

**代行要在断线之前定好**(protocol §1.1):agent 因限额或上下文耗尽而中断是常态。部署时就把代行者、代行期权力边界(**裁决算数;审核与合入不能落在同一 agent 上**)、待合入队列的链式基线规则写进信道存档。

**审核与验收都要设闸**(protocol §2.1、§2.2):一次给全、只打回有依据的、轮次封顶、三个越线信号;backlog 每张卡标验收强度,对抗档在出卡时点名。这两个环节没有自然终点,不设闸各方都会不自觉地加码。

## 日常路由(已部署项目中)

- C / Multica / `local_directory worktree` 报错:先读 `references/local-worktrees.md`;每轮 `start`,交付前 `check`,失败保留现场。不能用新 `run_id` 掩盖原运行的起点丢失;
- 旧项目切换本地并行 worktree:按参考文档的「旧部署迁移」更新实例与启动提示词,不能只改母本;
- **旧项目迁移到本版流程**(Reviewer 从开发期评审改为合入口验收):更新项目实例的 protocol / 三份手册 / 卡片模板 / 启动提示词,把唯一集成人改为 Reviewer,在信道宣告生效点;在途卡按旧流程走完,新卡按新流程;
- 我是 Architect:出卡/派卡 → `architect.md` §1;L1 → §3 裁决;交付报告 → §4 审核;审核通过 → §5.1 移交;验收退回 → §5.2 定性;未部署 Reviewer 时验收合入 → `reviewer.md` §2–§4。
- 我是 Implementer:领卡 → `implementer.md` §1;实施 → §2;交付 → §3–§4;打回 → §5。
- 我是 Reviewer:收到移交 → `reviewer.md` §1–§2(**先看卡面强度档**);出结论 → §3;合入 → §4。
- **接手代行 / 交回**:→ `protocol.md` §1.1——代行者权力边界、待合入队列与链式基线、交接对账消息;**半途卡不换手**。
- 需要给其他 agent 指引时:指向**项目仓库内的实例文档**,不指向本 skill 路径(它们读不到)。**例外**:若其他 agent 自己也能加载本 skill(各自的 skills 目录里有同一份母本),则不必实例化协议文档,直接共享母本——单一事实源、无实例漂移;代价是母本里的【坑位】没有落点,门禁命令表、路径与形态必须改由信道存档或项目内的指引文档承载,部署时要点名放在哪。
- 拿不准某规则 → `protocol.md`;疑似踩坑 → `anti-patterns.md` 先查有没有前车之鉴。

## 经验回流

新项目跑出的新教训(出卡自查新增项、反模式、裁决先例)先落项目实例文档,由 Owner 触发回流本母本——母本是跨项目资产,实例是项目现场。两处都改时先实例后母本,防漂移。
