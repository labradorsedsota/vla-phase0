# TripSplit Buggy App — 数据采集报告

> Owner: Moss | 更新于 2026-04-01

## 采集概要

| 指标 | 数值 |
|------|------|
| 总 session 数 | 5（含重试） |
| COMPLETED | 2 |
| STOPPED_BY_USER | 1（B1 日期输入卡住） |
| 采集完成率 | 3/19（仅针对已知 Bug 点） |

## 采集策略说明

TripSplit Buggy App 仅针对 3 个已知 Bug 对应的用例进行采集，未做全量覆盖。原因：

1. **HTML date input 限制**：mano-cua 对浏览器原生日期选择器操作效率极低（40+ 步/次），全量采集预估需 4+ 小时
2. **DB 预填充策略限制**：为规避日期输入问题采用的混合策略无法产出完整 GUI 创建轨迹
3. **投入产出判断**：3 条负样本已精确命中全部 Bug 且有 Golden 对照，全量采集主要增加「Buggy 但 PASS」类正样本，边际价值有限

如 Phase 1 需样本平衡，可补采 6-8 条非 Bug 路径（L2.3 筛选、L2.4 编辑、L2.5 删除、L3.1 精度、L3.3 空旅行等）。

## 重试/失败 session

| Session ID | 用例 | 原因 |
|-----------|------|------|
| `sess-20260401162235-b228e947bd934ec8b9b53f20f032eef9` | TC-L1.1 | 日期输入困难，killed |
| `sess-20260401163408-53b524787daf4c88926c5cf2429f8e20` | TC-L1.1 | 日期输入困难，killed（40步后终止） |

## 已知 Bug 捕获情况 — 3/3 全部命中

| Bug ID | 测试点 | 预期行为（Golden） | 实际表现（Buggy） |
|--------|--------|------------------|-----------------|
| B1 | TC-L1.1 创建旅行 | 创建后刷新旅行仍存在 | POST 后 302 重定向，旅行列表为空（db.commit 遗漏） |
| B2 | TC-L1.4 账单列表 | 按日期 DESC 倒序排列 | 按日期 ASC 正序排列（ORDER BY 方向反） |
| B3 | TC-L1.5/L1.6 差额+结算 | 差额 = paid - owed | 差额 = owed - paid（balance 公式写反） |

## 有效轨迹清单

### B1 — TC-L1.1 创建旅行（数据持久化失败）

| 字段 | 值 |
|------|------|
| Session ID | `sess-20260401163408-53b524787daf4c88926c5cf2429f8e20` |
| 状态 | STOPPED_BY_USER（40 步后因日期输入卡住终止，轨迹不完整） |
| 补充验证 | curl POST /trip/create → 302 FOUND → GET / 旅行列表为空 |
| Bug 确认 | db.commit() 遗漏，事务未提交，连接关闭时回滚 |
| 代码定位 | `buggy/app.py` L151 |

### B2 — TC-L1.4 账单列表排序（排序方向反）

| 字段 | 值 |
|------|------|
| Session ID | `sess-20260401163705-fec48b3a997f4b5493ffbf9bee47fe7f` |
| 状态 | COMPLETED |
| 步数 | 2 |
| 采集证据 | 截图显示记录顺序为 4/1→4/2→4/3（ASC），Golden 为 4/3→4/2→4/1（DESC） |
| Bug 确认 | ORDER BY date ASC 应为 DESC |
| 代码定位 | `buggy/app.py` L244/L249 |

### B3 — TC-L1.5/L1.6 差额+结算（结算方向反）

| 字段 | 值 |
|------|------|
| Session ID | `sess-20260401163824-6f338a615b094c79ae6ba5495004f5dd` |
| 状态 | COMPLETED |
| 步数 | 3 |
| 采集证据 | 截图显示小明+¥50/小红+¥200/小李-¥250，Golden 为小明-¥50/小红-¥200/小李+¥250 |
| Bug 确认 | balance = owed - paid 应为 paid - owed |
| 代码定位 | `buggy/app.py` L375-376 |

## 备注

- 所有 session 截图数据已上传 mano-cua 云端
- 本地 stdout 日志存于 `/tmp/vla-phase0/trajectories/tripsplit-buggy/`
- B1 的 mano-cua 轨迹不完整（STOPPED_BY_USER），Bug 验证通过 curl 补充完成
- B2 和 B3 的 mano-cua 轨迹完整（COMPLETED），数据可直接用于正负样本对
