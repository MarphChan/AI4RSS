# Implementation Plan (Task List)

## Phase 1: Project Setup & Core Configuration
- [ ] 1.1 **Initialize Project:** Create directory structure (`app.py`, `pages/`, `core/`, `data/`, `specs/`).
- [ ] 1.2 **Dependency Management:** Create `requirements.txt` with versions from `TECH_STACK.md`.
- [ ] 1.3 **Config Manager:** Implement `core/config_manager.py` to handle reading/writing `config.yaml` safely.
- [ ] 1.4 **Data Source Manager:** Implement `core/source_manager.py` to handle CRUD operations on `sources.json`.

## Phase 2: User Interface Foundation (Streamlit)
- [ ] 2.1 **Main App Skeleton:** Create `app.py` with sidebar navigation and page routing logic.
- [ ] 2.2 **Settings Page:** Implement `pages/1_Settings.py` with forms for API keys, schedule, and webhook URL. Connect to `Config Manager`.
- [ ] 2.3 **Source Manager Page:** Implement `pages/2_Sources.py` with `st.data_editor` to add/edit/delete sources. Connect to `Source Manager`.
- [ ] 2.4 **UI Polish:** Apply styles from `FRONTEND_GUIDELINES.md` (titles, icons, layout).
- [ ] 2.X **Localized Navigation:** Sidebar navigation labels follow selected language (中文/English).
- [ ] 2.5 **Batch Import Feature:** Implement batch RSS import in `pages/2_Sources.py` using LLM for parsing.
- [ ] 2.6 **Batch Actions in One List:** Support multi-select delete/test within the main sources table in `pages/2_Sources.py`.
- [ ] 2.7 **Stable Editing Experience:** Ensure type edits persist reliably and avoid unnecessary list position resets during repeated edits.

## Phase 3: Core Logic - The "Engine"
- [ ] 3.1 **Fetcher Module:** Implement `core/fetcher.py`.
    - [ ] RSS Parser: Use `feedparser` or `requests` + `xml` to extract items.
    - [ ] Web Scraper: Use `BeautifulSoup` to extract main content from HTML.
    - [ ] Filter Logic: Filter based on configured time period.
- [ ] 3.2 **LLM Engine:** Implement `core/llm.py`.
    - [ ] OpenAI Client Wrapper: Setup client with API key from config.
    - [ ] Summarization Prompt: Implement the specific prompt from PRD.
    - [ ] Mock Mode: Allow testing without burning tokens.
- [ ] 3.3 **Image Generator (Optional):** Implement `core/image_gen.py` (DALL-E 3 wrapper).

## Phase 4: The Workspace & Daily Workflow
- [ ] 4.1 **News Generation Logic:** Create a function `generate_daily_news()` that orchestrates fetching -> filtering -> summarization -> markdown generation.
- [ ] 4.2 **Workspace UI (Guided Steps):** Refactor `pages/3_Workspace.py` into a step-based flow.
    - [ ] 提供 Workspace 顶部 Tab：自动化信息收集与发布 / 手动信息收集和发布。
    - [ ] Step 1.1 数据源设置与管理：仅支持按 Type 筛选（默认 tech、记住上次选择），启用/禁用与触发生成。
    - [ ] Step 1.2 阅读清单：生成条目 + 外部链接；checkbox 标记已读/未读；支持多选删除条目并持久化。
    - [ ] Step 1.3 新闻预览与查看：版本选择、编辑与预览、主题筛选生成新版本。
    - [ ] Step 1.3 新闻预览与查看：支持基于 Step 1.2 阅读清单生成预览版本（默认未读）。
    - [ ] Step 1.4 发布通知设置和格式设置：Webhook 配置/测试、格式转换与推送。
39→    - [ ] 手动信息收集和发布：支持 Webhook 配置与缓存、手动添加 URL 列表、AI 解析生成结构化条目、支持编辑、格式转换与推送。
- [ ] 4.3 **Data Persistence:** Ensure generated markdown is saved to `data/YYYY-MM-DD-vX.0.md` with Front Matter (handle version incrementing).
- [ ] 4.4 **Push Logic:** Implement `core/pusher.py` to send the final markdown content to WeCom Webhook.
- [ ] 4.5 **Smart Format Adjustment:** Implement format selection and LLM parsing in `pages/3_Workspace.py`.
- [ ] 4.6 **Reading List (Unread/Read):** Add a persistent reading list with drag-and-drop between Unread/Read in `pages/3_Workspace.py`.
- [ ] 4.7 **Feishu URL Ingestion (Optional):** Add a lightweight local receiver to accept Feishu-forwarded URLs and append to Reading List.

## Phase 5: Automation & Polish
- [ ] 5.1 **Scheduler Implementation:** Create `core/scheduler.py` running in a daemon thread.
    - [ ] Check time every minute.
    - [ ] Trigger `generate_daily_news()` at configured time.
- [ ] 5.2 **Integration Testing:** Run full flow: Add Source -> Configure Settings -> Generate -> Edit -> Push.
- [ ] 5.3 **Documentation:** Update `README.md` with usage instructions.
