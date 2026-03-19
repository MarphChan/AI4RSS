import streamlit as st

TRANSLATIONS = {
    # App.py
    "page_title": {
        "en": "AI Daily News Assistant",
        "zh": "AI 每日新闻助手"
    },
    "welcome_message": {
        "en": """
    ### Welcome to your AI News Assistant! 
    
    This tool helps you aggregate, summarize, and publish news automatically.
    
    **Get Started:**
    1. Go to **Settings** to configure your API keys and schedule.
    2. Go to **Sources** to add RSS feeds or websites.
    3. Go to **Workspace** to generate your daily report.
    """,
        "zh": """
    ### 欢迎使用 AI 新闻助手！
    
    此工具帮助您自动聚合、总结并发布新闻。
    
    **开始使用：**
    1. 前往 **设置** 配置 API 密钥和定时任务。
    2. 前往 **数据源** 添加 RSS 订阅或网站。
    3. 前往 **工作区** 生成每日报告。
    """
    },
    "navigation": {
        "en": "Navigation",
        "zh": "导航"
    },
    "nav_home": {
        "en": "Home",
        "zh": "首页"
    },
    "nav_settings": {
        "en": "Settings",
        "zh": "设置"
    },
    "nav_sources": {
        "en": "Sources",
        "zh": "数据源"
    },
    "nav_workspace": {
        "en": "Workspace",
        "zh": "工作区"
    },
    "system_ready": {
        "en": "System Ready",
        "zh": "系统就绪"
    },
    "config_not_found": {
        "en": "⚠️ Configuration not found. Please visit Settings page.",
        "zh": "⚠️ 未找到配置。请访问设置页面。"
    },
    # Settings Page
    "settings_page_title": {
        "en": "Settings",
        "zh": "设置"
    },
    "system_settings_title": {
        "en": "⚙️ System Settings",
        "zh": "⚙️ 系统设置"
    },
    "llm_config_header": {
        "en": "🤖 LLM Configuration",
        "zh": "🤖 LLM 配置"
    },
    "llm_provider_label": {
        "en": "LLM Provider",
        "zh": "LLM 提供商"
    },
    "model_name_label": {
        "en": "Model Name",
        "zh": "模型名称"
    },
    "api_key_label": {
        "en": "API Key",
        "zh": "API 密钥"
    },
    "enable_image_gen_label": {
        "en": "Enable AI Image Generation",
        "zh": "启用 AI 图片生成"
    },
    "image_config_header": {
        "en": "🖼️ Image Configuration",
        "zh": "🖼️ 图片配置"
    },
    "default_images_label": {
        "en": "Default Image URLs (One per line)",
        "zh": "默认图片链接 (每行一个)"
    },
    "default_images_help": {
        "en": "These images will be used sequentially when no article image is found.",
        "zh": "当文章没有图片时，将按顺序使用这些图片。"
    },
    "schedule_system_header": {
        "en": "⏰ Schedule & System",
        "zh": "⏰ 定时与系统"
    },
    "auto_fetch_time_label": {
        "en": "Auto Fetch Time",
        "zh": "自动抓取时间"
    },
    "auto_push_time_label": {
        "en": "Auto Push Time",
        "zh": "自动推送时间"
    },
    "fetch_time_period_label": {
        "en": "Fetch Time Period",
        "zh": "抓取时间周期"
    },
    "time_period_24h": {
        "en": "Within 24 Hours",
        "zh": "24小时内"
    },
    "time_period_3d": {
        "en": "Within 3 Days",
        "zh": "3天内"
    },
    "time_period_7d": {
        "en": "Within 7 Days",
        "zh": "7天内"
    },
    "time_period_custom": {
        "en": "Custom (Hours)",
        "zh": "自由选择 (小时)"
    },
    "custom_hours_label": {
        "en": "Custom Hours",
        "zh": "自定义小时数"
    },
    "timezone_label": {
        "en": "Timezone",
        "zh": "时区"
    },
    "notifications_header": {
        "en": "📢 Notifications",
        "zh": "📢 通知"
    },
    "webhook_url_label": {
        "en": "Enterprise WeChat Webhook URL",
        "zh": "企业微信 Webhook URL"
    },
    "manual_webhook_url_label": {
        "en": "Manual Push Webhook URL",
        "zh": "手动发布 Webhook URL"
    },
    "manual_webhook_help": {
        "en": "Configure a separate webhook for manual publishing flow.",
        "zh": "为手动发布流程配置独立的 Webhook 链接。"
    },
    "save_config_button": {
        "en": "💾 Save Configuration",
        "zh": "💾 保存配置"
    },
    "config_saved_success": {
        "en": "Configuration saved successfully!",
        "zh": "配置保存成功！"
    },
    "test_connection_header": {
        "en": "### Test Connection",
        "zh": "### 测试连接"
    },
    "test_webhook_button": {
        "en": "🚀 Test Webhook",
        "zh": "🚀 测试 Webhook"
    },
    "sending_test_msg": {
        "en": "Sending test message...",
        "zh": "正在发送测试消息..."
    },
    "enter_webhook_warning": {
        "en": "Please enter a Webhook URL first.",
        "zh": "请先输入 Webhook URL。"
    },
    # Sources Page
    "source_manager_page_title": {
        "en": "Source Manager",
        "zh": "源管理"
    },
    "data_source_manager_title": {
        "en": "📡 Data Source Manager",
        "zh": "📡 数据源管理"
    },
    "add_new_source_expander": {
        "en": "➕ Add New Source",
        "zh": "➕ 添加新源"
    },
    "add_source_tab_single": {
        "en": "Single Entry",
        "zh": "单个录入"
    },
    "add_source_tab_batch": {
        "en": "Batch Import (AI)",
        "zh": "批量导入 (AI)"
    },
    "batch_import_instruction": {
        "en": "Paste text containing RSS URLs (e.g., a blog list or raw links). AI will extract them automatically.",
        "zh": "在此粘贴包含 RSS 地址的文本（如博客列表或原始链接）。AI 将自动提取。"
    },
    "analyze_button": {
        "en": "🔍 Analyze with AI",
        "zh": "🔍 AI 智能解析"
    },
    "analyzing_spinner": {
        "en": "🤖 Analyzing text for RSS feeds...",
        "zh": "🤖 正在分析文本提取 RSS 源..."
    },
    "import_selected_button": {
        "en": "📥 Import Selected Sources",
        "zh": "📥 导入选中的源"
    },
    "no_sources_found_warning": {
        "en": "⚠️ No valid sources found in the text.",
        "zh": "⚠️ 未在文本中找到有效的源。"
    },
    "batch_import_success": {
        "en": "✅ Successfully imported {} sources!",
        "zh": "✅ 成功导入 {} 个源！"
    },
    "source_name_label": {
        "en": "Source Name",
        "zh": "源名称"
    },
    "source_type_label": {
        "en": "Type",
        "zh": "类型"
    },
    "source_url_label": {
        "en": "URL",
        "zh": "URL"
    },
    "source_group_label": {
        "en": "Group",
        "zh": "分组"
    },
    "source_group_placeholder": {
        "en": "e.g. Tech, Finance (Default if empty)",
        "zh": "如：科技，财经（留空则为 Default）"
    },
    "add_source_button": {
        "en": "Add Source",
        "zh": "添加源"
    },
    "source_group_batch_label": {
        "en": "Target Group for Imported Sources",
        "zh": "导入源的目标分组"
    },
    "added_source_success": {
        "en": "Added source: {}",
        "zh": "已添加源：{}"
    },
    "name_url_required_error": {
        "en": "Name and URL are required.",
        "zh": "名称和 URL 为必填项。"
    },
    "manage_sources_header": {
        "en": "📋 Manage Sources",
        "zh": "📋 管理源"
    },
    "no_sources_info": {
        "en": "No sources configured yet. Add one above!",
        "zh": "尚未配置源。请在上方添加！"
    },
    "active_column_label": {
        "en": "Active",
        "zh": "启用"
    },
    "active_column_help": {
        "en": "Toggle to enable/disable this source",
        "zh": "切换以启用/禁用此源"
    },
    "last_fetched_column_label": {
        "en": "Last Fetched",
        "zh": "上次抓取"
    },
    "delete_source_caption": {
        "en": "To delete a source, select it below:",
        "zh": "要删除源，请在下方选择："
    },
    "select_source_delete_label": {
        "en": "Select Source to Delete/Test",
        "zh": "选择要删除/测试的源"
    },
    "delete_button_label": {
        "en": "🗑️ Delete '{}'",
        "zh": "🗑️ 删除 '{}'"
    },
    "source_deleted_success": {
        "en": "Source deleted.",
        "zh": "源已删除。"
    },
    "test_fetch_button_label": {
        "en": "🕸️ Test Fetch '{}'",
        "zh": "🕸️ 测试抓取 '{}'"
    },
    "test_fetch_info": {
        "en": "Test fetch functionality will be implemented in Phase 3.",
        "zh": "测试抓取功能将在第三阶段实现。"
    },
    "batch_delete_button": {
        "en": "🗑️ Delete Selected Sources",
        "zh": "🗑️ 批量删除选中源"
    },
    "batch_delete_success": {
        "en": "Successfully deleted {} sources.",
        "zh": "成功删除 {} 个源。"
    },
    "batch_delete_warning": {
        "en": "Please select sources to delete.",
        "zh": "请选择要删除的源。"
    },
    "batch_test_fetch_button": {
        "en": "🕸️ Test Fetch Selected",
        "zh": "🕸️ 测试抓取选中源"
    },
    "test_fetch_results_title": {
        "en": "Test Fetch Results",
        "zh": "测试抓取结果"
    },
    "test_fetch_success": {
        "en": "Successfully fetched {} items from {} sources.",
        "zh": "成功从 {} 个源抓取 {} 条内容。"
    },
    "test_fetch_no_results": {
        "en": "No items found.",
        "zh": "未找到内容。"
    },
    "fetching_spinner": {
        "en": "Fetching data...",
        "zh": "正在抓取数据..."
    },
    "discovery_mode_label": {
        "en": "Discovery Mode",
        "zh": "发现模式"
    },
    "mode_parse_text": {
        "en": "Parse Text",
        "zh": "解析文本"
    },
    "mode_topic_search": {
        "en": "Topic Search",
        "zh": "主题搜索"
    },
    "topic_search_placeholder": {
        "en": "Enter a topic (e.g. AI, Finance)",
        "zh": "输入主题（如：人工智能、财经）"
    },
    "search_sources_button": {
        "en": "🔍 Search Sources",
        "zh": "🔍 搜索源"
    },
    "searching_spinner": {
        "en": "🤖 Searching for sources...",
        "zh": "🤖 正在搜索源..."
    },
    "verify_sources_label": {
        "en": "Verify Connectivity",
        "zh": "验证连通性"
    },
    "verify_sources_help": {
        "en": "Test if the sources are accessible before importing.",
        "zh": "导入前测试源是否可访问。"
    },
    "verifying_spinner": {
        "en": "Verifying connectivity...",
        "zh": "正在验证连通性..."
    },
    # Workspace Page
    "workspace_page_title": {
        "en": "Workspace",
        "zh": "工作区"
    },
    "daily_news_workspace_title": {
        "en": "📝 Daily News Workspace",
        "zh": "📝 每日新闻工作区"
    },
    "todays_news_info": {
        "en": "📅 Today's News ({}) - Status: **{}**",
        "zh": "📅 今日新闻 ({}) - 状态：**{}**"
    },
    "no_news_warning": {
        "en": "⚠️ No news generated for today yet.",
        "zh": "⚠️ 今日尚未生成新闻。"
    },
    "start_generation_button": {
        "en": "🚀 Start Generation",
        "zh": "🚀 开始生成"
    },
    "select_groups_label": {
        "en": "Select Source Groups",
        "zh": "选择新闻分组"
    },
    "select_groups_help": {
        "en": "Leave empty to use ALL enabled sources.",
        "zh": "留空则使用所有已启用源。"
    },
    "max_items_label": {
        "en": "Max Items to Process",
        "zh": "最大处理条数"
    },
    "max_items_help": {
        "en": "Limit the number of news items to process (1-30).",
        "zh": "限制处理的新闻条数 (1-30)。"
    },
    "topic_filter_header": {
        "en": "Topic Filter",
        "zh": "主题筛选"
    },
    "topic_input_label": {
        "en": "Enter Topic",
        "zh": "输入感兴趣的主题"
    },
    "filter_max_items_label": {
        "en": "Max Items in Filtered Version",
        "zh": "筛选版本最大条数"
    },
    "filter_max_items_help": {
        "en": "Limit the number of articles in the generated version (1-20).",
        "zh": "限制生成版本中的文章数量 (1-20)。"
    },
    "generate_filtered_version_button": {
        "en": "Generate Filtered Version",
        "zh": "生成筛选版本"
    },
    "filtering_spinner": {
        "en": "Filtering articles...",
        "zh": "正在筛选文章..."
    },
    "generation_complete_success": {
        "en": "Generation Complete!",
        "zh": "生成完成！"
    },
    "generation_error": {
        "en": "Error during generation: {}",
        "zh": "生成过程中出错：{}"
    },
    "editor_header": {
        "en": "Editor (Markdown)",
        "zh": "编辑器 (Markdown)"
    },
    "content_label": {
        "en": "Content",
        "zh": "内容"
    },
    "save_changes_button": {
        "en": "💾 Save Changes",
        "zh": "💾 保存更改"
    },
    "changes_saved_toast": {
        "en": "Changes saved!",
        "zh": "更改已保存！"
    },
    "live_preview_header": {
        "en": "Live Preview",
        "zh": "实时预览"
    },
    "publish_header": {
        "en": "🚀 Publish",
        "zh": "🚀 发布"
    },
    "confirm_push_button": {
        "en": "✅ Confirm & Push to WeCom",
        "zh": "✅ 确认并推送到企业微信"
    },
    "pushing_spinner": {
        "en": "Pushing to WeCom...",
        "zh": "正在推送到企业微信..."
    },
    "push_success": {
        "en": "Successfully pushed to Enterprise WeChat!",
        "zh": "成功推送到企业微信！"
    },
    "push_failed": {
        "en": "Failed to push. Check configuration and logs.",
        "zh": "推送失败。请检查配置和日志。"
    },
    "smart_format_adjustment_header": {
        "en": "🤖 Smart Format Adjustment",
        "zh": "🤖 AI 智能调整推送格式"
    },
    "push_format_label": {
        "en": "Select Push Format",
        "zh": "选择推送格式"
    },
    "format_standard_markdown": {
        "en": "Standard Markdown (Default)",
        "zh": "标准 Markdown (默认)"
    },
    "format_news": {
        "en": "News (Graph-Text)",
        "zh": "图文格式 (News)"
    },
    "format_markdown_v2": {
        "en": "Markdown V2 (AI Optimized)",
        "zh": "Markdown V2 (AI 优化)"
    },
    "smart_parse_button": {
        "en": "✨ Smart Parse Format",
        "zh": "✨ 智能解析格式"
    },
    "parsing_spinner": {
        "en": "AI is parsing content...",
        "zh": "AI 正在解析内容..."
    },
    "parsed_json_label": {
        "en": "Adjust JSON Payload",
        "zh": "调整 JSON Payload"
    },
    "preview_parsed_header": {
        "en": "Parsed Preview",
        "zh": "解析后预览"
    },
    "json_parse_error": {
        "en": "⚠️ Invalid JSON format.",
        "zh": "⚠️ JSON 格式无效。"
    },
    # Feishu Receiver
    "feishu_receiver_header": {
        "en": "Feishu Link Integration",
        "zh": "飞书转发链接接入"
    },
    "feishu_enable_receiver": {
        "en": "Enable local receiver service",
        "zh": "启用本地接收服务"
    },
    "feishu_enable_receiver_help": {
        "en": "Start an HTTP service locally to receive links forwarded via Feishu and add them to the unread list.",
        "zh": "开启后会在本机启动一个 HTTP 服务，用于接收飞书转发的链接并写入未读清单。"
    },
    "feishu_host_label": {
        "en": "Listen Address",
        "zh": "监听地址"
    },
    "feishu_host_help": {
        "en": "Keep 127.0.0.1 for local only; use 0.0.0.0 for LAN access.",
        "zh": "一般保持 127.0.0.1；若需局域网访问可改为 0.0.0.0"
    },
    "feishu_port_label": {
        "en": "Port",
        "zh": "端口"
    },
    "feishu_token_label": {
        "en": "Token (optional)",
        "zh": "Token（可选）"
    },
    "feishu_token_help": {
        "en": "If set, include ?token=... in the callback URL for simple verification.",
        "zh": "若设置 Token，请在回调 URL 上携带 ?token=... 用于简单校验"
    },
    # Status
    "status_unknown": {
        "en": "Unknown",
        "zh": "未知"
    },
    "status_pending_review": {
        "en": "Pending Review",
        "zh": "待审核"
    },
    "status_published": {
        "en": "Published",
        "zh": "已发布"
    }
}

def get_text(key, *args):
    """
    Get translated text for the given key.
    If args are provided, format the text with them.
    """
    # Default to Chinese if language is not set
    if 'language' not in st.session_state:
        st.session_state['language'] = '中文'
        
    lang = st.session_state['language']
    lang_code = 'zh' if lang == '中文' else 'en'
    
    # Get translation or fallback to key
    text_dict = TRANSLATIONS.get(key, {})
    text = text_dict.get(lang_code, key)
    
    # If the key itself is missing or translation missing, try to find english
    if text == key and lang_code == 'zh':
        text = text_dict.get('en', key)
        
    if args:
        try:
            return text.format(*args)
        except:
            return text
    return text

def init_language():
    """Initialize language state if not exists"""
    if 'language' not in st.session_state:
        st.session_state['language'] = '中文'

def language_selector():
    """Render language selector widget"""
    # Use columns to place it in the top right
    # This should be called inside the main function of each page, 
    # preferably before the title or in a sidebar if preferred.
    # To mimic "top right", we can use columns.
    
    # We use a container to push it to the right
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col2:
            st.selectbox(
                "Language / 语言", 
                ["中文", "English"], 
                key="language", 
                label_visibility="collapsed",
                index=0 if st.session_state.get('language', '中文') == '中文' else 1
            )
