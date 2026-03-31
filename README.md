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
步骤 8: Moss 拿 Bug 清单作为 Ground Truth，标注轨迹数据
```

### ⚠️ 关键约束

- **步骤 2 必须在步骤 6 之前完成** — Moss 生成测试用例时不接触 Bug 清单，保证测试客观性
- **步骤 2/3/4 可并行** — 测试用例生成与应用开发互不依赖
- **步骤 7 diff 机制** — 同一套用例跑两个版本，Golden pass + Buggy fail 的差异点即 Bug 命中点，自动产出正负样本对

## 里程碑

| 阶段 | 内容 | 状态 |
|------|------|------|
| Day 1 (3/30) | PRD + 应用开发 + mano-cua 实测 | ✅ 完成 |
| Day 2 (3/31) | md2wechat Golden 采集 + TripSplit 开发 | ✅ 完成 |
| Day 3 | md2wechat Buggy 采集 + TripSplit 采集 | 待开始 |
| Day 3~4 | 人工 Ground Truth 标注 | 待开始 |
| Day 4 | Phase 0 评估报告 + 数据打包 | 待开始 |

## 文档结构

```
project/vla-phase0/
├── README.md                    # Pichai | 本文件
├── DECISIONS.md                 # Pichai/Moss | 决策+待确认
├── prds/                        # Pichai | PRD + L1/L2/L3 + Bug清单
├── apps/                        # Fabrice | Golden/Buggy App + 技术说明
├── test/fixtures/               # Moss | 测试输入数据（按App分子目录）
├── test/reports/                # Moss | 验收结果
└── meetings/                    # Pichai | 讨论纪要（只记结论和分歧）
```

## 文件维护规则

- 每个文件头部标注 Owner
- DECISIONS.md：Pichai 主维护，Moss 可追加，每条标注决策者+时间
- Bug 清单：Fabrice 提交内容，Pichai 审核后写入 PRD 末尾章节
- Moss 生成测试用例时只读 PRD Bug 清单以上的内容
