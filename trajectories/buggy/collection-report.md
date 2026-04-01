# md2wechat Buggy App — 数据采集报告

> Owner: MOSS | 采集时间: 2026-04-01

## 采集概要

| 指标 | 数值 |
|------|------|
| 总 session 数 | 17 |
| COMPLETED | 17 |
| 工具不可采集 | 1（L2.1，同 Golden） |
| 等待修复 | 1（L1.4，同 Golden） |
| 采集完成率 | 17/17（100%） |

## Bug 捕获情况

| Bug ID | 关联测试点 | 预期 Bug | 实际捕获 | 状态 |
|--------|-----------|---------|---------|------|
| B1 | L2.4 脚注转换 | 脚注编号全部显示 [0] | 全部脚注显示 [0]，不递增 | 已捕获 |
| B2 | L2.5 表格渲染 | 隔行不变色 | 所有行背景色相同，无 zebra striping | 已捕获 |
| B3 | L2.2 主题切换 | 切换主题后预览不刷新 | 标题装饰条颜色不跟随主题变化 | 已捕获 |

## 额外发现的异常

| 测试点 | 异常描述 | 类型 |
|--------|---------|------|
| L1.3b 文本强调 | Evaluation 标注斜体渲染可能异常 | MODEL_REASONING |
| L1.5 复制按钮 | 粘贴到 TextEdit 后标题装饰色/边框丢失 | UNMATCHED_OUTCOME |
| L3.1 长文档性能 | 编辑时页面滚动位置重置 | UNMATCHED_OUTCOME |
| L3.5 连续主题切换 | 切换5个主题后预览区样式始终不变（B3 的延伸表现） | UNMATCHED_OUTCOME |

## 有效 COMPLETED 轨迹清单

### L1 层（基础功能）— 6/7 完成（跳 L1.4）

| Case | Session ID | 步数 | Evaluation |
|------|-----------|------|------------|
| L1.1 文件上传 | `sess-20260401123241-61cee7ce3be9435886f2a52d2dadd1b0` | 46 | success |
| L1.2 实时编辑 | `sess-20260401124952-5bf5002af4e04103b1c0accd7f63a3ad` | 4 | success |
| L1.3a 标题层级 | `sess-20260401125108-968bfcee60034eeea51d3f26c88e13be` | 26 | success |
| L1.3b 文本强调 | `sess-20260401125752-2084bb520b69469ba54caa6c6d790ede` | 13 | model_failure |
| L1.3c 列表渲染 | `sess-20260401130136-eef167afe7234e5db90e90ab19183b36` | 4 | success |
| L1.5 复制按钮 | `sess-20260401130244-35e5a54178664f998ec1579f51f9e4ee` | 18 | unmatched |

### L2 层（交互体验）— 6/7 完成（跳 L2.1）

| Case | Session ID | 步数 | Evaluation | Bug |
|------|-----------|------|------------|-----|
| L2.2 主题切换 | `sess-20260401130829-ed473824a98f45a78e13b40d4f038bc5` | 12 | unmatched | B3 |
| L2.3 字号调节 | `sess-20260401131226-024d3ff946df44e58bf6b542c00b22d8` | 3 | success | — |
| L2.4 脚注转换 | `sess-20260401131331-0ebdbe7054a4495eb0ae110c1937d28c` | 4 | unmatched | B1 |
| L2.5 表格渲染 | `sess-20260401132511-47ae6a2db0d541d1abe91bde9db8b23b` | 6 | unmatched | B2 |
| L2.6 引用块样式 | `sess-20260401133753-d1cd8271629d4c3fb07616b726fc057d` | 9 | success | — |
| L2.7 自定义主色 | `sess-20260401134002-sharp-ridge` | 9 | success | — |

### L3 层（高级场景）— 5/5 完成

| Case | Session ID | 步数 | Evaluation |
|------|-----------|------|------------|
| L3.1 长文档性能 | `sess-20260401134242-39bd21e3aa08404083f63610a2001208` | 9 | unmatched |
| L3.2 特殊字符 | `sess-20260401134504-622115188f4d4d679acba31b39901a84` | 5 | success |
| L3.3 空文件处理 | `sess-20260401134647-450087bc25294f8e8e45edcfb22b74d8` | 5 | success |
| L3.4 响应式布局 | `sess-20260401134829-905a244019744e71b16dd03191ec06cc` | 12 | success |
| L3.5 连续主题切换 | `sess-20260401135146-e4e52f9c46a84cdaa1dba9b28c95cfb7` | 13 | unmatched |

## 备注

- 所有 session 截图数据已上传 mano-cua 云端
- L2.1 拖拽上传、L1.4 代码高亮与 Golden 采集相同原因跳过
- B3（主题切换不刷新预览）导致 L3.5（连续主题切换）也表现异常，属于同一 Bug 的不同表现
