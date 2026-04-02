# pm-cockpit 详细方案

## 一、整体架构

```
GitHub Projects（数据层 + 展示层）
├── 每个项目 = 一个 GitHub Project
├── 每个任务 = 一个 Issue（带自定义字段）
├── 所有人通过 Web UI 查看/操作
└── Bot 通过 gh CLI 读写

pm-cockpit Skill（规范层 + 巡检层）
├── 项目启动规范
├── 任务指派规范 ← 解决短板2
├── 环节流转规范 ← 解决短板3
├── 风险管理规范 ← 解决短板4
├── 自动巡检规则 ← 解决短板1、5
└── 持续改进机制 ← 解决短板5
```

---

## 二、GitHub Projects 数据结构

### 2.1 Project 创建规范

每个项目对应一个 GitHub Project，创建时设定：

```bash
gh project create --owner labradorsedsota --title "[P1] VLA Phase 0 - 测试数据采集"
```

命名规范：`[优先级] 项目名 - 一句话描述`

### 2.2 自定义字段

在每个 Project 上创建以下字段：

| 字段名 | 类型 | 选项 / 说明 |
|--------|------|-------------|
| Status | SINGLE_SELECT | `Todo`, `Assigned`, `In Progress`, `Blocked`, `Done`, `On Hold` |
| Priority | SINGLE_SELECT | `P0-紧急`, `P1-重要`, `P2-常规`, `P3-低优` |
| Owner | TEXT | 负责人 ID（pichai / fabrice / moss / 人名） |
| Stage | SINGLE_SELECT | 按项目定义，如 `需求`, `研发`, `测试`, `验收` |
| Estimated Hours | NUMBER | 预估工时（小时） |
| Actual Hours | NUMBER | 实际工时（完成时填写） |
| Status Since | DATE | 进入当前状态的日期（每次改 Status 时同步更新） |
| Due Date | DATE | 截止日期（如有） |
| Depends On | TEXT | 前置依赖的 Issue 编号，如 `#1, #3` |
| Blocks | TEXT | 完成后解锁的 Issue 编号，如 `#5, #6` |

**关键约束：每次修改 Status 时，必须同步更新 Status Since。** 这是整个时间感知体系的基础。

### 2.3 Issue 使用规范

每个任务创建为 Issue，body 包含：

```markdown
## 任务描述
[具体做什么]

## 输入物
- [链接/位置/说明]

## 产出标准
- [完成标准1]
- [完成标准2]

## 备注
- [已知风险、约束、注意事项]
```

Labels 用于分类：
- `stage:需求` / `stage:研发` / `stage:测试` — 所属环节
- `blocked` — 被阻塞（与 Status 字段联动）
- `critical-path` — 关键路径任务

### 2.4 视图配置

每个 Project 创建以下视图：

| 视图名 | 类型 | 用途 |
|--------|------|------|
| 看板 | Board（按 Status 分列） | 全局状态概览 |
| 按负责人 | Table（按 Owner 分组） | 每个人查看自己的任务 |
| 按环节 | Table（按 Stage 分组） | 查看各环节进展 |
| 阻塞项 | Table（过滤 Status=Blocked） | 快速定位阻塞 |
| 时间线 | Table（按 Due Date 排序） | 截止日期概览 |

---

## 三、Skill 核心规范

### 3.1 项目启动流程

**触发：** 收到新项目需求且确认要做时。

**步骤：**

1. **创建 GitHub Project**
   - 命名：`[优先级] 项目名 - 一句话描述`
   - 创建自定义字段（按 2.2 的字段列表）
   - 配置视图（按 2.4）

2. **定义项目元信息**（写在 Project Description 中）
   ```
   目标：[一句话，可验证的成功标准]
   环节流：需求 → 研发 → 测试 → 验收
   团队：Pichai(PM), Fabrice(研发), Moss(测试)
   目标日期：YYYY-MM-DD
   ```

3. **拆解任务并创建 Issues**
   - 按环节拆解
   - 每个 Issue 填写：描述、输入物、产出标准
   - 设置依赖关系（Depends On / Blocks）
   - 设置预估工时（Estimated Hours）
   - 识别关键路径，打 `critical-path` 标签

4. **识别可预见的风险**
   - 在 Project 中创建一个 `风险登记` Issue（pinned），列出已识别的风险和预案
   - 不求全面，识别能识别的

5. **通知团队**
   - 在相关群中发送项目启动信息，附 Project 链接

### 3.2 任务指派规范（解决短板2）

**触发：** 将任务分配给某个人/bot 时。

**指派消息必须包含六要素：**

```
📌 任务指派

1. 做什么：[具体任务描述]
2. 输入物：[链接/位置，注意事项]
3. 产出标准：[做到什么程度算完成]
4. 时间预期：[预计 X 小时完成，截止 YYYY-MM-DD HH:MM]
5. Issue 链接：[GitHub Issue URL]
6. 请确认收到并告知是否可以开始
```

**指派后必须做的：**
- Issue 的 Status 改为 `Assigned`，Status Since 更新为当前时间
- Owner 字段设为负责人
- 等待对方确认（ACK）
- ACK 后 Status 改为 `In Progress`，Status Since 再次更新
- 在 tasks.yaml（或 Issue comment）中记录下次跟进时间

**如果 30 分钟未收到 ACK：**
- 主动询问一次
- 仍无回应 → 预警给 PM（我自己），评估是否需要调整

### 3.3 环节流转规范（解决短板3）

**触发：** 项目从一个环节进入下一个环节时。

**流转动作：**

1. **生成交接包**（发到下一环节的群中）：

```
## 🔄 流转：[项目名] [当前环节] → [下一环节]

**结论：**（确认的结论，不是讨论过程）
- [确认的范围]
- [明确排除的]

**交付物：**
- [链接1]
- [链接2]

**验收标准：**
- [下一环节拿什么标准判断上一环节产出合格]

**已知风险/约束：**
- [上一环节发现的、可能影响下一环节的问题]

**优先级：** Px
**期望完成时间：** YYYY-MM-DD

**反向触发条件：**
如遇 [xxx情况]，@Pichai 回 [上一环节群] 讨论，不要自行决定。
```

2. **更新 GitHub Project**
   - 相关 Issues 的 Stage 字段更新
   - 下一环节的 Issues 状态改为 `Todo`

3. **确认下一环节负责人已收到并理解交接包**

### 3.4 状态更新规范

**谁更新：** 任务的 Owner 负责更新自己任务的状态。如果 Owner 是 bot，由 PM（我）代为更新。

**什么时候更新：**
- 开始做 → `In Progress` + Status Since
- 被卡住 → `Blocked` + Status Since + 在 Issue comment 说明卡在哪
- 做完了 → `Done` + Actual Hours
- 暂停 → `On Hold` + Status Since + 原因

**PM 的责任：** 如果 Owner 没有主动更新，PM 在巡检时主动询问并代为更新。

### 3.5 风险管理规范（解决短板4）

**项目启动时：**
- 花 10 分钟识别可预见的风险，记入 `风险登记` Issue
- 每个风险记录：描述、影响程度、预案（如有）

**执行过程中：**
- 遇到新风险/意外问题 → 先自己尝试解决（2-3 种方案）
- 解决后 → 在 Issue comment 记录问题和解决方式
- 解决不了 → 立刻预警，不要默默卡住

**判断边界：**

| 自己解决 | 上报/讨论 |
|---------|---------|
| 技术问题（版本冲突、兼容性、环境问题） | 方向性决策（做不做、做哪个） |
| 执行路径优化 | 需求有歧义 |
| 降级方案选择 | 涉及外部影响（发布、删除、推送） |
| 工具/依赖问题 | 成本/资源超出预期 |

---

## 四、自动巡检规则（解决短板1、5）

### 4.1 巡检触发

- **Heartbeat 定期触发**（每次 heartbeat 轮询时执行）
- **手动触发**（收到"查看项目状态"类请求时）

### 4.2 巡检流程

```
1. gh project item-list 拉取所有 active Project 的 items（JSON 格式）
2. 解析每个 item 的 Status、Status Since、Estimated Hours、Depends On、Blocks、Owner
3. 按规则检测异常
4. 有异常 → 推送预警消息
5. 无异常 → 静默
```

### 4.3 检测规则

**超时检测：**

| 条件 | 级别 | 动作 |
|------|------|------|
| In Progress 超过 estimated_hours × 1.5 | 🟡 注意 | 主动询问进展 |
| In Progress 超过 estimated_hours × 2 | 🔴 预警 | 推消息，评估是否需要介入 |
| Blocked 超过 4 小时 | 🟡 注意 | 检查阻塞原因 |
| Blocked 超过 8 小时 | 🔴 预警 | 必须介入处理 |
| Assigned 超过 1 小时未变为 In Progress | 🟡 注意 | ACK 可能没收到，主动跟进 |
| 无 estimated_hours 的任务超过 24 小时 | 🟡 注意 | 提醒补充预估 |

**阻塞链检测：**

```
对每个 Status=Blocked 的 item：
1. 读取其 Depends On 字段
2. 检查前置任务的状态
3. 如果前置任务也是 Blocked → 继续追踪
4. 输出完整阻塞链：
   "T5(Blocked) ← T2(In Progress, 超时3h) ← T1(Done)"
5. 识别根因（链中第一个非 Done 的任务）
```

**资源冲突检测：**

```
按 Owner 聚合所有 active Project 中 Status=In Progress 的任务：
如果同一个 Owner 有 2+ 个 In Progress 任务 → 标记冲突
输出："Fabrice 当前有 2 个进行中任务：[项目A] T3, [项目B] T2，需确认优先级"
```

**里程碑偏差检测：**

```
项目目标日期 - 当前日期 < 剩余任务预估工时总和 → 🔴 项目可能延期
```

### 4.4 预警消息格式

```
🚨 项目巡检预警 | 2026-04-02 15:00

[VLA Phase 0]
🔴 T2 "生成测试用例" (Moss) — Blocked 已 27h，预期 2h
   阻塞链：T5, T6 等待 T2 完成
   建议：立即跟进 Moss 状态，确认阻塞原因

🟡 T8 "数据标注" — 无预估工时，建议补充

[项目B]
🟢 无异常

资源状态：
⚠️ Fabrice 同时在 2 个项目中有进行中任务
```

---

## 五、持续改进

### 5.1 排期经验库

**存储位置：** workspace 中的 `projects/estimation-log.md`

**记录时机：** 每个任务 Done 时，记录预估 vs 实际：

```markdown
| 日期 | 项目 | 任务类型 | 预估(h) | 实际(h) | 比率 | 备注 |
|------|------|---------|---------|---------|------|------|
| 4/1 | VLA | PRD撰写 | 1 | 2 | 2.0x | 讨论确认耗时长 |
| 4/1 | VLA | App开发(工具型) | 2 | 1.5 | 0.75x | Fabrice效率高 |
```

**使用方式：** 下次排期时，按任务类型查历史比率，用数据修正预估。

### 5.2 项目回顾

**触发：** 项目完成或里程碑达成后。

**回顾内容：**
1. 排期偏差分析 —— 哪些估准了、哪些偏了、为什么
2. 阻塞事件复盘 —— 发生了什么阻塞、怎么解决的、能否提前避免
3. 协调失误记录 —— 有没有传话不到位、跟进不及时的情况
4. 改进项 —— 具体的行动改进，反馈到 skill 规范中

---

## 六、Skill 文件结构

```
pm-cockpit/
├── SKILL.md                         # 核心规范（何时触发什么动作）
├── references/
│   ├── project-setup-checklist.md   # 项目启动清单
│   ├── task-assignment-template.md  # 任务指派六要素模板
│   ├── handoff-template.md          # 环节流转交接包模板
│   ├── patrol-rules.md              # 巡检规则详细说明
│   ├── review-template.md           # 项目回顾模板
│   └── github-projects-setup.md     # GitHub Projects 字段和视图配置指南
```

---

## 七、落地步骤

1. **授权：** `gh auth refresh -s project` 添加 project scope
2. **创建 skill 目录和文件**
3. **用一个实际项目（VLA Phase 0 或新项目）试运行**
4. **根据试运行反馈调整规范**
5. **将调整后的规范更新回 skill 文件**
