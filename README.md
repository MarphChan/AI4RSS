# AI_RSS (AI Daily News Assistant)
# AI_RSS - AI 日报助手 (本地 MVP 版)

A zero-code AI news aggregation tool that helps you configure, fetch, summarize, and push daily news to Enterprise WeChat.
一个零代码 AI 新闻聚合工具，帮助您配置、获取、总结并将每日新闻推送到企业微信。

## Features
## 功能特性

- **Visual Configuration**: Manage API keys, schedules, and webhooks via a friendly UI.
  - **可视化配置**: 通过友好的用户界面管理 API 密钥、计划任务和 Webhook。
- **Multi-Source Support**: Subscribe to RSS feeds or crawl websites.
  - **多源支持**: 订阅 RSS 源或抓取网站。
- **AI-Powered**: Uses LLMs (OpenAI, DashScope, etc.) to summarize news into 30-word Chinese snippets.
  - **AI 驱动**: 使用 LLM（OpenAI、DashScope 等）将新闻总结为 30 字的中文摘要。
- **Daily Workflow**: Fetch -> Summarize -> Edit (Markdown) -> Push.
  - **每日工作流**: 获取 -> 总结 -> 编辑 (Markdown) -> 推送。
- **Automated Schedule**: Runs in the background to fetch and push news at set times.
  - **自动计划**: 在后台运行，按设定时间获取并推送新闻。

## Installation
## 安装指南

1. **Clone the repository**:
   **克隆仓库**:
   ```bash
   git clone https://github.com/MarphChan/AI4RSS.git
   cd ai-daily-news-assistant
   ```

2. **Install dependencies**:
   **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   **运行应用**:
   ```bash
   streamlit run app.py
   ```
   **或通过这种方式运行应用**:
   ```bash
   python3 -m streamlit run app.py
   ```

## Usage Guide
## 使用指南

### 1. Initial Setup (Settings)
### 1. 初始设置 (设置页面)
- Navigate to the **Settings** page.
  - 前往 **Settings (设置)** 页面。
- Select your LLM Provider (e.g., DashScope) and enter your API Key.
  - 选择您的 LLM 提供商（例如 DashScope）并输入您的 API 密钥。
- Set the **Auto Fetch Time** (e.g., 08:00) and **Auto Push Time** (e.g., 09:30).
  - 设置 **Auto Fetch Time (自动获取时间)**（例如 08:00）和 **Auto Push Time (自动推送时间)**（例如 09:30）。
- Configure your **Enterprise WeChat Webhook** URL.
  - 配置您的 **Enterprise WeChat Webhook (企业微信 Webhook)** URL。
- Click **Save Configuration**.
  - 点击 **Save Configuration (保存配置)**。

### 2. Manage Sources
### 2. 管理数据源
- Go to the **Source Manager** page.
  - 前往 **Source Manager (数据源管理)** 页面。
- Add new RSS feeds or website URLs.
  - 添加新的 RSS 源或网站 URL。
- Toggle sources on/off as needed.
  - 根据需要开启/关闭数据源。

### 3. Generate & Push
### 3. 生成与推送
- Go to the **Workspace** page.
  - 前往 **Workspace (工作区)** 页面。
- Click **Start Generation** to fetch and summarize news manually.
  - 点击 **Start Generation (开始生成)** 手动获取并总结新闻。
- Review the generated Markdown content in the editor.
  - 在编辑器中预览生成的 Markdown 内容。
- Click **Confirm & Push** to send the daily news to your team.
  - 点击 **Confirm & Push (确认并推送)** 将每日新闻发送给您的团队。

## Project Structure
## 项目结构

- `app.py`: Main entry point.
  - `app.py`: 主入口文件。
- `pages/`: Streamlit pages (Settings, Sources, Workspace).
  - `pages/`: Streamlit 页面（设置、数据源、工作区）。
- `core/`: Backend logic (Fetcher, LLM, Generator, Scheduler).
  - `core/`: 后端逻辑（获取器、LLM、生成器、调度器）。
- `history/`: Stored daily news markdown files.
  - `history/`: 存储的每日新闻 Markdown 文件。
- `config.yaml`: Local configuration file (auto-generated).
  - `config.yaml`: 本地配置文件（自动生成）。
- `sources.json`: Data sources list (auto-generated).
  - `sources.json`: 数据源列表（自动生成）。

## License
MIT License

