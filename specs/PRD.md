# Product Requirements Document (PRD)
# 产品需求文档 (PRD)

## 1. Project Overview
## 1. 项目概览
**Product Name:** AI Daily News Assistant (Local MVP)
**产品名称：** AI 每日新闻助手 (本地 MVP)
**Type:** Desktop Web Application (Localhost)
**类型：** 桌面 Web 应用程序 (本地运行)
**Core Value:** A zero-code AI news aggregation tool. Users manage API keys, data sources, and scheduled tasks via a visual interface to complete the "Configure -> Fetch -> Edit -> Push" workflow locally.
**核心价值：** 一个零代码 AI 新闻聚合工具。用户通过可视化界面管理 API 密钥、数据源和定时任务，在本地完成“配置 -> 获取 -> 编辑 -> 推送”的工作流。

## 2. Goals & Success Metrics
## 2. 目标与成功指标
### Goals
### 目标
- Enable users to aggregate news from RSS and web sources without writing code.
- 允许用户无需编写代码即可聚合来自 RSS 和 Web 来源的新闻。
- Provide a seamless workflow to review and edit AI-generated summaries before pushing.
- 提供无缝的工作流，以便在推送之前审查和编辑 AI 生成的摘要。
- Ensure data privacy by keeping all configurations and history local.
- 通过将所有配置和历史记录保存在本地来确保数据隐私。

### Success Metrics
### 成功指标
- User can successfully configure API keys and sources via UI.
- 用户可以通过 UI 成功配置 API 密钥和来源。
- Application successfully fetches, filters (last 24h), and summarizes news.
- 应用程序成功获取、过滤（过去 24 小时）并总结新闻。
- Generated markdown is editable and pushable to Enterprise WeChat via Webhook.
- 生成的 Markdown 可编辑并通过 Webhook 推送到企业微信。
- Scheduled tasks run reliably in the background when the app is open.
- 当应用程序打开时，定时任务在后台可靠运行。

## 3. Scope
## 3. 范围
### In Scope
### 包含范围
- **User Interface:** Streamlit-based web interface (Settings, Source Manager, Workspace).
- **用户界面：** 基于 Streamlit 的 Web 界面（设置、源管理器、工作区）。
- **Core Logic:** Python backend for scheduling, API requests, and data parsing.
- **核心逻辑：** 用于调度、API 请求和数据解析的 Python 后端。
- **Data Persistence:** Local file system (`config.yaml`, `sources.json`, `history/*.md`).
- **数据持久化：** 本地文件系统 (`config.yaml`, `sources.json`, `history/*.md`)。
- **AI Integration:** LLM for summarization (OpenAI/DashScope/VolcEngine) and Image Generation (DALL-E 3/Wanx).
- **AI 集成：** 用于摘要的 LLM (OpenAI/DashScope/火山引擎) 和图像生成 (DALL-E 3/Wanx)。
- **Notifications:** Enterprise WeChat Webhook.
- **通知：** 企业微信 Webhook。

### Out of Scope
### 不在范围内
- Multi-user authentication or cloud database storage (Phase 2).
- 多用户身份验证或云数据库存储（第二阶段）。
- Complex dynamic web scraping (Selenium/Playwright) - strictly static HTML parsing for MVP.
- 复杂的动态网页抓取 (Selenium/Playwright) - MVP 仅限静态 HTML 解析。
- Mobile app version.
- 移动应用版本。
- Real-time streaming updates (daily batch processing only).
- 实时流更新（仅每日批处理）。

## 4. Functional Requirements
## 4. 功能需求

### 4.1 System Settings (Page 1)
### 4.1 系统设置 (页面 1)
- **LLM Configuration:** Select provider, input API Key, select model.
- **LLM 配置：** 选择提供商，输入 API 密钥，选择模型。
- **Image Generation:** Toggle on/off, provider selection.
- **图像生成：** 开启/关闭切换，选择提供商。
- **Schedule:** Set fetch time and push time.
- **时间表：** 设置获取时间和推送时间。
- **Time Period:** Select fetch time period (24h, 3 days, 7 days, or Custom).
- **时间段：** 选择获取时间段（24小时、3天、7天或自定义）。
- **Max Items:** Limit the number of news items to process (1-30).
- **最大条数：** 限制处理的新闻条数 (1-30)。
- **Notification:** Configure Webhook URL and test connectivity.
- **通知：** 配置 Webhook URL 并测试连接性。
- **Action:** Save configuration to `config.yaml`.
- **操作：** 保存配置到 `config.yaml`。

### 4.2 Source Management (Page 2)
### 4.2 来源管理 (页面 2)
- **Source List:** View all sources with status (Enabled/Disabled), group, and last fetch time.
- **来源列表：** 查看所有来源及其状态（启用/禁用）、分组和上次获取时间。
- **Add Source:** Input Name, Type (RSS/Web/Social), URL, Group (default: "Default").
- **添加来源：** 输入名称、类型 (RSS/Web/社交媒体)、URL、分组 (默认："Default")。
- **Batch Import:** 
- **批量导入：**
  - Input: Text area to paste multiple RSS URLs or unstructured text containing them.
  - 输入：文本区域，用于粘贴多个 RSS URL 或包含它们的非结构化文本。
  - Process: Use LLM to identify and extract valid RSS links and propose names.
  - 处理：使用 LLM 识别并提取有效的 RSS 链接并建议名称。
  - Action: Preview parsed results -> Select/Deselect -> Assign Group -> Import to system.
  - 操作：预览解析结果 -> 选择/取消选择 -> 分配分组 -> 导入系统。
- **Edit/Delete:** 
- **编辑/删除：**
  - Modify existing sources including group assignment.
  - 修改现有来源，包括分组分配。
  - Batch Delete: Select multiple sources to delete at once.
  - 批量删除：选择多个来源一次性删除。
- **Test Fetch:** Immediate trigger for a single source to validate selector/RSS.
- **测试获取：** 立即触发单个来源以验证选择器/RSS。

### 4.3 Workspace (Page 3 - Guided Steps)
### 4.3 工作区 (页面 3 - 分步引导)
Workspace 重构为 4 个“子页面/步骤”，步骤间有依赖关系：下一步仅使用并复用上一步的选择与结果，形成更明确的「配置 → 阅读 → 预览 → 发布」链路。

- **Step 1.1 数据源设置与管理**
  - 仅支持“数据源类型（Type）”筛选（不支持在此处新增/删除数据源；数据源维护仍在 Sources 页面）。
  - 默认选择类型为【tech】，并缓存上次选择的类型（本地持久化）。
  - 快速查看/启用/禁用数据源，在当前类型范围内触发生成（Start Generation）。
- **Step 1.2 阅读清单**
  - 阅读清单由两部分组成：数据源生成的条目 + 用户手动/外部转发的链接。
  - 每条阅读项前提供 checkbox，用于标记是否已阅读（勾选即进入已读）。
  - 支持多选删除阅读清单条目（对未读/已读均生效），删除后从本地持久化中移除。
- **Step 1.3 新闻预览与查看**
  - 版本选择（vX.0）与状态展示。
  - Markdown 内容编辑 + 预览。
  - 主题筛选生成新版本（Top N）。
- **Step 1.4 发布通知设置和格式设置**
  - 配置并测试 Webhook。
  - 选择推送格式：Markdown / 图文 news / markdown_v2。
  - 智能格式解析、预览解析结果、确认推送。

### 4.4 Background Logic
### 4.4 后台逻辑
- **Scheduler:** Thread-based scheduler running `schedule` library.
- **调度器：** 基于线程的调度器，运行 `schedule` 库。
- **Fetcher:** Concurrent execution of data fetching.
- **获取器：** 并发执行数据获取。
- **Filter:** Filter articles based on configured time period (default 24h).
- **过滤器：** 根据配置的时间段（默认 24 小时）过滤文章。
- **Feishu URL Ingestion (Optional):** Receive Feishu-forwarded reading URLs and add them to Reading List as Unread.
- **飞书链接接入（可选）：** 接收从飞书转发过来的阅读链接，并写入阅读清单的【未读】。

## 5. Data Structures
## 5. 数据结构

### 5.1 Global Config (`config.yaml`)
### 5.1 全局配置 (`config.yaml`)
```yaml
system:
  cron_schedule: "0 8 * * *"  # Auto-fetch time (自动获取时间)
  push_time: "09:30"          # Auto-push time (自动推送时间)
  timezone: "Asia/Shanghai"
  time_period: 24             # Fetch time period in hours (获取时间段，以小时为单位)
  max_items: 20               # Max items to process (最大处理条数)

llm:
  provider: "dashscope"       # Options: dashscope, volcengine, openai (选项：dashscope, volcengine, openai)
  api_key: "sk-xxxxxxxxxxxx"  # Encrypted/Masked in UI (在 UI 中加密/脱敏)
  model_name: "qwen-max"      # e.g., qwen-plus, doubao-pro-32k

image:
  enable_generation: true
  provider: "wanx"            # wanx / dall-e-3

notification:
  webhook_url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."

feishu:
  receiver_enabled: false
  receiver_host: "127.0.0.1"
  receiver_port: 8765
  receiver_token: ""
```

### 5.2 Data Sources (`sources.json`)
### 5.2 数据源 (`sources.json`)
```json
[
  {
    "id": "src_001",
    "name": "OpenAI Blog",
    "type": "rss",
    "url": "https://openai.com/blog/rss.xml",
    "enabled": true,
    "last_crawl_time": "2023-10-27 08:00:00"
  },
  {
    "id": "src_002",
    "name": "Sam Altman X",
    "type": "web_crawl",
    "url": "https://twitter.com/sama",
    "enabled": true,
    "headers": { "User-Agent": "Mozilla/5.0..." }
  }
]
```

### 5.3 Daily News File (`data/YYYY-MM-DD-vX.0.md`)
### 5.3 每日新闻文件 (`data/YYYY-MM-DD-vX.0.md`)
Support creating multiple files per day with versioning (e.g., `2023-10-27-v1.0.md`, `2023-10-27-v2.0.md`).
支持每天创建多个文件并进行版本控制（例如 `2023-10-27-v1.0.md`, `2023-10-27-v2.0.md`）。

Uses Front Matter for metadata and Markdown for content.
使用 Front Matter 存储元数据，使用 Markdown 存储内容。

```markdown
---
date: "2023-10-27"
version: "v1.0"
status: "pending_review"  # pending_review / published (待审核 / 已发布)
push_time: "09:30"
articles_meta:
  - id: "art_001"
    source_id: "src_001"
    original_url: "https://openai.com/blog/gpt-4-turbo"
    ai_image_prompt: "Futuristic robot reading news, flat style"
    use_ai_image: false
---

# 📅 2023-10-27 AI Daily News

## 1. OpenAI Releases GPT-4 Turbo
!https://openai.com/assets/cover.jpg
> **Summary**: Context window expanded to 128k, knowledge base updated to April 2023, development costs reduced by 3x.
> *Source: https://openai.com/blog/gpt-4-turbo*
```

### 5.4 Reading List (`history/reading_list.json`)
### 5.4 阅读清单 (`history/reading_list.json`)
Reading list is stored locally as a JSON file to persist Unread/Read state across days and support external URLs not present in the generated daily file.
阅读清单以本地 JSON 文件方式存储，用于跨天保留未读/已读状态，并支持不在当天生成结果中的外部阅读链接。

## 6. Prompt Engineering Strategy
## 6. 提示工程策略
- **Summarization:** Strict JSON output, Chinese language, <30 words.
- **摘要：** 严格的 JSON 输出，中文语言，<30 字。
- **Discovery:** Extract links from HTML published in last 24h.
- **发现：** 从过去 24 小时发布的 HTML 中提取链接。
- **Image Gen:** Minimalist, flat style, tech theme.
- **图像生成：** 极简主义，扁平风格，科技主题。
