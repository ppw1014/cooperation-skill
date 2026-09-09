---
id: "<task>/<run-id>/<seq>"
from: "<role-and-agent>"
to: "<one-recipient>"
cc: []
in_reply_to: []
ack: []
kind: "<dispatch|question|decision|delivery|review|closeout>"
task: "<task-id>"
run_id: "<current-run-id>"
branch: "<actual-branch-or-detached>"
task_base: "<full-commit-sha>"
run_start: "<full-commit-sha>"
delivery_sha: "<already-created-code-or-document-commit-sha>"
---

# <主题>

<结论、需要收件人执行的动作、卡面路径与其确定 SHA。只填实际已知字段,非交付类消息可以省略 task_base/delivery_sha;不猜测哈希。>

<交付类消息按 implementer.md 给出验证、实施发现和存疑点,验证绑定 delivery_sha。ack 仅列实际读过的消息 ID。>

<本地提交、宿主记录、主干集成、远端发布的实际状态;尚未发生的不写完成。载体提交在提交本消息之后获得,在最终回复/通知中给出,不写回本文件。>
