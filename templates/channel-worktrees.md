# 本地 worktree 协作部署配置

> 当前配置由指定 Architect 维护。消息另存于 `messages/`,不在本文件并行追加。已部署项目中的 `channel.md` 保留历史,不作为 C 模式的新消息入口。

- 工作区形态:C(同机不同工作目录、相同 Git common-dir)
- 管理者:【manual / multica,以实际任务上下文为准】
- 协议:【protocol.md】;C 操作:【references/local-worktrees.md】
- guard 路径:【项目内实际路径,如 docs/collab/scripts/worktree_guard.py】
- 消息目录:【docs/collab/messages】;消息模板:【templates/message.md】
- 历史信道:【docs/collab/channel.md / 无】
- 唯一集成人:【角色 + 当前任务身份】
- 集成工作区/分支:【manual 时指定;multica 时使用集成人本轮实际分配】
- 主干目标与更新入口:【目标分支 + 实际由谁/通过何入口更新,不得假定平台自动合入 main】
- 宿主记录结果来源:【平台任务结果/实际可用查询入口】
- 远端发布:【沿用项目已有授权规则】

## 参与者与消息发现

| 任务/角色身份 | 机器 | 实际 worktree / git-dir / common-dir | 发送分支 | 消息 task/run-id |
| --- | --- | --- | --- | --- |
| 【身份】 | 【机器标识】 | 【inspect 结果】 | 【实际 refs/heads/...】 | 【唯一命名空间】 |

新参与者的分支先由 Architect 登记,或在已送达的派卡消息中明确指定;运行 ID 每轮唯一,恢复上下文沿用。固定发送分支的载体 SHA 再读取,不能把本方消息目录没有新文件当作无人发言。登记信息须通过已建立通路交给参与者。

## 部署确认

- 配置版本:【承载此配置的已提交 SHA,可由后续部署消息引用,不自填本次提交 SHA】
- 拓扑证据:【各方 inspect 的路径关系与机器标识】
- 通路证据:【另一 worktree 已读到的消息 ID 与载体 SHA】
- 生效对象:【确认加载该配置的运行;未确认者保持待迁移】
