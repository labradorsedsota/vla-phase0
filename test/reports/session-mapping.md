# Phase 0 Session 映射表

> 生成时间：2026-04-02 23:25 | 生成者：MOSS

---

## 一、md2wechat Golden（29 条日志 → 18 个测试点）

### 报告引用的正式 session（18 条）

| 测试点 | 判定 | Session ID | 日志文件 | 步数 | expected-result | 采集时间 | 页面重置 | 问题标注 |
|--------|------|-----------|---------|------|----------------|---------|---------|---------|
| L1.1 文件上传 | PASS | sess-..7867fbbe | L1.1_file_upload.log | 28 | N | 2026-03-31 14:20 | 未重置 | — |
| L1.2 实时编辑 | PASS | sess-..4b9b03c1 | L1.2_realtime_edit.log | 12 | N | 2026-03-31 14:23 | 未重置 | — |
| L1.3a 标题层级 | PASS | sess-..412f473c | L1.3a_heading_levels.log | 42 | N | 2026-03-31 14:24 | 未重置 | — |
| L1.3b 文本强调 | PASS | sess-..f86448e2 | L1.3b_text_emphasis.log | 24 | N | 2026-03-31 14:28 | 未重置 | — |
| L1.3c 列表渲染 | PASS | sess-..a93750fb | L1.3c_lists.log | 38 | N | 2026-03-31 14:30 | 未重置 | — |
| L1.4 代码高亮 | PASS | sess-..47bc3083 | L1.4_code_highlight_v2.log | 152 | Y | 2026-04-02 14:40 | 未重置 | v2 重采，日志已补 |
| L1.5 一键复制 | PASS | sess-..33894b6d | L1.5_copy_button.log | 59 | N | 2026-03-31 15:38 | 未重置 | — |
| L2.2 主题切换 | PASS | sess-..258951ce | L2.2_theme_switch.log | 13 | N | 2026-03-31 14:41 | 未重置 | — |
| L2.3 字号调节 | PASS | sess-..080c1170 | L2.3_font_size.log | 12 | N | 2026-03-31 14:42 | 未重置 | — |
| L2.4 脚注转换 | PASS | sess-..3ad34240 | L2.4_footnotes_v2.log | 44 | Y | 2026-04-02 14:59 | 未重置 | v2 重采，旧版 INVALID（素材错误） |
| L2.5 表格渲染 | PASS | sess-..b81cb1b7 | L2.5_table.log | 12 | N | 2026-03-31 14:43 | 未重置 | — |
| L2.6 引用块样式 | PASS | sess-..2c0bc314 | L2.6_blockquote.log | 28 | N | 2026-03-31 15:57 | 未重置 | — |
| L2.7 自定义主色 | PASS | sess-..2585b22d | L2.7_custom_color_v4.log | 23 | N | 2026-03-31 18:59 | 未重置 | v4，前 3 次重试 |
| L3.1 长文档性能 | PASS | sess-..2727cead | L3.1_long_document_v3.log | 20 | N | 2026-03-31 18:56 | 未重置 | v3，前 2 次重试 |
| L3.2 特殊字符 | PASS | sess-..31b0fc55 | L3.2_special_chars.log | 12 | N | 2026-03-31 15:23 | 未重置 | — |
| L3.3 空文件处理 | PASS | sess-..0ba15836 | L3.3_empty_file.log | 26 | N | 2026-03-31 15:25 | 未重置 | — |
| L3.4 响应式布局 | FAIL | sess-..17e51949 | L3.4_responsive_v2.log | 9 | Y | 2026-04-02 15:16 | 未重置 | v2 重采，测试对象为 md2wechat.cn（非本地 Golden App） |
| L3.5 连续主题切换 | PASS | sess-..08b5284f | L3.5_rapid_theme_switch.log | 34 | N | 2026-03-31 14:45 | 未重置 | 报告中 Session ID 截断有误（08b52847 vs 08b5284f） |

### 非正式 session（11 条：重试、合并、废弃）

| 日志文件 | Session ID | 步数 | 状态 | 说明 |
|---------|-----------|------|------|------|
| L2.1_drag_upload.log | sess-..5820d0a2 | 53 | 跳过 | mano-cua 不支持拖拽 |
| L2.1_drag_upload_v2.log | — | 0 | 跳过 | 空文件 |
| L2.4_L2.6_footnotes_blockquote.log | sess-..f01c7564 | 50 | 废弃 | 合并 session（违反隔离原则） |
| L2.4_footnotes.log | sess-..527a5005 | 36 | 废弃 | 被 v2 替代（素材错误） |
| L2.7_custom_color.log | sess-..e228fe95 | 56 | 废弃 | 被 v4 替代 |
| L2.7_custom_color_redo.log | sess-..965d1750 | 20 | 废弃 | 被 v4 替代 |
| L3.1_long_document.log | sess-..66901c21 | 48 | 废弃 | 被 v3 替代 |
| L3.1_long_document_redo.log | sess-..e92f2f66 | 43 | 废弃 | 被 v3 替代 |
| L3.1_long_document_final.log | sess-..5c347424 | 40 | 废弃 | 被 v3 替代 |
| L3.2_L3.3_special_empty.log | sess-..3a39c8d0 | 12 | 废弃 | 合并 session（违反隔离原则） |
| L3.4_responsive.log | sess-..e822bd65 | 16 | 废弃 | 被 v2 替代 |

---

## 二、md2wechat Buggy（18 条，全部 STUB）

| 测试点 | 判定 | Session ID | 日志状态 | 采集时间 | 问题标注 |
|--------|------|-----------|---------|---------|---------|
| L1.1 文件上传 | PASS | sess-..61cee7ce | STUB | 2026-04-01 12:32 | 日志不可审计 |
| L1.2 实时编辑 | PASS | sess-..5bf5002a | STUB | 2026-04-01 12:49 | 日志不可审计 |
| L1.3a 标题层级 | PASS | sess-..968bfcee | STUB | 2026-04-01 12:51 | 日志不可审计 |
| L1.3b 文本强调 | WARN | sess-..2084bb52 | STUB | 2026-04-01 12:57 | 日志不可审计 |
| L1.3c 列表渲染 | PASS | sess-..eef167af | STUB | 2026-04-01 13:01 | 日志不可审计 |
| L1.4 代码高亮 | PASS | sess-..141628 | STUB | 2026-04-01 14:16 | 日志不可审计 |
| L1.5 一键复制 | PASS | sess-..35e5a541 | STUB | 2026-04-01 13:02 | 日志不可审计 |
| L2.2 主题切换 | PASS | sess-..ed473824 | STUB | 2026-04-01 13:08 | 日志不可审计 |
| L2.3 字号调节 | PASS | sess-..024d3ff9 | STUB | 2026-04-01 13:12 | 日志不可审计 |
| L2.4 脚注转换 | FAIL | sess-..0ebdbe70 | STUB | 2026-04-01 13:13 | 日志不可审计 |
| L2.5 表格渲染 | PASS | sess-..47ae6a2d | STUB | 2026-04-01 13:25 | 日志不可审计 |
| L2.6 引用块 | FAIL | sess-..d1cd8271 | STUB | 2026-04-01 13:37 | 日志不可审计 |
| L2.7 自定义主色 | FAIL | sess-..sharp-ridge | STUB | 2026-04-01 13:40 | 日志不可审计 |
| L3.1 长文档 | PASS | sess-..39bd21e3 | STUB | 2026-04-01 13:42 | 日志不可审计 |
| L3.2 特殊字符 | PASS | sess-..62211518 | STUB | 2026-04-01 13:45 | 日志不可审计 |
| L3.3 空文件 | PASS | sess-..450087bc | STUB | 2026-04-01 13:46 | 日志不可审计 |
| L3.4 响应式 | FAIL | sess-..905a2440 | STUB | 2026-04-01 13:48 | 日志不可审计 |
| L3.5 连续主题 | PASS | sess-..e4e52f9c | STUB | 2026-04-01 13:51 | 日志不可审计 |

---

## 三、TripSplit Golden（13 条，全部完整）

| 测试点 | 判定 | Session ID | 日志文件 | 步数 | expected-result | 采集时间 | 页面重置 | 问题标注 |
|--------|------|-----------|---------|------|----------------|---------|---------|---------|
| TC-L1.1 创建旅行 | PASS | sess-..0f809132 | TC-L1.1_create_trip.log | 78 | Y | 2026-04-01 15:27 | 未重置 | — |
| TC-L1.2 添加费用 | PASS | sess-..fdd34c41 | TC-L1.2_add_expense.log | 21 | Y | 2026-04-01 15:35 | 未重置 | — |
| TC-L1.3 均分 | PASS | sess-..215cb317 | TC-L1.3_equal_split.log | 9 | Y | 2026-04-01 15:38 | 未重置 | — |
| TC-L1.4 费用列表 | PASS | sess-..a0143ea9 | TC-L1.4_expense_list.log | 38 | Y | 2026-04-01 15:41 | 未重置 | — |
| TC-L1.7 多笔费用 | PASS | sess-..868bb532 | TC-L1.7_multi_expense_v3.log | 10 | Y | 2026-04-01 16:06 | 未重置 | v3，前 2 次重试 |
| TC-L2.1 按比例分 | PASS | sess-..c2bdc5c4 | TC-L2.1_ratio_split.log | 33 | Y | 2026-04-01 16:08 | 未重置 | — |
| TC-L2.3 类别筛选 | PASS | sess-..d9170df8 | TC-L2.3_category_filter.log | 12 | Y | 2026-04-01 16:13 | 未重置 | — |
| TC-L2.4 编辑费用 | PASS | sess-..1cde55e4 | TC-L2.4_edit_expense.log | 17 | Y | 2026-04-01 16:14 | 未重置 | — |
| TC-L2.5 删除费用 | PASS | sess-..cb7e6aac | TC-L2.5_delete_expense.log | 12 | Y | 2026-04-01 16:16 | 未重置 | — |
| TC-L3.1 精度 | PASS | sess-..12bd98f8 | TC-L3.1_precision.log | 9 | Y | 2026-04-01 16:20 | 未重置 | — |
| TC-L3.3 空旅行 | PASS | sess-..c7c981ed | TC-L3.3_empty_trip.log | 10 | Y | 2026-04-01 16:18 | 未重置 | — |

*注：TC-L1.7 有 v1/v2 两个废弃 session（sess-..c5ae9ce1, sess-..d6e2bd2a），未纳入正式报告。*

---

## 四、TripSplit Buggy（3 条，全部完整）

| 测试点 | 判定 | Session ID | 日志文件 | 步数 | 采集时间 | 问题标注 |
|--------|------|-----------|---------|------|---------|---------|
| TC-L1.1 创建旅行 | PASS | sess-..53b52478 | TC-L1.1_create_trip.log | 27 | 2026-04-01 16:34 | — |
| TC-L1.4 排序 | UNMATCHED | sess-..fec48b3a | TC-L1.4_sort_order.log | 7 | 2026-04-01 16:37 | Bug 命中 |
| TC-L1.6 结算方向 | UNMATCHED | sess-..6f338a61 | TC-L1.6_settle_direction.log | 9 | 2026-04-01 16:38 | Bug 命中 |

---

## 五、已识别问题汇总

| 问题类型 | 影响范围 | 详情 |
|---------|---------|------|
| 判定与观测矛盾 | md2wechat Golden L2.4（原版） | 观测记录含"未渲染"但判定 PASS，已重采修正 |
| 素材不匹配 | md2wechat Golden L2.4（原版） | 使用了 `[^N]` 脚注语法而非 Markdown 链接格式 |
| 指令失真 | md2wechat Golden L3.4（原版） | "resize to half screen" 丢失 PRD 要求的 "768px + 上下分栏" |
| 测试对象 URL 错误 | md2wechat Golden L3.4（v2） | 访问 md2wechat.cn 而非本地 golden.html |
| 日志未落盘 | md2wechat Golden L1.4（原版） | 原 session 日志未保存，已重采补齐 |
| 日志全部 STUB | md2wechat Buggy 全部 18 条 | 仅含元数据，完整数据存于 mano-cua 云端 |
| 截图未落盘 | 全部轨迹 | 本地 0 张截图，完整截图存于 mano-cua 云端 |
| expected-result 缺失 | md2wechat Golden 25/29 条 | 未触发 mano-cua 自动评估 |
| 合并 session | md2wechat Golden 2 条 | L2.4+L2.6、L3.2+L3.3 合并执行 |
| Session ID 截断错误 | md2wechat Golden L3.5 | 报告中 08b52847 vs 实际 08b5284f |
| 页面状态未重置 | 全部轨迹 | 所有 session 均未在启动前重新加载页面 |
