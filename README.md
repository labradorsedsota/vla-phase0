# VLA Phase 0 — 视觉自动化验收测试数据采集

> Owner: Pichai

## 项目目标

用 mano-cua（视觉自动化工具）对 Web 应用跑验收测试，采集操作轨迹数据，人工标注 Ground Truth，用于评估 VLA 模型作为 QA 工具的可行性。

Phase 0 目标：2 个 A 类应用，跑通全流程，采集 20-30 条高质量标注轨迹。

## 核心概念

| 概念 | 定义 |
|------|------|
| **A 类应用** | 简单工具型，输入→处理→可验证输出（如 Markdown 转换器、JSON Formatter） |
| **B 类应用** | 中等交互，含状态管理（如 Todo List、表单系统）— Phase 1 |
| **C 类应用** | 复杂交互，含多步流程（如审批流、权限系统）— Phase 1+ |
| **Golden App** | 功能完全正确的应用版本（正样本） |
| **Buggy App** | 在 Golden 基础上植入 2-3 个真实感 Bug 的版本（负样本） |
| **L1 验收** | 基础功能验证 — 必须全部通过，否则应用不可用 |
| **L2 验收** | 交互体验 + 边界情况 — 核心体验完整性 |
| **L3 验收** | 高级场景 + 鲁棒性 — 极端条件下的表现 |

## 团队分工

| 角色 | 负责人 | 职责 |
|------|--------|------|
| 产品经理 | Pichai | PRD 编写、L1/L2/L3 验收描述、Bug 清单审核、项目文档维护 |
| 开发工程师 | Fabrice | Golden App + Buggy App 开发、Bug 设计与植入、技术文档 |
| QA 工程师 | Moss | 验收任务生成、mano-cua 采集、数据清洗、测试报告 |
| 品鉴者 | 人工 | Ground Truth 标注、争议裁定、质量审核 |

## 8 步工作流程

```
步骤 1: Pichai 出 PRD + L1/L2/L3 验收描述
步骤 2: Moss 基于 PRD（不含 Bug 信息）生成验收任务和测试数据  ⚠️
步骤 3: Fabrice 开发 Golden App
步骤 4: Fabrice 独立设计 Bug + 开发 Buggy App
步骤 5: Fabrice 将 Bug 清单提交给 Pichai
步骤 6: Pichai 审核合理性后写入 PRD 末尾
步骤 7: mano-cua 用同一套测试用例分别跑 Golden 和 Buggy
```

> Ground Truth 标注由 Mano 团队负责，不在本工作流范围内。

### ⚠️ 关键约束

- **步骤 2 必须在步骤 6 之前完成** — Moss 生成测试用例时不接触 Bug 清单，保证测试客观性
- **步骤 2/3/4 可并行** — 测试用例生成与应用开发互不依赖
- **步骤 7 diff 机制** — 同一套用例跑两个版本，Golden pass + Buggy fail 的差异点即 Bug 命中点，自动产出正负样本对

## 当前进度（更新于 2026-04-01 18:15）

### App 1: md2wechat（Markdown 转微信公众号排版）— 集中完成中

| 步骤 | 状态 | 说明 |
|------|------|------|
| 1. PRD + L1/L2/L3 | ✅ 完成 | `prds/md2wechat.md`，19 条验收点 |
| 2. 测试用例生成 | ✅ 完成 | Moss 已生成 |
| 3. Golden App | ✅ 完成 | `apps/md2wechat/golden.html` |
| 4. Buggy App | ✅ 完成 | `apps/md2wechat/buggy.html`，3 个 bug |
| 5. Bug 清单提交 | ✅ 完成 | Fabrice 提交 |
| 6. Bug 清单审核 | ✅ 完成 | 已写入 PRD 末尾 |
| 7. mano-cua 采集 | ✅ 完成 | Golden 18/19，Buggy 18/18，共 36 条有效轨迹 |

**采集详情：**
- Golden App：见 `test/reports/md2wechat-golden-collection.md`（17/19 完成）
- Buggy App：见 `test/reports/md2wechat-buggy-collection.md`（17/17 完成，3 个 Bug 全部捕获）
- L2.1 拖拽上传：标记工具不可采集（mano-cua 无法跨应用拖拽）
- L1.4 代码高亮：等 Fabrice 修复 marked.js 后补采
- ⚠️ **Buggy 本地日志缺失：** 采集时未做 stdout 重定向，18 条轨迹仅有 [STUB] 元数据存根，逐步操作日志不可恢复。详见采集报告。

### App 2: tripsplit（旅行分账记账本）

| 步骤 | 状态 | 说明 |
|------|------|------|
| 1. PRD + L1/L2/L3 | ✅ 完成 | `prds/tripsplit.md`，19 条验收点 |
| 2. 测试用例生成 | ✅ 完成 | Moss 生成 19 条用例，`test/tripsplit-testcases.md` |
| 3. Golden App | ✅ 完成 | `apps/tripsplit/golden/`（Flask 多文件） |
| 4. Buggy App | ✅ 完成 | `apps/tripsplit/buggy/`，3 个 bug |
| 5. Bug 清单提交 | ✅ 完成 | Fabrice 提交 |
| 6. Bug 清单审核 | ✅ 完成 | 已写入 PRD 末尾（3/31 16:05） |
| 7. mano-cua 采集 | ✅ 完成 | Golden 11 条 + Buggy 3 条，3/3 Bug 命中 |
| 8. Ground Truth 标注 | ✅ 完成 | `test/reports/tripsplit-ground-truth.md` |

### Phase 0 评估报告

- ✅ 已提交：`test/reports/phase0-evaluation.md`
- 50 条轨迹，7 组正负样本对，6/6 Bug 检出率 100%
- 待补充：TripSplit Buggy 采集覆盖说明 + 「Buggy 但 PASS」标注策略

## 里程碑

| 阶段 | 内容 | 状态 |
|------|------|------|
| Day 1（3/30-31） | PRD × 2 + 应用开发 × 2 + Bug 审核 × 2 | ✅ 完成 |
| Day 2（4/1） | Moss 测试用例 + mano-cua 采集 + Ground Truth 标注 | ✅ 完成 |
| Day 2（4/1） | Phase 0 评估报告 | ✅ 已提交，待修订 |
| 待定 | 人工 Ground Truth 复核 + 数据打包交付 | ⏳ 待启动 |

## 文档结构

```
project/vla-phase0/
├── README.md                    # Pichai | 本文件
├── DECISIONS.md                 # Pichai/Moss | 决策+待确认
├── prds/                        # Pichai | PRD + L1/L2/L3 + Bug清单
│   ├── md2wechat.md
│   └── tripsplit.md
├── apps/                        # Fabrice | Golden/Buggy App
│   ├── md2wechat/
│   │   ├── golden.html
│   │   └── buggy.html
│   └── tripsplit/
│       ├── golden/
│       └── buggy/
├── test/fixtures/               # Moss | 测试输入数据（按App分子目录）
├── test/reports/                # Moss | 验收结果
└── meetings/                    # Pichai | 讨论纪要
```

## 文件维护规则

- 每个文件头部标注 Owner
- DECISIONS.md：Pichai 主维护，Moss 可追加，每条标注决策者+时间
- Bug 清单：Fabrice 提交内容，Pichai 审核后写入 PRD 末尾章节
- Moss 生成测试用例时只读 PRD Bug 清单以上的内容
