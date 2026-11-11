---
name: cooperation-skill
description: 多 agent 协作框架(Architect 设计/批量出卡/裁决/收官 + Implementer 自主实现 + 可选 Coordinator 派卡与卡级门禁 + 可选 Reviewer 里程碑验收与主干合入)。用于部署协作协议、出卡派卡、处理提案与阻塞、卡级门禁、里程碑验收、收官自迭代与 Owner 交付报告;支持共享目录、独立 clone、本地并行 worktree 及 Multica 托管任务的每轮起点保护。
---

# 多 agent 协作框架

一句话:**Architect 只在里程碑两头出场**——开头批量出薄卡(目标 + 完成判据 + 本卡约束),结尾做收官评估并签发给 Owner 的交付报告;中间 **Implementer 自主实现**(绿区直接做、黄区提案并继续、红区才停),**Coordinator(可选)派卡、逐卡过机械门禁并集成、记账**,**Reviewer(可选)在里程碑末把整体跑起来验收并合入主干**。Owner 只裁决真正属于他的事,其余问题在交付前自己迭代掉。

```
每张卡:  派卡 → 细化判据 → 实现 ⇄ 提案/裁决 → 交付 → 卡级门禁 → 合入集成分支
         Coord.  Implementer ──────────────────────┘  Coordinator ─────────┘
里程碑:  设计/ADR → 批量出卡 →〔逐卡循环〕→ 里程碑验收 → 收官评估 ⇄ 自迭代 → 合入主干 → Owner 报告
         Architect ─────────┘              Reviewer     Architect           Reviewer   Architect
```

**每轮先确认工作区,再执行角色手册。** 本地并行 worktree 为形态 C;Multica 的目录、分支和本轮起点由宿主分配。遇到 C 或 Multica,先读 [本地 worktree 工作流](references/local-worktrees.md),并在任何 Git 写操作前执行其中的 guard `start`。沿起点追加提交,不 amend 宿主 checkpoint、不按旧模板重建分支。已部署项目也要走这一步。

**Coordinator 与 Reviewer 都是可选角色**:未部署 Coordinator 时派卡记账归 Architect、卡级门禁归 Reviewer;未部署 Reviewer 时验收与主干合入归 Architect;都没有就是双 agent 原形(protocol §1)。

## 四个要先讲清楚的设计

1. **内容链路与控制链路分开**(protocol §1):设计 → 卡面 → 实现 → 验收这条链上不放转述者。Coordinator 可以用便宜的模型,正因为它不碰内容——派卡、记账、对着封闭清单过门禁,都不需要判断;卡面永远出自 Architect;
2. **检查分三层,各管一件事**(protocol §2):卡级门禁每张卡都做,只查能机械判定的;里程碑验收把整体实际跑起来;收官评估看结构并给每个问题归类。代价是常规卡的实测推迟到里程碑末,所以**里程碑要切小**,对抗档与取证档的卡仍逐卡验收;
3. **决策按回退成本分层**(protocol §6):回退只动本卡代码 → Implementer 直接做;回退封在本卡内 → 提案并继续;会外溢或不可逆 → 停下等裁决;产品方向、主观体验、已批准的契约、花钱 → Owner。**有客观依据且修法清楚的问题,任何一层都不往上交**;
4. **规则按执行者档位取用**(protocol §1.3):正文按强模型写。Implementer 是较弱模型时登记为保守档,叠加 `profiles/guarded.md`——黄区并入红区、Architect 写全卡面、逐卡审核。

## 文件地图

| 文件 | 内容 | 谁读 |
| --- | --- | --- |
| `protocol.md` | 共同协议:角色与两条链路、代行、执行者档位、生命周期与三层检查、止损、验收强度、卡级门禁清单、信道、形态 A/B/C 与两级集成、L1-L3、三区、Owner 裁决规则、退回依据、里程碑收官与交付报告、工程规约 | 全员必读 |
| `architect.md` | 批量出卡(薄卡)、出卡自查、被唤起时的裁决与按需审核、退回定性、收官评估与归类、写交付报告 | Architect |
| `coordinator.md` | 派卡、卡级门禁与集成、跟踪分流、三本账、里程碑收口与报告汇编 | Coordinator;未部署时门禁归 Reviewer、其余归 Architect |
| `implementer.md` | 领卡、细化完成判据、三区内的实施纪律、三节交付报告、退回处理 | Implementer |
| `reviewer.md` | 里程碑验收、对抗档/取证档逐卡验收、台账与问题清单、合入主干、漏检回流 | Reviewer;未部署时由 Architect 执行 |
| `profiles/guarded.md` | 保守档附录:给较弱 Implementer 的收紧规则 | 用保守档时的 Architect / Implementer |
| `references/local-worktrees.md` | C 模式与 Multica:每轮起点、消息收发、确定 SHA 验收、串行集成、失败恢复、旧部署迁移 | C / 托管任务必读 |
| `scripts/worktree_guard.py` | Python 3 标准库工具:只读探测、一次性记录起点、交付前检查 | C / 托管任务开工与交付时 |
| `anti-patterns.md` | 反模式池(历史教训,持续追加) | 全员 |
| `templates/` | channel 骨架、任务卡、Owner 交付报告、三份启动提示词 | 部署与日常 |

## 新项目部署流程(Architect 侧执行)

关键认知:**其他 agent 读不到本 skill 目录**——它们只读项目仓库和自己的启动提示词。所以部署 = 把协作基础设施**实例化进项目仓库**;本 skill 是母本 + 部署器。

1. **定角色、模型来源与档位**:问 Owner 有几个 agent、**分别是什么模型**,按下表落位并记入信道存档(protocol §1.2、§1.3):

   | 角色 | 要什么样的模型 |
   | --- | --- |
   | Architect | 设计能力最强的那个。它的上下文最贵,所以不让它记账 |
   | Implementer | 执行细致、能独立读懂代码库 → 标准档;较弱或易偏离 → 保守档 |
   | Reviewer(可选) | 严谨、肯真跑;最好与 Implementer 异源。里程碑末才大量出场 |
   | Coordinator(可选) | 守流程、便宜即可,不要求设计能力;但要能可靠地跑命令、比对输出。agent 数不够时省掉它 |

2. **定配置**(按已授权上下文与项目实情):信道位置、分支来源、项目门禁命令表(protocol §8)、注释/文案语言、**两级集成人与里程碑集成分支命名**(protocol §4)、**记账位置**(backlog、挂账、门禁记录、待 Owner 裁决清单、交付报告目录);C 模式还需登记发送分支、主干更新入口;
3. **定工作区形态与管理者**:按 protocol §4 的只读拓扑探测区分 A(共享目录)、B(独立 clone)、C(本地并行 worktree),并记录 manual / multica。不能把「看不到未提交消息」直接判为 B。Reviewer 的独立 worktree 同样按 C 收发消息;
4. **实例化进仓库**:A/B 使用 `templates/channel.md`;C 使用 `templates/channel-worktrees.md` 建部署配置,消息使用 `templates/message.md`。拷贝 `protocol.md`、各已部署角色的手册、`anti-patterns.md`、`templates/task-card-*.md`(含细化文件模板)、`templates/owner-report.md` 进项目(如 `docs/collab/`),填掉项目配置;用保守档时加 `profiles/guarded.md`;推荐同时拷贝 `architect.md`。C / 托管部署还要拷贝 `references/local-worktrees.md`、`scripts/worktree_guard.py` 及其引用的两个模板,保持相对目录结构,并在项目配置明确实际脚本路径;
5. **给 Owner 出启动提示词**:按 `templates/implementer-bootstrap.md`(按部署再加 `coordinator-bootstrap.md`、`reviewer-bootstrap.md`)填空,交 Owner 配置给对应 agent——只指路径不复制内容;
6. **写部署宣告**,按已选通路送达并收显式确认,完成消息通路验证;
7. 设计文档与 ADR 定稿 → 批量出第一个里程碑的卡(`architect.md` §1)→ 交 Coordinator 派卡 → 协作开始。

**部署时要讲清楚的四件事**(不讲清楚必出事):

1. **卡面写什么、不写什么**:写目标、少量有区分力的完成判据、本卡特有约束、已知未知;不写实现步骤、运行信息和常驻规则。**放权靠的是红区清楚,不是卡面写满**(architect.md §1.2);
2. **提案不停工,但也不会自动生效**:黄区的事先做后裁,到交付还没答复的提案会让这张卡在合入前等 Architect(protocol §5);
3. **门禁只认清单,退回直达**:Coordinator 的门禁退回只引 protocol §2.3 清单与命令输出,直达 Implementer;有争议的才交 Architect。里程碑验收的问题清单一次给全交 Architect 归类,不直接发 Implementer(protocol §6.3);
4. **什么事才找 Owner**:protocol §6.2 的六类。其余问题在里程碑收官时自己迭代掉,Owner 拿到的是一份修完之后的交付报告(protocol §7)。

**代行要在断线之前定好**(protocol §1.1):agent 因限额或上下文耗尽而中断是常态。部署时就把代行者、代行期权力边界(**裁决算数;主干合入需要 Reviewer 的验收与 Architect 的归类两方都在,缺一方主干就等**)写进信道存档。卡都落在集成分支上,主干等待不阻塞开发。Coordinator 不代行裁决与验收。

**验收与收官自迭代都要设闸**(protocol §2.1、§2.2):一次给全、只退回有依据的、轮次封顶、三个越线信号;每张卡标验收强度,对抗档在出卡时点名。这些环节没有自然终点,不设闸各方都会不自觉地加码。

## 日常路由(已部署项目中)

- C / Multica / `local_directory worktree` 报错:先读 `references/local-worktrees.md`;每轮 `start`,交付前 `check`,失败保留现场。不能用新 `run_id` 掩盖原运行的起点丢失;
- 旧项目切换本地并行 worktree:按参考文档的「旧部署迁移」更新实例与启动提示词,不能只改母本;
- **旧项目迁移到本版流程**(Architect 逐卡审核 → 按需唤起 + 收官评估;Reviewer 逐卡验收 → 里程碑验收;新增 Coordinator 卡级门禁、里程碑集成分支、三区、Owner 交付报告):更新项目实例的 protocol / 各手册 / 卡片模板 / 启动提示词,登记各 Implementer 的档位、两级集成人与记账位置,在信道宣告生效点;在途卡按旧流程走完,新卡按新流程。**想保留旧流程的严格度,把 Implementer 登记为保守档即可**,不必停留在旧版本;
- 我是 Architect:出卡 → `architect.md` §1;被唤起 → §2 的表;L1 → §3;判据确认与按需审核 → §4;退回定性 → §5;里程碑收官与写报告 → §6。未部署 Coordinator 时派卡记账 → `coordinator.md` §1、§3–§5;未部署 Reviewer 时验收合入 → `reviewer.md` §1–§4;
- 我是 Coordinator:派卡 → `coordinator.md` §1;收到交付 → §2 门禁与集成;看到别的消息该不该动 → §3 的表;记账 → §4;里程碑收口与汇编 → §5;
- 我是 Implementer:领卡 → `implementer.md` §1;细化判据 → §2;实施 → §3;交付 → §4–§5;退回 → §6;
- 我是 Reviewer:里程碑的卡全部集成 → `reviewer.md` §1、§2.1;对抗档/取证档的卡过了门禁 → §2.2–§2.3;出结论 → §3;合入主干 → §4。未部署 Coordinator 时收到交付 → `coordinator.md` §2;
- **这件事该不该找 Owner** → `protocol.md` §6.2;**这件事在哪一区** → §6.1;
- **接手代行 / 交回**:→ `protocol.md` §1.1——代行者权力边界、主干何时要等、交接对账消息;**半途卡不换手**;
- 需要给其他 agent 指引时:指向**项目仓库内的实例文档**,不指向本 skill 路径(它们读不到)。**例外**:若其他 agent 自己也能加载本 skill(各自的 skills 目录里有同一份母本),则不必实例化协议文档,直接共享母本——单一事实源、无实例漂移;代价是母本里的【坑位】没有落点,门禁命令表、路径、形态与档位必须改由信道存档或项目内的指引文档承载,部署时要点名放在哪;
- 拿不准某规则 → `protocol.md`;疑似踩坑 → `anti-patterns.md` 先查有没有前车之鉴。

## 经验回流

新项目跑出的新教训(出卡自查新增项、反模式、裁决先例、Owner 裁决规则的边界案例)先落项目实例文档,由 Owner 触发回流本母本——母本是跨项目资产,实例是项目现场。两处都改时先实例后母本,防漂移。
