---
id: "<task>/<run-id>/<seq>"
from: "<role-and-agent>"
to: "<one-recipient>"
cc: []
in_reply_to: []
ack: []
kind: "<dispatch|question|refinement|proposal|blocked|decision|delivery|gate|review|acceptance|return|milestone-acceptance|milestone-review|closeout>"
task: "<task-id>"
run_id: "<current-run-id>"
branch: "<actual-branch-or-detached>"
task_base: "<full-commit-sha>"
run_start: "<full-commit-sha>"
delivery_sha: "<already-created-code-or-document-commit-sha>"
---

# <主题>

<结论、需要收件人执行的动作、卡面路径与其确定 SHA。只填实际已知字段,非交付类消息可以省略 task_base/delivery_sha;不猜测哈希。派卡消息在此写明执行者档位、授权同步的依赖 SHA、集成分支、是否需要先确认完成判据——这些运行信息不在卡面里。>

<交付类消息按 implementer.md §5 的三节给出:做了什么与怎么做的、验证证据(绑定 delivery_sha)、需要知道的事(需 Architect 过目的条目标出)。ack 仅列实际读过的消息 ID。>

<本地提交、宿主记录、主干集成、远端发布的实际状态;尚未发生的不写完成。载体提交在提交本消息之后获得,在最终回复/通知中给出,不写回本文件。>
