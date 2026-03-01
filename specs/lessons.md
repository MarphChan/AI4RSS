# 经验教训记录

## 2026-02-28 OpenAI 客户端初始化报错

### 问题现象
应用启动或调用 LLM 时报错：
```
TypeError: __init__() got an unexpected keyword argument 'proxies'
```
Traceback 指向 `core/llm.py` 中 `OpenAI()` 的初始化调用，最终定位到 `openai/_base_client.py` 中 `httpx` 客户端的初始化。

### 根本原因
依赖库版本冲突。
- 项目使用的 `openai` 版本为 `1.13.3`。
- 环境中安装的 `httpx` 版本为 `0.28.1`。
- `httpx` 在 `0.28.0` 版本中进行了破坏性更新，移除了 `proxies` 参数（改用 `proxy` 或 `mounts`）。
- 旧版本的 `openai` 库在内部初始化 `httpx.Client` 时仍使用 `proxies` 参数，导致不兼容。

### 解决思路
需要确保 `openai` 和 `httpx` 版本兼容。
1. **方案一（采用）**：降级 `httpx` 版本。将 `httpx` 限制在 `0.28.0` 以下（如 `0.27.2`），以兼容当前的 `openai` 版本。
2. **方案二**：升级 `openai` 版本。升级到支持新版 `httpx` 的 `openai` 版本。考虑到代码稳定性，优先选择方案一。

### 实施步骤
1. 修改 `requirements.txt`，添加 `httpx<0.28.0`。
2. 重新安装依赖。

## 2026-03-01 阅读清单勾选已读导致跳回数据源管理

### 问题现象
在 Workspace 的「1.2 阅读清单」中勾选某条为“已读”，页面会跳回「1.1 数据源设置与管理」。

### 根本原因
Streamlit 的 `data_editor` 勾选会触发脚本 rerun；原实现中阅读清单更新后再次 `st.rerun()`，叠加编辑器 key 随版本变化，导致部分 widget state 发生重建，进而使步骤状态丢失并回落到初始化默认值（1.1）。

### 解决思路
减少不必要的状态重建，并在内部刷新前显式保持导航状态。
1. 使用稳定的 `data_editor` key，避免因 key 变化导致 widget state 重建。
2. 在阅读清单写回并触发 rerun 前，显式写回 `workspace_step="1.2 阅读清单"`，避免回落到默认步骤。

### 实施步骤
1. 将阅读清单 `data_editor` 的 key 改为固定值。
2. 在“加入未读”和“已读状态变更”触发 `st.rerun()` 前写回 `workspace_step`。

## 2026-03-01 数据源管理搜索结果未清空导致与预期不符

### 问题现象
在数据源管理的“批量导入/主题搜索”里多次搜索时，期望每次都清空上一次结果并展示本次新结果；实际行为与预期不一致，用户无法得到“仅当前搜索”的候选列表。

### 根本原因
候选列表使用 `st.session_state['batch_candidates']` 保存，但没有将“搜索结果的生命周期”设计清楚：搜索行为应该覆盖（清空+写入）还是累积（合并追加）。当实现与产品预期不一致时，就会表现为“结果未清空/结果被错误累积/刷新后看起来不对”。另外，候选表格的勾选状态如果不回写到 session_state，也会在 rerun 后丢失。

### 解决思路
明确交互语义：搜索是“覆盖当前结果集”。实现上每次搜索都应清空并覆盖 `batch_candidates`；同时把候选表格编辑结果回写到 session_state，保证在同一次结果集内勾选状态稳定。

### 实施步骤
1. 搜索完成后直接覆盖写入 `st.session_state['batch_candidates']`，无结果时删除该键以清空列表。
2. 每次渲染候选表格后，将编辑后的 candidates 回写到 `st.session_state['batch_candidates']`。
