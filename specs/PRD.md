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

### 4.3 Workspace (Page 3 - Core)
### 4.3 工作区 (页面 3 - 核心)
- **Source Selection:** 
- **来源选择：**
  - Filter sources by Group (e.g., "Tech", "Finance", or "All").
  - 按分组筛选来源（例如，“科技”、“金融”或“全部”）。
  - View list of sources in the selected groups.
  - 查看选定分组中的来源列表。
- **Manual Trigger:** "Start Generation" button.
- **手动触发：** “开始生成”按钮。
- **Editor:** Two-column layout. Left: Markdown editor. Right: Live preview.
- **编辑器：** 双列布局。左侧：Markdown 编辑器。右侧：实时预览。
- **Regenerate Image:** AI re-drawing for specific news items.
- **重新生成图像：** AI 为特定新闻条目重新绘图。
- **Smart Format Adjustment:** 
- **智能格式调整：**
  - Select push format: "Markdown" or "News (Graph-Text)".
  - 选择推送格式：“Markdown”或“新闻（图文）”。
  - Button: "Smart Parse Format".
  - 按钮：“智能解析格式”。
  - Preview: Preview the parsed content before pushing.
  - 预览：推送前预览解析后的内容。
- **Topic Filter:**
  - Input: Topic of interest (e.g., Tech, Finance).
  - 输入：感兴趣的主题（例如：科技、金融）。
  - Input: Max Items (e.g., 5).
  - 输入：最大条数（例如：5）。
  - Button: "Generate Filtered Version".
  - 按钮：“生成筛选版本”。
  - Action: Generate a new version (e.g., v1.1) containing only relevant articles (top N).
  - 操作：生成一个仅包含相关文章（Top N）的新版本（例如 v1.1）。
- **Push:** "Confirm & Push" button to send final content to Webhook.
- **推送：** “确认并推送”按钮，将最终内容发送到 Webhook。

### 4.4 Background Logic
### 4.4 后台逻辑
- **Scheduler:** Thread-based scheduler running `schedule` library.
- **调度器：** 基于线程的调度器，运行 `schedule` 库。
- **Fetcher:** Concurrent execution of data fetching.
- **获取器：** 并发执行数据获取。
- **Filter:** Filter articles based on configured time period (default 24h).
- **过滤器：** 根据配置的时间段（默认 24 小时）过滤文章。

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

## 6. Prompt Engineering Strategy
## 6. 提示工程策略
- **Summarization:** Strict JSON output, Chinese language, <30 words.
- **摘要：** 严格的 JSON 输出，中文语言，<30 字。
- **Discovery:** Extract links from HTML published in last 24h.
- **发现：** 从过去 24 小时发布的 HTML 中提取链接。
- **Image Gen:** Minimalist, flat style, tech theme.
- **图像生成：** 极简主义，扁平风格，科技主题。
