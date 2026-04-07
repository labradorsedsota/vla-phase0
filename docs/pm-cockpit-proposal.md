# pm-cockpit 详细方案（v3）

## 一、整体架构

```
GitHub Projects（数据层 + 展示层）
├── 每个项目 = 一个 GitHub Project
├── 每个任务 = 一个 Issue（带自定义字段）
├── 所有人通过 Web UI 查看/操作
└── Bot 通过 gh CLI 读写

pm-cockpit Skill（规范层 + 巡检层）
├── 统一 ID 体系
├── 项目启动规范
├── 任务指派规范 ← 解决短板2
├── 环节流转规范 ← 解决短板3
├── 风险管理规范 ← 解决短板4
├── 自动巡检规则 ← 解决短板1、5
└── 持续改进机制 ← 解决短板5
```

**解决的五个短板：**

1. 追踪是记录不是监控 → 时间感知的状态追踪 + 自动巡检预警
2. 协调是传话不是确保发生 → 任务指派六要素 + ACK 机制
3. 跨群依赖管理 → 全局视图 + 结构化流转交接包
4. 风险应对 → 能识别的提前识别，遇到时及时解决
5. 排期与进度预警 → 经验库积累 + 滞后自动预警

---

## 二、统一 ID 体系

### 2.1 实体层级

```
项目 (Project)
├── 应用 (App)
│   ├── 版本 (Version)
│   ├── 测试点 (Testpoint)

│   └── 轨迹 (Trace)
├── 任务 (Task)
├── 决策 (Decision)
└── 会议 (Meeting)
```

### 2.2 ID 格式总表

| 实体 | 格式 | 示例 | 说明 |
|------|------|------|------|
| 项目 | `{代号}` | `VLA` | 2-5 个大写字母，全局唯一 |
| 应用 | `{项目}-{应用缩写}` | `VLA-M2W`、`VLA-TS` | 缩写 2-4 个大写字母，项目内唯一 |
| 应用版本 | `{应用缩写}-{版本号}` | `M2W-v1`、`M2W-v2`、`TS-v3` | 版本号递增，应用内唯一 |
| 测试点 | `{应用缩写}.{层级}.{序号}` | `M2W.L1.1`、`M2W.L2.4` | 应用缩写 + L 编号 |
| 轨迹 | `{项目小写}-{应用小写}-{版本}-{测试点}-{序号}` | `vla-m2w-v1-L2.4-01` | 嵌入 mano-cua task 水印 |
| 任务 | `{项目}-T{序号}` | `VLA-T001` | 项目内递增 |
| 决策 | `{项目}-D{序号}` | `VLA-D001` | 项目内递增 |
| 会议 | `{项目}-MTG-{日期}` | `VLA-MTG-0330` | 同天多次加后缀 a/b |

### 2.3 上下文简写规则

| 场景 | 写法 | 原因 |
|------|------|------|
| 跨项目引用 | `VLA-M2W.L2.4` | 完整定位 |
| 项目内跨应用引用 | `M2W.L2.4` | 项目上下文已知 |
| 单应用文档内（如 PRD） | `L2.4` | 应用上下文明确 |
| 群聊 / 跨群 / 巡检预警 | `VLA-T003` / `M2W.L2.4` | 至少带应用或项目前缀 |
| 轨迹水印 | `vla-m2w-v1-L2.4-01` | 完整定位，支持跨项目检索 |

**原则：能从上下文推断的部分可以省略，但在任何可能产生歧义的场景中必须用全称。**

### 2.4 轨迹 ID 详细设计

**格式：** `{项目小写}-{应用小写}-{版本}-{测试点}-{采集序号}`

| 字段 | 含义 | 检索价值 |
|------|------|---------|
| `vla` | 项目代号（小写） | "拉这个项目的全部轨迹" |
| `m2w` | 应用缩写（小写） | "拉这个应用的全部轨迹" |
| `v1` | 应用版本 | "只看 v1 版本" / "对比 v1 和 v2" |
| `L2.4` | 测试点编号 | "这个测试点的历次表现" |
| `01` | 同版本同测试点的采集序号 | 区分重跑 |

**嵌入方式：** task 末尾加分隔线 + 水印标记

```
（正常任务描述）

---mano inner test---
[mosstid: vla-m2w-v1-L2.4-01]
```

**检索示例：**
- `vla-` → VLA 项目全部轨迹
- `vla-m2w-` → md2wechat 应用全部轨迹
- `vla-m2w-v1-` → md2wechat v1 版本全部轨迹
- `vla-m2w-v2-L2.4` → md2wechat v2 版本 L2.4 测试点
- `L2.4` → 跨版本该测试点全部轨迹

**版本迭代典型场景：**

```
v1（初版）：     vla-m2w-v1-L1.1-01, vla-m2w-v1-L2.4-01, ...
v2（修复后）：   vla-m2w-v2-L1.1-01, vla-m2w-v2-L2.4-01, ...
v3（大改版）：   vla-m2w-v3-L1.1-01, ...
```

### 2.5 应用注册表

每个项目维护一份应用注册表，作为 ID 映射的权威来源：

```yaml
# config/apps.yaml
project: VLA

apps:
  - id: VLA-M2W
    abbr: m2w
    name: "md2wechat"
    name_cn: "Markdown转微信格式"
    type: web
    testpoints: 19
    versions:
      - tag: v1
        desc: "初版"
      - tag: v2
        desc: "修复 v1 问题后版本"

  - id: VLA-TS
    abbr: ts
    name: "tripsplit"
    name_cn: "旅行分账"
    type: web
    testpoints: 15
    versions:
      - tag: v1
        desc: "初版"

counters:
  task: 8        # 下一个: VLA-T009
  decision: 13   # 下一个: VLA-D014
  meeting: 2     # 下一个: VLA-MTG-0401
```

### 2.6 ID 在各类文档中的应用

**PRD 文档：**

```markdown
# VLA-M2W PRD — Markdown 转微信公众号格式

文档编号：VLA-M2W-PRD
关联任务：VLA-T001

## L1 — 基础功能
- L1.1 文件上传：点击上传 → 选 .md → 左原文右预览
...

```

**决策记录：**

```markdown
# VLA 决策记录

## VLA-D001 ✅ L1.3 拆分为 3a/3b/3c
- 日期：2026-03-30
- 决策者：Jo
- 影响：测试点从 17 条增至 19 条
```

**会议纪要：**

```markdown
# VLA-MTG-0330 — Phase 0 启动会

## 议题
1. 文档管理方案 → VLA-D003 - VLA-D012
2. 应用 VLA-M2W 的 PRD 评审

## 待办
- VLA-T001 Pichai 完成 PRD（已完成）
- VLA-T002 Moss 生成测试用例（进行中）
```

**Git commit：**

```
[VLA-T003] feat: implement md2wechat v1
[VLA-T004] fix: 修复脚注编号问题 → md2wechat v2
```

**任务指派消息：**

```
📌 任务指派 VLA-T002

做什么：基于 VLA-M2W PRD 生成测试用例
输入物：prds/VLA-M2W.md
产出标准：覆盖 M2W.L1.1 - M2W.L3.5 全部 19 个测试点
时间预期：3 小时
Issue：github.com/.../issues/2
请确认收到并告知是否可以开始
```

**环节流转交接包：**

```
## 🔄 流转：VLA 需求定义 → 研发实现

交付物：VLA-M2W PRD（prds/VLA-M2W.md）
关联任务：VLA-T003（M2W v1 开发）
验收标准：M2W.L1.1 - M2W.L3.5 全部 PASS
```

**巡检预警：**

```
🚨 项目巡检 | 2026-04-02 15:00

[VLA]
🔴 VLA-T002 "生成测试用例" (Moss) — 超时 27h
   阻塞链：VLA-T005, VLA-T006 等待中
   关联应用：VLA-M2W, VLA-TS
```

**测试报告：**

```markdown
# VLA-M2W 测试报告 — v1

| 测试点 | 轨迹 ID | 结果 | 备注 |
|--------|---------|------|------|
| M2W.L1.1 | vla-m2w-v1-L1.1-01 | PASS | — |
| M2W.L2.4 | vla-m2w-v1-L2.4-01 | FAIL | 脚注编号不递增 |
```

**文件/目录命名：**

```
vla-phase0/
├── config/apps.yaml
├── prds/
│   ├── VLA-M2W.md
│   └── VLA-TS.md
├── apps/
│   ├── m2w/
│   │   ├── v1/
│   │   └── v2/
│   └── ts/
│       └── v1/
├── test/
│   ├── fixtures/m2w/
│   └── reports/VLA-M2W-v1-report.md
├── meetings/
│   └── VLA-MTG-0330.md
└── DECISIONS.md
```

---

## 三、GitHub Projects 数据结构

### 3.1 Project 创建规范

每个项目对应一个 GitHub Project：

```bash
gh project create --owner labradorsedsota --title "[P1] VLA - 测试数据采集"
```

命名规范：`[优先级] {项目代号} - 一句话描述`

### 3.2 自定义字段

| 字段名 | 类型 | 选项 / 说明 |
|--------|------|-------------|
| Status | SINGLE_SELECT | `Todo`, `Assigned`, `In Progress`, `Blocked`, `Done`, `On Hold` |
| Priority | SINGLE_SELECT | `P0-紧急`, `P1-重要`, `P2-常规`, `P3-低优` |
| Owner | TEXT | 负责人 ID |
| Stage | SINGLE_SELECT | 按项目定义，如 `需求`, `研发`, `测试`, `验收` |
| App | TEXT | 关联的应用 ID，如 `VLA-M2W` |
| Estimated Hours | NUMBER | 预估工时（小时） |
| Actual Hours | NUMBER | 实际工时（完成时填写） |
| Status Since | DATE | 进入当前状态的日期 |
| Due Date | DATE | 截止日期 |
| Depends On | TEXT | 前置依赖 Issue 编号，如 `#1, #3` |
| Blocks | TEXT | 完成后解锁的 Issue 编号 |

**关键约束：每次修改 Status 时，必须同步更新 Status Since。**

### 3.3 Issue 使用规范

Issue title 带任务 ID 前缀：`[VLA-T001] 撰写 PRD + L1/L2/L3 验收描述`

Issue body：

```markdown
## 任务描述
[具体做什么]

## 输入物
- [链接/位置/说明]

## 产出标准
- [完成标准]

## 备注
- [已知风险、约束]
```

Labels：
- `app:VLA-M2W` — 关联应用
- `stage:需求` / `stage:研发` / `stage:测试` — 所属环节
- `blocked` — 被阻塞
- `critical-path` — 关键路径任务

### 3.4 视图配置

| 视图名 | 类型 | 用途 |
|--------|------|------|
| 看板 | Board（按 Status 分列） | 全局状态概览 |
| 按负责人 | Table（按 Owner 分组） | 每个人看自己的任务 |
| 按环节 | Table（按 Stage 分组） | 各环节进展 |
| 按应用 | Table（按 App 分组） | 各应用相关任务 |
| 阻塞项 | Table（过滤 Status=Blocked） | 快速定位阻塞 |
| 时间线 | Table（按 Due Date 排序） | 截止日期概览 |

---

## 四、Skill 核心规范

### 4.1 项目启动流程

**触发：** 确认要做新项目时。

**步骤：**

1. **分配项目代号**（2-5 个大写字母，全局唯一）
2. **创建 GitHub Project**（命名：`[Px] {代号} - 描述`）
3. **创建自定义字段和视图**（按 3.2、3.4）
4. **定义项目元信息**（写在 Project Description）
   ```
   项目代号：VLA
   目标：[一句话，可验证]
   环节流：需求 → 研发 → 测试 → 验收
   团队：Pichai(PM), Fabrice(研发), Moss(测试)
   目标日期：YYYY-MM-DD
   ```
5. **创建应用注册表**（`config/apps.yaml`）
6. **拆解任务并创建 Issues**
   - 按环节拆解，每个 Issue 带任务 ID
   - 设置依赖关系、预估工时
   - 识别关键路径
7. **识别可预见的风险**
   - 在 Project 中创建 `风险登记` Issue
8. **通知团队**，附 Project 链接

### 4.2 任务指派规范（解决短板 2）

**触发：** 将任务分配给某人/bot 时。

**指派消息六要素：**

```
📌 任务指派 {任务ID}

1. 做什么：[具体任务描述]
2. 输入物：[链接/位置，注意事项]
3. 产出标准：[做到什么程度算完成]
4. 时间预期：[预计 X 小时，截止时间]
5. Issue 链接：[URL]
6. 请确认收到并告知是否可以开始
```

**指派后动作：**
- Issue Status → `Assigned`，更新 Status Since
- 等 ACK → ACK 后 Status → `In Progress`，再次更新 Status Since
- 记录跟进时间点

**30 分钟未收到 ACK → 主动询问一次；仍无回应 → 预警。**

### 4.3 环节流转规范（解决短板 3）

**触发：** 项目从一个环节进入下一个环节时。

**交接包模板：**

```
## 🔄 流转：{项目代号} {当前环节} → {下一环节}

**结论：**（确认的结论，不是讨论过程）
- 确认范围：
- 明确排除：

**交付物：**
- [链接]

**验收标准：**
- [下一环节拿什么标准判断上一环节产出合格]

**已知风险/约束：**
- [上一环节发现的可能影响下一环节的问题]

**优先级：** Px
**期望完成时间：** YYYY-MM-DD

**反向触发条件：**
如遇 [xxx 情况]，@Pichai 回 [上一环节群] 讨论。
```

**流转后动作：**
- 更新 Issues 的 Stage 字段
- 确认下一环节负责人收到并理解交接包

### 4.4 状态更新规范

**谁更新：** Owner 更新自己的任务。Owner 是 bot 的由 PM 代为更新。

**何时更新：**

| 事件 | Status 改为 | 附加动作 |
|------|------------|---------|
| 开始做 | `In Progress` | 更新 Status Since |
| 被卡住 | `Blocked` | 更新 Status Since + Issue comment 说明原因 |
| 做完 | `Done` | 填写 Actual Hours |
| 暂停 | `On Hold` | 更新 Status Since + 原因 |

**PM 责任：** Owner 未主动更新时，巡检中主动询问并代为更新。

### 4.5 风险管理规范（解决短板 4）

**项目启动时：** 花 10 分钟识别可预见的风险，记入 `风险登记` Issue。

**执行过程中：**
- 遇到意外 → 先自己尝试 2-3 种方案
- 解决了 → Issue comment 记录
- 解决不了 → 立刻预警

**判断边界：**

| 自己解决 | 上报/讨论 |
|---------|---------|
| 技术问题（版本、兼容性、环境） | 方向性决策（做不做、做哪个） |
| 执行路径优化 | 需求有歧义 |
| 降级方案选择 | 涉及外部影响（发布、删除） |
| 工具/依赖问题 | 成本/资源超出预期 |

---

## 五、自动巡检规则（解决短板 1、5）

### 5.1 触发

- **Heartbeat 定期触发**
- **手动触发**（"查看项目状态"）

### 5.2 流程

```
1. gh project item-list 拉取所有 active Project 的 items（JSON）
2. 解析 Status、Status Since、Estimated Hours、Depends On、Blocks、Owner
3. 按规则检测异常
4. 有异常 → 推送预警
5. 无异常 → 静默
```

### 5.3 检测规则

**超时检测：**

| 条件 | 级别 | 动作 |
|------|------|------|
| In Progress 超过 estimated_hours × 1.5 | 🟡 注意 | 主动询问进展 |
| In Progress 超过 estimated_hours × 2 | 🔴 预警 | 评估是否介入 |
| Blocked 超过 4 小时 | 🟡 注意 | 检查阻塞原因 |
| Blocked 超过 8 小时 | 🔴 预警 | 必须介入 |
| Assigned 超过 1 小时未变 In Progress | 🟡 注意 | 跟进 ACK |
| 无 estimated_hours 超过 24 小时 | 🟡 注意 | 提醒补充 |

**阻塞链检测：**

```
对每个 Status=Blocked 的 item：
1. 读取 Depends On
2. 检查前置任务状态
3. 前置也 Blocked → 继续追踪
4. 输出阻塞链 + 识别根因
```

**资源冲突检测：**

```
同一 Owner 在多个 active Project 中有 In Progress 任务 → 标记冲突
```

**里程碑偏差：**

```
项目目标日期 - 当前日期 < 剩余任务预估工时总和 → 🔴 可能延期
```

### 5.4 Bot 响应巡检（实时交互层）

PM 在推进任务时，会直接与协作 bot（如 Moss、Fabrice）交互。当 bot 无响应时，需要自动升级处理。

**前置配置：** 项目初期在项目配置中指定「人类品鉴者」（一人或多人），巡检升级时自动引用。

**规则：**

| 时间 | 级别 | 动作 |
|------|------|------|
| 15 分钟无反馈 | 🟡 催促 | @该 bot 询问进展 |
| 每 15 分钟仍无反馈 | 🟡 持续催促 | 继续 @该 bot（每 15 分钟一次） |
| 累计 1 小时以上无反馈 | 🔴 升级 | @人类品鉴者 介入 |

**说明：**
- Bot 中途回复 → 计时器重置，正常推进
- 催促期间持续每 15 分钟 @一次，不停不跳
- 升级后人类品鉴者介入判断：bot 是否故障、任务是否需要转交

### 5.5 预警消息格式

```
🚨 项目巡检预警 | {日期时间}

[{项目代号}]
🔴 {任务ID} "{任务名}" ({Owner}) — {状态} 已 {时长}，预期 {预估}
   阻塞链：{被阻塞的任务ID列表}
   建议：{具体行动建议}

资源状态：
⚠️ {Owner} 同时有 {N} 个进行中任务：{列表}
```

---

## 六、持续改进

### 6.1 排期经验库

**位置：** `projects/estimation-log.md`

**记录时机：** 每个任务 Done 时。

```markdown
| 日期 | 项目 | 任务类型 | 预估(h) | 实际(h) | 比率 | 备注 |
|------|------|---------|---------|---------|------|------|
| 4/1 | VLA | PRD 撰写 | 1 | 2 | 2.0x | 讨论确认耗时长 |
| 4/1 | VLA | App 开发 | 2 | 1.5 | 0.75x | Fabrice 效率高 |
```

**使用：** 下次排期按任务类型查历史比率修正预估。

### 6.2 项目回顾

**触发：** 项目完成或里程碑达成后。

**内容：**
1. 排期偏差分析
2. 阻塞事件复盘
3. 协调失误记录
4. 改进项 → 反馈到 skill 规范

---

## 七、Skill 文件结构

```
pm-cockpit/
├── SKILL.md                         # 核心规范
├── references/
│   ├── project-setup-checklist.md   # 项目启动清单
│   ├── id-scheme.md                 # ID 体系规范
│   ├── task-assignment-template.md  # 任务指派六要素模板
│   ├── handoff-template.md          # 环节流转交接包模板
│   ├── patrol-rules.md              # 巡检规则说明
│   ├── review-template.md           # 项目回顾模板
│   └── github-projects-setup.md     # GitHub Projects 配置指南
```

---

## 八、落地步骤

1. `gh auth refresh -s project` 添加 project scope
2. 创建 skill 目录和文件
3. 用实际项目试运行
4. 根据反馈调整规范
5. 更新 skill 文件
