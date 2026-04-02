# mano-cua 测试执行规范 v1.0

> 制定：Pichai + Moss | 日期：2026-04-02 | 来源：phase 0 回查复盘

---

## 背景

Phase 0 回查中暴露了 5 类执行缺陷，本规范将隐含假设转化为强制校验步骤，后续所有 mano-cua 测试执行必须逐项遵守。

### 已知缺陷与对应条款

| 缺陷 | 案例 | 对应条款 |
|------|------|---------|
| 判定与观测矛盾 | L2.4 脚注转换 | 条款 9-11 |
| 任务指令与 PRD 不对齐 | L3.4 响应式布局 | 条款 3 |
| 日志未本地落盘 | L1.4 代码高亮 | 条款 5, 8 |
| 测试对象 URL 未校验 | L3.4 重采 | 条款 1-2 |
| 页面状态未重置 | 多条 session 步数异常 | 条款 1 |

---

## 一、启动前（Pre-flight）

### 条款 1：强制重置页面状态

每次 mano-cua session 启动前，重新加载目标页面：

```bash
open -a "Google Chrome" <目标URL>
sleep 2
```

- Golden 测试 → 本地 golden.html（如 `file:///tmp/vla-phase0/apps/md2wechat/golden.html`）
- Buggy 测试 → 本地 buggy.html（如 `file:///tmp/vla-phase0/apps/md2wechat/buggy.html`）

确保从初始状态开始，不继承上一个 session 的编辑内容、主题、字号等残留状态。

### 条款 2：确认页面已加载完毕，URL 正确

`open -a` 执行后等待页面加载（sleep 2），确认 Chrome 当前标签页的 URL 指向目标测试对象。

### 条款 3：任务指令对齐 PRD 原文

- 任务指令必须包含 PRD 原文中的关键词（具体数值、具体行为动词），不允许同义替换
- 指令末尾加约束："仅在当前页面操作，不要导航到其他网址"
- 指令生成后与 PRD 原文做 diff check：验收标准中的关键词是否在指令中出现，缺失的补上

### 条款 4：确认测试素材/fixture 文件与 PRD 定义匹配

每条测试点使用的 fixture 文件必须与 PRD 描述的输入格式一致。例如：
- L2.4 脚注转换：PRD 要求 `[链接文字](url)` 格式 → 使用 `links-footnotes.md`（含 Markdown 链接），不得使用 `[^N]` 脚注语法的文件

### 条款 5：确认日志输出路径已配置

```bash
mano-cua run "任务指令" --expected-result "预期结果" 2>&1 | tee <本地日志路径>
```

日志路径命名规范：`trajectories/<app>-<golden|buggy>/<测试点ID>_<描述>.log`

---

## 二、执行中（In-flight）

### 条款 6：首步 URL 校验

mano-cua 启动后，检查第一步 screenshot 中的 URL 是否指向目标测试对象。发现偏离立即终止（`mano-cua stop`）并重启。

### 条款 7：自主导航拦截

mano-cua 在执行过程中如果自行导航到非目标 URL（如从本地 golden.html 跳转到 md2wechat.cn），立即终止并重启。

---

## 三、完成后（Post-flight）

### 条款 8：日志完整性确认

确认日志文件已落盘且为完整数据：
- 非 STUB 文件（行数 > 20）
- 包含逐步 action/reasoning 记录
- 包含 Session ID 和 Status 信息

### 条款 9：输出观测摘要

判定前必须先输出观测摘要，逐条列出：
- mano-cua evaluation 结果（如存在，作为首项）
- 正面观测事实
- 负面观测事实

### 条款 10：基于观测摘要给出判定 + 理由

判定必须逐条回应观测摘要中的每项事实，尤其是负面事实。判定理由必须明确引用观测证据。

### 条款 11：负面观测 + PASS 的强制约束

当 mano-cua 的观测记录中出现明确的失败描述（"未渲染"、"raw text"、"NOT proper"、"failed"、"error" 等），判定不得为 PASS，除非：
- 有合理的技术解释（如 evaluation 模型误判）
- 解释已在报告中明确记录

---

## 附录：checklist 速查表

```
启动前：
[ ] open -a Chrome <目标URL>（重置页面状态）
[ ] 确认 URL 正确
[ ] 指令含 PRD 关键词 + "不要导航到其他网址"
[ ] fixture 与 PRD 匹配
[ ] 日志 tee 到本地

执行中：
[ ] 首步 screenshot URL 正确
[ ] 无自主导航偏离

完成后：
[ ] 日志已落盘，非 STUB，行数 > 20
[ ] 观测摘要已输出（正面 + 负面）
[ ] 判定逐条回应负面事实
[ ] 负面 + PASS → 附理由
```
