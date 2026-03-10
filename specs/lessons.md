# 经验教训记录

## 2026-03-10 Streamlit 重复 Key 导致组件冲突

### 问题现象
在 Streamlit 应用的 "1.2 阅读清单" 页面点击 "删除选中" 按钮时报错：`DuplicateWidgetID: There are multiple identical st.button widgets with the same generated key.`。

### 根本原因
代码中存在两个 `st.button("删除选中")`，分别位于 `_render_step_reading_list`（阅读清单页）和 `_render_manual_tab`（手动收集页）。
虽然这两个函数在逻辑上属于不同的 "步骤" 或 "Tab"，但 Streamlit 的运行机制是每次交互重新运行整个脚本。当用户处于特定步骤（如 1.2）时，`_render_step_reading_list` 被调用，同时 `_render_manual_tab` 也被调用（因为它在另一个 Tab 中，而 Streamlit 会渲染所有 Tab 的内容）。
由于两个按钮的 label 相同且未指定 `key` 参数，Streamlit 无法区分它们，从而抛出 DuplicateWidgetID 错误。

### 解决思路
为所有可能共存的同名组件显式指定唯一的 `key` 参数。

### 实施步骤
1. 修改 `pages/3_Workspace.py`。
2. 为阅读清单页的删除按钮添加 `key="reading_list_delete_btn"`。
3. 为手动收集页的删除按钮添加 `key="manual_list_delete_btn"`。

## 2026-03-10 修改数据源时报错（NumPy 类型序列化）

### 问题现象
在 Streamlit 应用的 "数据源管理" 页面修改数据源配置（如启用/禁用）并保存时，报错 `TypeError: Object of type bool_ is not JSON serializable`。

### 根本原因
Streamlit 的 `data_editor` 组件返回的数据使用了 Pandas DataFrame。当从 DataFrame 中提取单个值（如布尔值）时，Pandas 可能会返回 NumPy 类型（如 `numpy.bool_`）而非 Python 原生类型（`bool`）。
Python 标准库的 `json.dump` 默认不支持 NumPy 类型的序列化，导致在保存 `sources.json` 时抛出异常。

### 解决思路
在将数据保存到 JSON 文件之前，或者在更新内存中的数据源对象时，显式地将 NumPy 类型转换为 Python 原生类型。
利用 NumPy 标量的 `.item()` 方法可以方便地将其转换为对应的 Python 标量。

### 实施步骤
1. 修改 `core/source_manager.py`。
2. 添加 `_sanitize_value` 辅助方法，检查值是否具有 `.item` 属性（NumPy 类型的特征），如果有则调用它进行转换。
3. 在 `update_source` 和 `update_sources_bulk` 方法中，使用 `_sanitize_value` 清洗传入的 `updates` 字典。

## 2026-03-06 获取数据源报错（NaN 处理）

### 问题现象
用户在“获取数据源”或管理数据源时遇到报错。根本原因是 `sources.json` 文件中包含 `NaN` 值（例如 `"logo": NaN`）。Streamlit 前端或 Pandas 在处理这些 `NaN` 值时可能引发异常。

### 根本原因
1. Python 的 `json` 模块默认允许序列化 `NaN` 为 `NaN`，但这在标准 JSON 中是非法的。
2. Pandas 处理缺失数据时会使用 `NaN`。如果直接将 DataFrame 转换为 dict 并保存为 JSON，就会引入 `NaN`。
3. Streamlit 的 `data_editor` 在处理含有 `NaN` 的列（尤其是被强制指定为 `TextColumn` 时）可能会出现类型冲突或渲染错误。

### 解决思路
1. 在 `core/source_manager.py` 的 `_load_sources` 中，加载数据后立即清洗，将所有的 `NaN` 替换为 `""` 或 `None`。
2. 在 `update_sources_bulk` 中，在更新源数据之前，先清洗 `updates` 字典中的 `NaN` 值。
3. 确保 `sources.json` 始终包含合法的 JSON 数据。

### 实施步骤
1. 修改 `core/source_manager.py`，引入 `math` 模块，添加 `NaN` 检测和替换逻辑。
2. 编写测试脚本 `tests/reproduce_fetch_error.py` 验证修复效果，并清理现有的 `sources.json` 文件。

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

## 2026-03-06 LLM 配置不生效与 Base URL 覆盖问题

### 问题现象
用户在设置页面配置了 Base URL、API Key 和模型（Provider 选为 OpenAI），但 AI 相关功能（如摘要、RSS 解析）仍然无法工作。

### 根本原因
1. **Base URL 被忽略**：`core/llm_base.py` 中对于 `openai` provider 硬编码了 `https://api.openai.com/v1`，导致用户在设置页面配置的 Custom Base URL 被忽略。用户虽然意图使用兼容 OpenAI 协议的其他服务（如 Dashscope），但选了 `openai` provider 后 Base URL 配置无效。
2. **配置未实时生效**：`LLMEngine` 在模块导入时初始化，且作为全局单例存在。当用户在设置页面更新配置并保存后，`core/config_manager.py` 虽然更新了文件和内存中的配置，但 `LLMEngine` 实例并未重新加载配置，导致其仍持有旧的（或空的）凭证，直到应用重启。

### 解决思路
1. **允许 OpenAI Provider 覆盖 Base URL**：修改 `core/llm_base.py`，在 `provider == "openai"` 时，如果用户配置了 `base_url`，则优先使用用户配置的 URL。
2. **实现热重载机制**：在 `LLMBase` 中添加 `reload()` 方法，用于重新读取配置并初始化客户端。在设置页面保存配置后，显式调用 `llm_engine.reload()`，确保更改立即生效。

### 实施步骤
1. 修改 `core/llm_base.py`，添加 `reload` 方法，并优化 Base URL 选择逻辑。
2. 修改 `pages/1_Settings.py`，在保存配置后调用 `llm_engine.reload()`。

## 2026-03-10 定时任务未执行

### 问题现象
定时发布的任务（如每日新闻生成和推送）没有成功执行，尽管服务是在线的。

### 根本原因
调度器逻辑存在缺陷。`SchedulerService` 每分钟检查一次配置变更（`_run_loop` 中的 `time.time() - last_config_check > 60`），每次检查都会调用 `_refresh_schedule`。
在原实现中，`_refresh_schedule` 会无条件调用 `schedule.clear()` 清空所有任务，然后重新添加任务。
如果 `_refresh_schedule` 的执行时间恰好与任务的计划执行时间（如 08:00:00）重合或极其接近，`schedule` 库可能会在任务执行前将其清除并重新添加。重新添加的任务会被 `schedule` 库视为“今天已过，安排在明天”，导致当天的任务被跳过。

### 解决思路
仅在配置（`fetch_time` 或 `push_time`）实际发生变化时才刷新调度表。如果配置未变，保持现有的调度任务不变，避免不必要的 `schedule.clear()`。

### 实施步骤
1. 修改 `core/scheduler.py`，在 `SchedulerService` 中增加 `_last_fetch_time`和 `_last_push_time` 成员变量。
2. 在 `_refresh_schedule` 中增加判断逻辑，只有当时间配置发生变化时才执行 `schedule.clear()` 和重新调度。

## 2026-03-10 阅读清单预览生成数量不足

### 问题现象
用户在 "1.2 阅读清单" 中添加了多条 URL，但在 "1.3 新闻预览" 点击生成预览时，生成的预览版本只包含部分条目（例如 5 条只生成了 2 条），且没有任何错误提示，界面显示 "Success"。

### 根本原因
1. **静默失败**：`core/generator.py` 中的 `generate_daily_news_from_urls` 在并发抓取 URL 时，如果某些 URL 抓取失败（如超时、404、反爬虫拦截），`fetcher` 会返回空列表或 `None`。
2. **逻辑缺陷**：生成器逻辑中只收集成功抓取并摘要的条目，完全忽略了失败的条目。
3. **缺乏反馈**：最终生成的 Markdown 内容仅包含成功条目，用户无法得知哪些条目被遗漏及其原因。

### 解决思路
1. **增强错误追踪**：在生成过程中记录所有请求的 URL 和实际成功的 URL。
2. **用户可见反馈**：计算差集（请求 URL -成功 URL），将失败的 URL 列表追加到生成的 Markdown 文档末尾，作为一个显式的 "⚠️ Failed to Fetch" 章节。
3. **保持流程连续**：部分失败不应阻断整个生成流程，确保用户至少能看到成功的部分。

### 实施步骤
1. 修改 `core/generator.py` 的 `generate_daily_news_from_urls` 方法。
2. 在收集完 `fetched_items` 后，计算 `failed_urls`。
3. 在构建 Markdown 内容时，如果存在 `failed_urls`，则在文末添加警告章节列出这些 URL。
