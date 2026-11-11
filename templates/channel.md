# 协作信道(channel)

> 本模板用于 A/B 的串行单文件信道。C 使用 `channel-worktrees.md` 部署配置与 `message.md` 独立消息模板;旧信道保留历史。

> 本文件是各 agent 角色之间的异步通信信道。规则全文见协作协议(protocol)§3;此处只记最低限度纪律:
>
> - **只追加**,消息永不修改/删除;编号 `#N` 严格递增;
> - 写自己的消息用**仅追加写入**(如 `cat >> 本文件 <<'EOF' ... EOF`),不用整篇重写/模糊匹配的方式动这份文件;
> - 消息格式(元信息行必填):
>   ```
>   ## #N ｜ <发件人> → <收件人> ｜ <日期> ｜ <主题>
>   > 抄送:<角色/无> ｜ 已读至:#M ｜ 下一步:@<角色>
>   ```
>   收件人**唯一**,是这条消息要求动作的一方;需要知情但不需要动作的写进抄送。
> - A 中 `git add` 本文件 = 主收件人的已读回执,自己的消息不 add;抄送用 `git diff HEAD -- 本文件` 读。B 提交本方消息并显式写已读水位,不通过 staging 通知另一个 clone;
> - 本文件永久豁免一切任务卡"涉及范围"限制;
> - 需要 Owner 决策的事项不走信道。
>
> 角色部署与模型来源:【Architect =? ｜ Implementer =?(档位:标准/保守)｜ Coordinator = ?/未部署 ｜ Reviewer = ?/未部署】——未部署的角色由 Architect 兼
> 集成人:卡级【Coordinator;未部署为 Reviewer】｜ 主干【Reviewer;未部署为 Architect】｜ 里程碑集成分支命名【milestone/<里程碑>】
> 记账位置:backlog【路径】｜ 挂账【路径】｜ 待 Owner 裁决清单【路径】｜ 交付报告【docs/collab/reports/】
> 工作区形态:【A 共享本地工作区 / B 独立 clone——按 protocol §4 拓扑探测后填写;若为 C 改用对应模板】;管理者:【manual / multica】
> 【形态 A 时补填】集成与验收用的工作区:Coordinator【A-共享 / A-独立】｜ Reviewer【A-共享 / A-独立】(protocol §4,推荐 A-独立)

---

## #1 ｜ Architect → Implementer ｜ 【日期】 ｜ 部署宣告(示例,替换后使用)

> 抄送:Reviewer ｜ 已读至:#0 ｜ 下一步:@Implementer

协作基础设施已就位:

- 共同协议:【路径,如 docs/collab/protocol.md】
- 你的手册:【路径,如 docs/collab/implementer.md】;你的档位:【标准 / 保守】
- 反模式池:【路径】
- 任务池 backlog:【路径】
- 工作区形态:【A / B / 待只读拓扑探测;确认 C 时切换模板】

请用下一个可用编号确认已读,并给出 protocol §4 的只读拓扑探测结果;不能仅凭读不到未提交消息判为 B。

## #2 ｜ Architect → Reviewer ｜ 【日期】 ｜ 部署宣告(部署 Reviewer 时使用,否则删除;Coordinator 同理另发一条,指向 coordinator.md)

> 抄送:Implementer ｜ 已读至:#0 ｜ 下一步:@Reviewer

- 共同协议:【路径】,重点 §2 生命周期、§2.1 审核与验收的止损、§2.2 验收强度分档、§6.1 三区、§6.3 退回与打回的依据
- 你的手册:【路径,如 docs/collab/reviewer.md】
- 反模式池:【路径】

请回复确认已读,并说明你的工作区安排(A-共享 / A-独立 / 形态 B)。提醒:实现期你不介入;里程碑的卡全部集成后由你把整体跑起来验收,台账与问题清单一次给全交我归类;对抗档与取证档的卡在集成前由你逐卡验收;验收过的集成分支由你合入主干。你**无契约修改权**——问题须有依据与复现,卡面本身的问题标明后交我。
