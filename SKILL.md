---
name: cooperation-skill
description: 双 agent 协作框架(Architect 出卡/裁决/验收/收口 + Implementer 按卡实现)。用于:在新项目部署双 agent 协作基础设施;日常出任务卡、派卡、处理信道消息、L1/L2/L3 分级裁决、验收交付、收口合入。源自项目 A 的协作规范 v1.5 及实战演化。
---

# 双 agent 协作框架

一句话:**Architect(出卡/定契约/裁决/验收/merge)+ Implementer(按卡实现/自检/上报发现)+ Owner(人类,决策/验收/触发)**,通过仓库内只追加信道异步协作;任务卡自包含 + 硬边界 + 机器可验收;实施发现分级反馈,裁决前一律按契约。

## 文件地图

| 文件 | 内容 | 谁读 |
| --- | --- | --- |
| `protocol.md` | 共同协议:角色三角、生命周期、**双 Architect 交叉 review(一轮止损)**、**验收强度分档**、信道规则、工作区形态 A/B 与握手探测、L1/L2/L3 分级、绿区/红区、体量披露制、工程规约 | 双方必读 |
| `architect.md` | 第一部分:出卡门禁、派卡、信道处理、裁决流程、验收五步、收口序列 | Architect |
| `implementer.md` | 第二部分:领卡、实施纪律、自检清单、交付报告、打回处理 | Implementer |
| `anti-patterns.md` | 反模式池(历史教训,持续追加) | 双方 |
| `templates/` | channel 骨架、开发/内容任务卡模板、Implementer 启动提示词模板 | 部署时用 |

## 新项目部署流程(Architect 侧执行)

关键认知:**Implementer agent 读不到本 skill 目录**——它只读项目仓库和自己的启动提示词。所以部署 = 把协作基础设施**实例化进项目仓库**;本 skill 是母本 + 部署器。

1. **定配置**(问 Owner 或按项目实情):信道文件路径(默认 `docs/collab/channel.md`)、分支命名约定、项目门禁命令表(protocol §8 坑位)、体量预算基线、注释/文案语言;
2. **定工作区形态**:Owner 指定 A(共享本地工作区)或 B(分离工作区);Owner 未指定则部署后用**握手探测**(protocol §4:信道写入含随机标记的消息不 commit,对方读得到 → A,读不到 → 补 commit+push 走通 → B),结论记入信道存档;
3. **实例化进仓库**:按 `templates/channel.md` 建信道文件;拷贝 `protocol.md`、`implementer.md`、`anti-patterns.md` 进项目(如 `docs/collab/`),**填掉全部【坑位】**(门禁命令表、路径、形态);`architect.md` 可拷可不拷(Architect 直接用 skill 母本,拷入则对 Implementer 透明,推荐拷);
4. **给 Owner 出启动提示词**:按 `templates/implementer-bootstrap.md` 填空,交 Owner 配置给 Implementer agent——只指路径不复制内容;
5. **写信道 #1 部署宣告**(模板内含示例),等 Implementer 回 #2 确认已读(顺带完成形态握手);
6. 建 backlog(若无)→ 出第一张卡(`architect.md` §1)→ 协作开始。

**若项目有两个 agent 都能当 Architect**:可在派出第一张实现卡之前插入一次交叉 review(protocol §2.1)。这个环节收益集中在前几轮、之后急剧转负,**部署时就要把"一轮止损 + 必审四类 + 四个越线信号"讲清楚**,不要等跑起来再收口——它没有自然终点,双方都会不自觉地加码。同时按 protocol §2.2 给 backlog 每张卡标验收强度,对抗档在出卡时点名,不留给验收时临场判断。

## 日常路由(已部署项目中)

- 我是 Architect:出卡/派卡 → `architect.md` §1;收到信道消息 → §2 分流(L1 → §3 裁决;交付 → §4 验收五步);合入 → §5 收口序列。
- 需要给 Implementer 指引时:指向**项目仓库内的实例文档**,不指向本 skill 路径(它读不到)。
- 拿不准某规则 → `protocol.md`;疑似踩坑 → `anti-patterns.md` 先查有没有前车之鉴。

## 经验回流

新项目跑出的新教训(出卡门禁新增项、反模式、裁决先例)先落项目实例文档,由 Owner 触发回流本母本——母本是跨项目资产,实例是项目现场。两处都改时先实例后母本,防漂移。
