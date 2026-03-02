# 经验教训记录

## 2026-03-02 Claude Rate Limit 处理

### 问题背景
Claude API 有严格的 rate limit，高并发调用时容易触发 429 错误。

### 解决方案
在 `core/llm_base.py` 中实现统一的重试机制：
- 指数退避：`delay = base_delay * 2^attempt`
- 添加抖动：±10% 随机抖动避免 thundering herd
- 尊重 `retry-after` header
- 最多重试 3 次

### 配置示例
```yaml
llm:
  provider: anthropic
  model_name: claude-3-5-sonnet-20241022
```

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

## 2026-03-02 LLM 引擎架构不兼容导致草稿生成为空

### 问题现象
在工作区的「手动链接列表」中点击「AI解析生成草稿」，虽然提示成功，但生成的 Markdown 草稿没有内容（显示“该版本没有可编辑条目”）。

### 根本原因
LLM 引擎层架构重构引入了不兼容：
1. **属性缺失**：`LLMBase` 在重构后移除了 `self.client` 属性，改为 `self.openai_client` 和 `self.anthropic_client`。
2. **Mixins 未更新**：`ContentMixin`、`DiscoveryMixin` 和 `FormatMixin` 仍然直接访问 `self.client`，导致在执行 `summarize` 等操作时触发 `AttributeError`。
3. **错误处理链过长**：
   - `ContentMixin.summarize` 抛出 `AttributeError`。
   - `generator.py` 中的 `_process_single_item` 捕获该异常并返回 `None`。
   - `generate_daily_news_from_urls` 将 `None` 丢弃，最终 `processed_articles` 为空。
   - 文件虽然被创建，但 `articles_meta` 为空列表。

### 解决思路
1. **统一调用入口**：Mixins 不应直接操作 `self.client`，而应调用 `LLMBase` 提供的抽象方法 `generate_response`。
2. **恢复兼容性属性**（临时）：在 `LLMBase` 中恢复 `self.client` 属性作为别名，以防其他地方仍有直接引用。
3. **集成专用解析接口**：引入专门针对微信等复杂网页的解析服务（如 Jina Reader），通过在 URL 前添加前缀或使用专用 API 获取干净的 Markdown 内容。

### 实施步骤
1. 在 `LLMBase` 的 `_init_clients` 中，根据当前 provider 为 `self.client` 赋值。
2. 重构 `ContentMixin.summarize`、`DiscoveryMixin` 和 `FormatMixin`，使用 `self.generate_response` 代替直接调用 client。
3. 在 `config.yaml` 中添加 `parser` 配置，并更新 `fetcher.py`：
   - 识别 `mp.weixin.qq.com` 域名。
   - 自动路由至 Jina Reader (`r.jina.ai`) 进行内容提取，避开微信的防爬限制。

## 2026-03-02 左侧栏双图标与微信解析失败修复

### 问题现象
1. 左侧栏导航项显示两个重复的图标。
2. 解析微信公众号文章时报错 `No content fetched from provided URLs.`，或者提取不到正文/图片。

### 根本原因
1. **双图标问题**：在 `core/i18n.py` 的翻译字符串中已经包含了表情符号（如 `🏠 首页`），而在 `core/ui_nav.py` 调用 `st.sidebar.page_link` 时又传入了 `icon` 参数。Streamlit 会同时渲染这两个来源的图标。
2. **微信解析问题**：
   - 默认使用的 Jina Reader (`r.jina.ai`) 在处理微信文章时偶尔会超时或返回特定的错误提示文字。
   - 原逻辑未处理 Jina 的超时异常，且在 Jina 返回 200 状态码但内容为错误提示时，仍将其作为正文返回。
   - 微信文章图片通常使用 `data-src` 而非标准 `src` 属性，导致图片提取失败。

### 解决思路
1. **UI 优化**：规范化导航配置，将图标与文字分离。翻译文件仅保留纯文字，图标统一由 `page_link` 的 `icon` 参数控制。
2. **增强抓取鲁棒性**：
   - 为 Jina Reader 添加 `try-except` 捕获超时并检测返回内容是否包含错误关键字。
   - 增加失败回退机制：若 Jina 失败，回退到标准 `requests` 抓取。
   - 针对微信域名进行定制化解析，提取 `#js_content` 容器内容。
   - 扩展图片提取逻辑，支持 `data-src` 属性。

### 实施步骤
1. 修改 `core/i18n.py`，移除 `nav_home` 等键值中的表情符号。
2. 更新 `core/fetcher.py` 中的 `_fetch_web` 方法，增加 Jina 错误检测与回退逻辑。
3. 更新 `_extract_image_from_html`，支持 `img.get('data-src')`。

