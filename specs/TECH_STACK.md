# Tech Stack & Dependencies

## 1. Core Language & Environment
- **Python:** `3.10+` (Required for modern type hinting and library support)
- **Virtual Environment:** `venv` (Standard library)

## 2. Web Framework (Frontend)
- **Streamlit:** `1.32.0`
  - *Rationale:* Zero HTML/CSS/JS, rapid prototyping, built-in session state management, easy data visualization.
  - *Key Components:* `st.sidebar`, `st.columns`, `st.expander`, `st.form`, `st.code`.
- **streamlit-sortables:** (Community component)
  - *Usage:* Drag-and-drop sorting and moving items between Unread/Read containers in Workspace.

## 3. Backend Logic & API
- **OpenAI (Python SDK):** `1.13.3`
  - *Usage:* Interact with OpenAI, DashScope (via OpenAI-compatible API), or other LLMs.
- **Requests:** `2.31.0`
  - *Usage:* HTTP requests for fetching RSS feeds, web pages, and sending webhooks.
- **BeautifulSoup4:** `4.12.3`
  - *Usage:* Parsing HTML content from non-RSS sources.
- **lxml:** `5.1.0`
  - *Usage:* Faster XML/HTML parser backend for BeautifulSoup.
- **Schedule:** `1.2.1`
  - *Usage:* Simple job scheduling for periodic tasks (fetch/push).

## 4. Data Handling & Persistence
- **PyYAML:** `6.0.1`
  - *Usage:* Reading/writing `config.yaml` and Front Matter in Markdown files.
- **Pandas:** `2.2.1`
  - *Usage:* Handling tabular data for the `Source Manager` (e.g., displaying sources in a dataframe).
- **python-frontmatter:** `1.1.0`
  - *Usage:* Parsing and updating metadata in Markdown files (crucial for `data/YYYY-MM-DD-vX.0.md`).

## 5. Development Tools
- **Black:** `24.2.0` (Code formatter)
- **Flake8:** `7.0.0` (Linter)
- **Watchdog:** `4.0.0` (File system monitoring, useful for auto-reloading if needed outside Streamlit's watcher).

## 6. Installation Command
```bash
pip install streamlit==1.32.0 openai==1.13.3 requests==2.31.0 beautifulsoup4==4.12.3 lxml==5.1.0 schedule==1.2.1 pyyaml==6.0.1 pandas==2.2.1 python-frontmatter==1.1.0 black==24.2.0 flake8==7.0.0 watchdog==4.0.0
```
