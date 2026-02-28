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
