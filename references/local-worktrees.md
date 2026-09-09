# 本地 worktree 与 Multica 工作流

适用于 protocol §4 的形态 C,以及 Multica 分配目录/分支的托管运行。先识别实际拓扑,再叠加宿主约束;不要仅凭路径中出现 `multica` 或旧文档中的 A/B 标签判断。

## 部署与每轮开工

项目部署配置由 Architect 维护,默认 `docs/collab/workspace.md`,使用 [部署模板](../templates/channel-worktrees.md)。记录各参与者的机器、实际工作区、发送分支、消息命名空间、管理者、唯一集成人与主干更新入口。角色来自本次任务指派,目录和分支来自本次实际运行。

只读探测(Python 3 标准库,Git 支持 `--path-format=absolute`):

```sh
python3 scripts/worktree_guard.py inspect
git worktree list --porcelain
```

同机不同 `worktree` / `git_dir`、相同 `git_common_dir` 是 C。index 和 HEAD 各自独立,普通分支 refs 与提交对象共享。对方分支的新提交已经能用 `git show` 读,本方工作文件不会自动更新。源目录本身也是一个工作区,不能把它当共享写入出口。

**每轮在任何 Git 写操作前**,包括整理历史、切分支和依赖同步,记录起点:

```sh
collab_run_id='swo-152-architect-r1'
python3 scripts/worktree_guard.py start --run-id "$collab_run_id" --task-base <task-base-sha>
```

- 示例运行 ID 必须替换为本次执行的唯一 ID,优先使用宿主提供的执行 ID;没有时为本轮生成一次 UUID 并保留。ID 用 ASCII 字母、数字、点、下划线、连字符,不超过 128 字符。上下文恢复、重复检查沿用同一 ID;真正的新一轮才换 ID。
- `task_base` 是卡面要求的确定基线,跨轮保持卡面定义;`run_start` 是这轮第一条 Git 写操作前的实际 HEAD,每轮重新捕获。尚无任务卡时可省略 `--task-base`,但交付仍须核对后续卡面基线;不能重写记录来补字段。
- 脚本记录到本 worktree 的 `git_dir/cooperation-skill/runs/<run-id>.json`,不进入工作树;按各自 git-dir 定位,不能统一用 common-dir 构造状态路径。同一运行的 `start` 不覆盖已存在记录,重复运行会校验原记录。
- `start` 先固定起点,允许卡面基线尚未合入;交付 `check` 同时要求起点和已记录的 `task_base` 都可达。对象不存在时先通过只读 Git 查询/已授权 fetch 取得对象,不要移动 HEAD。
- 已做过 Git 写操作才发现忘了记录时,不能把当前 HEAD 当成本轮起点。先从宿主本轮上下文和 reflog 取证,报告缺失的开工检查;本脚本不支持事后指定或覆盖 `run_start`。

部署到项目时,把上述脚本路径替换成配置中的实际路径(例如 `docs/collab/scripts/worktree_guard.py`)。用 `--repo <任务工作区>` 可从别处检查原运行,该全局参数放在子命令之前。

## 任务与历史边界

| 场景 | 执行方式 |
| --- | --- |
| 手工创建 C 工作区 | 在运行开始前按卡面基线创建独立 worktree/分支;同一分支不供多个运行并发写 |
| Multica 已分配工作区 | 沿用实际目录、分支或 detached HEAD 状态,不另建任务分支或切 main |
| 本方实现、文档、署名 | 追加新提交;宿主生成的 baseline/checkpoint 和起点提交保留原样 |
| 卡面基线不在当前历史中 | 确认卡面明确授权该依赖后,`git merge --no-ff <确定 SHA>` 同步进本方分支;冲突按契约处理,方向不清则 L1 |
| 需要不同基线才能开始 | 让宿主在下一运行开始前分配正确基线;当前运行不能 reset/rebase 掉起点 |
| 取消本方文件暂存 | `git restore --staged <路径>` 不移动 HEAD,不属于历史改写 |

**托管运行默认只追加。** 不为美化 message/尾注 amend checkpoint;不对包含起点的区间做 rebase/squash;不把分支 reset 到起点之外。也不能通过 `branch -f`、`update-ref`、另一个工作区或强制 checkout 绕过这些约束。检查证明的是提交可达性,不替代实现范围、文件内容与测试验收。

卡片可指定业务基线与依赖 SHA,不能用预设分支名覆盖宿主已经分配的分支。多个 Architect 并行时,每张卡声明唯一集成人;“都有 Architect 角色”不代表可同时改主干。

## 消息收发

使用 [独立消息模板](../templates/message.md)。每个发送者只在自己的命名空间新增消息:

```text
docs/collab/messages/<task>/<run-id>/001.md
docs/collab/messages/<task>/<run-id>/002.md
```

消息 ID 为 `<task>/<run-id>/<seq>`,每轮的 ID 全局唯一,序号只在本轮递增。更正发布新文件并引用原 ID,已发布消息不改不删。`to` 唯一,`cc` 可多方;`in_reply_to` 指向回复对象,`ack` 列出实际读过的消息,不能用“最大编号”推断其它并行消息已读。

1. **发送**:保存本方工作为提交 `D`;交付消息填写 `delivery_sha: D` 和 `task_base`,验证证据也绑定 D。提交新增消息文件得到载体提交 `M`。不能在消息里填写它自身尚未产生的提交 SHA。
2. **发现**:收件人从部署配置/已到达的派卡消息获取发送分支,用 `git rev-parse <发送分支>^{commit}` 固定载体 SHA;新参与者必须先由 Architect 登记其分支,不能靠扫描所有 `agent/*` 猜哪些任务相关。
3. **读取**:用下面的只读命令列出并读取该载体的消息,无需 checkout、merge 或 push。本方以消息 ID 去重,显式确认。通知中若给了 SHA,优先读该 SHA。

   ```sh
   git ls-tree -r --name-only <载体SHA> -- docs/collab/messages/
   git show <载体SHA>:docs/collab/messages/<task>/<run-id>/001.md
   git show <卡面SHA>:<卡面路径>
   ```

4. **检查并交付**:消息提交后对最终 HEAD 执行 guard `check`,最终回复给出消息 ID、载体 SHA 和检查结果。代码 D 与载体 M 要分别记录;只新增通信文件的 M 不改变绑定 D 的代码验收。载体必须包含 D,可用 `git merge-base --is-ancestor <D> <M>` 验证。

可用 Multica 已配置的任务评论/消息通知这些指针,以实际可用工具为准,不假设存在某个 CLI/API。通知必须沿用用户已有授权。没有通知工具时,按协议由触发方读取登记分支即可,不要求 Owner 搬运消息正文。旧 `channel.md` 是历史归档,C 的新消息不再并行追加该文件。

## 交付与固定 SHA 评审

交付消息至少给出:任务/运行 ID、实际分支、`task_base`、`run_start`、`delivery_sha`、验证命令及结果、实施发现。引用任务卡时还给卡面 SHA,避免本方旧工作文件掩盖最新契约。

```sh
python3 scripts/worktree_guard.py check --run-id "$collab_run_id"
```

返回 `0` 表示检查通过,`1` 表示身份/祖先关系不符,`2` 表示记录缺失、Git 或输入错误。`check` 不写文件、不移动分支、不修复历史;在最终消息提交之后再执行。它检查当前 Git 状态,不证明宿主稍后记录成功,也不是拦截所有 Git 命令的 hook。

Reviewer/Architect 的代码范围是卡面确定的 `task_base..delivery_sha`,不能用空的工作区 diff 或移动中的分支 HEAD 替代。基线中继承的改动与本卡增量分别披露。

只读检查用 `git show` / `git diff`;需要运行门禁时,可创建**自己拥有的临时 detached review worktree**并固定到 `delivery_sha`,验证后清理该临时目录。它不是替换宿主工作区;不进入 Implementer 的现场操作,不改变 Reviewer 托管运行的分支/起点。无工作区创建权限时用项目已配置的评审执行环境。报告记录实际验证的 SHA,更新交付后只对新的变化与受影响门禁复验。

## 串行集成与宿主收口

1. 指定 Architect 收到并固定消息载体 M 与代码 D,核对祖先关系、范围、依赖和绑定 D 的验证证据。代码、已发布消息与任务文档都须有归档去向。
2. 在**配置中指定且自己拥有的集成工作区/分支**串行合并确定 SHA。可以合并 M,但必须先核实 `D..M` 只含已经审查的通信/文档变化,不能把未审代码顺带合入。托管运行的集成工作区仍是宿主分配的那一份。
3. 保留集成人自己的 `run_start`,在合并态跑必要门禁,追加 backlog/验收记录,然后执行最终 guard 检查。集成不能移动仍在执行的其它任务分支。
4. 把结果交给宿主正常记录。**不假定 Multica 会自动把记录的任务分支合入 main。** 只有配置中的主干入口实际完成更新并核实目标 SHA 后,才报告主干已合入;缺少入口时明确列为“已验收,待主干集成”,不切源目录绕过宿主。
5. 本地提交完成、宿主记录成功、主干集成、远端发布分别报告。push 沿用已有授权,本地可见不依赖 push。已被 worktree 占用或宿主仍管理的分支不删除;托管 worktree 由平台回收。自己创建的 review worktree 可自行清理。

## 失败恢复

出现 `local_directory worktree: refusing to record branch` 时,保留原目录和运行记录,先做只读核查:

```sh
git worktree list --porcelain
git reflog -n 20 --date=iso
git show -s --format='%H %P %T %s' <run_start> <delivered>
git merge-base --is-ancestor <run_start> <delivered>
git diff --stat <run_start> <delivered>
```

对照本轮起点与 reflog 区分 amend、reset、rebase 或交付了错误分支。即使两个 tree 相同,起点不是祖先仍属失败。不要删除保留目录、强推分支、换运行 ID 或覆盖起点让检查变绿。

运行已失败并结束后,由指定恢复者按照宿主实际重试约定保留原两端,在新的恢复分支上基于正确起点重建经过核对的增量;新运行按其真实启动点另行捕获。恢复脚本不会替宿主补写旧运行的成功状态。本 skill 不自动执行恢复或修改宿主内部元数据。

## 旧部署迁移

1. 检查项目实例和启动提示词,保留项目门禁、角色契约和历史消息;只替换工作区、分支、已读和收口相关操作。历史消息里的 A 配置保留为当时记录,当前配置明确指向 `workspace.md`。
2. 将参考文档、guard、部署与消息模板随实例复制,保留相对链接可达,登记实际脚本路径。实例若已经是定制旧版,可在入口明确引用本参考覆盖旧 Git 操作,不要整份覆盖项目规则。
3. 完成拓扑探测,登记当前参与者、发送分支和唯一集成人。启动提示词不能再硬编码源目录,也不能把当前 worktree 的可见性解释为共享目录。
4. 将迁移文件纳入正常交付,让所有活跃运行明确读到同一部署版本。更新母本或源目录的未提交文件不会自动更新其它 worktree;已有运行不能用迁移当作重新捕获起点的理由。

## 验证范围

母本回归命令:`python3 -B -m unittest discover -s tests -v`。临时仓库覆盖追加提交、改说明的 amend、越界 reset/rebase、分支切换、每轮与每 worktree 记录隔离、依赖合并、独立消息读取与串行集成;测试自行清理临时仓库。完成这些只证明本地 Git 工作流,实际 Multica 的记录与回收还须通过一次真实运行验证。
