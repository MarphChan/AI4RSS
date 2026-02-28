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
- [ ] 2.5 **Batch Import Feature:** Implement batch RSS import in `pages/2_Sources.py` using LLM for parsing.
- [ ] 2.6 **Batch Delete Feature:** Allow selecting multiple sources for deletion in `pages/2_Sources.py`.

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
- [ ] 4.2 **Workspace UI:** Implement `pages/3_Workspace.py`.
    - [ ] Display status of last run.
    - [ ] "Start Generation" button triggers the logic.
    - [ ] Split view editor: `st.text_area` (left) + `st.markdown` (right).
- [ ] 4.3 **Data Persistence:** Ensure generated markdown is saved to `data/YYYY-MM-DD-vX.0.md` with Front Matter (handle version incrementing).
- [ ] 4.4 **Push Logic:** Implement `core/pusher.py` to send the final markdown content to WeCom Webhook.
- [ ] 4.5 **Smart Format Adjustment:** Implement format selection and LLM parsing in `pages/3_Workspace.py`.

## Phase 5: Automation & Polish
- [ ] 5.1 **Scheduler Implementation:** Create `core/scheduler.py` running in a daemon thread.
    - [ ] Check time every minute.
    - [ ] Trigger `generate_daily_news()` at configured time.
- [ ] 5.2 **Integration Testing:** Run full flow: Add Source -> Configure Settings -> Generate -> Edit -> Push.
- [ ] 5.3 **Documentation:** Update `README.md` with usage instructions.
