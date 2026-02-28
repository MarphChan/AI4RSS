import streamlit as st
import sys
import os
import requests
import frontmatter
from datetime import datetime

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import news_generator
from core.config_manager import config_manager
from core.source_manager import source_manager
from core.llm import llm_engine
from core.pusher import pusher
from core import i18n
import json

st.set_page_config(page_title="Workspace", page_icon="📝", layout="wide")

def test_webhook(url):
    """Send a test message to the webhook."""
    try:
        payload = {
            "msgtype": "text",
            "text": {
                "content": "👋 Hello! This is a test message from AI Daily News Assistant."
            }
        }
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return True, "Success! Message sent."
        else:
            return False, f"Failed. Status: {response.status_code}, Body: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    i18n.init_language()
    
    # Language Selector (Top Right)
    col_title, col_lang = st.columns([8, 2])
    with col_lang:
        st.selectbox(
            "Language", 
            ["中文", "English"], 
            key="language", 
            label_visibility="collapsed",
            index=0 if st.session_state.get('language', '中文') == '中文' else 1
        )
        
    with col_title:
        st.title(i18n.get_text("daily_news_workspace_title"))
    
    # Check if today's news exists
    today_versions = news_generator.get_today_versions()
    selected_version_path = None
    today_content = None
    
    # Top Action Bar
    col_status, col_action = st.columns([3, 1])
    
    with col_status:
        if today_versions:
            # Version Selector
            
            c_ver, c_info, c_del = st.columns([2, 2, 0.5])
            with c_ver:
                # Create friendly labels
                version_labels = []
                label_to_path = {}
                for p in today_versions:
                    fname = os.path.basename(p)
                    if "-v" in fname:
                        v_num = fname.split("-v")[1].replace(".md", "")
                        label = f"v{v_num}"
                    else:
                        label = "Original"
                    
                    full_label = f"{label} ({fname})"
                    version_labels.append(full_label)
                    label_to_path[full_label] = p
                
                selected_label = st.selectbox(
                    "Select Version",
                    options=version_labels,
                    label_visibility="collapsed",
                    key="version_selector"
                )
                selected_version_path = label_to_path[selected_label]
                today_content = news_generator.load_news(selected_version_path)
                
            with c_info:
                if today_content:
                    post = frontmatter.loads(today_content)
                    status = post.metadata.get('status', 'unknown')
                    status_display = i18n.get_text(f"status_{status}", status)
                    st.info(f"📅 {datetime.now().strftime('%Y-%m-%d')} | {status_display}")
            
            with c_del:
                if st.button("🗑️", help="Delete this version", type="secondary"):
                    if news_generator.delete_news(selected_version_path):
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Failed")
        else:
            st.warning(i18n.get_text("no_news_warning"))

    with col_action:
        # Group Selection
        available_groups = source_manager.get_all_groups()
        selected_groups = st.multiselect(
            i18n.get_text("select_groups_label"),
            available_groups,
            placeholder="Select Groups (Empty=All)",
            help=i18n.get_text("select_groups_help"),
            label_visibility="collapsed"
        )
        
        # Max Items Setting
        max_items = st.number_input(
            i18n.get_text("max_items_label"),
            min_value=1,
            max_value=30,
            value=config_manager.get("system.max_items", 20),
            help=i18n.get_text("max_items_help")
        )

        # Show which sources are selected (Preview count)
        if selected_groups:
             selected_sources = source_manager.get_enabled_sources(selected_groups)
             st.caption(f"Selected {len(selected_sources)} sources.")
        else:
             all_sources = source_manager.get_enabled_sources()
             st.caption(f"All {len(all_sources)} sources selected.")

        if st.button(i18n.get_text("start_generation_button"), type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(msg, value):
                status_text.text(msg)
                progress_bar.progress(value)
            
            try:
                final_content = news_generator.generate_daily_news(
                    progress_callback=update_progress, 
                    target_groups=selected_groups,
                    max_items=max_items
                )
                if final_content.startswith("No"): # Error message
                    st.error(final_content)
                else:
                    st.success(i18n.get_text("generation_complete_success"))
                    st.rerun()
            except Exception as e:
                st.error(i18n.get_text("generation_error", e))

        st.divider()

        # Topic Filter
        if today_content:
            st.markdown(f"**{i18n.get_text('topic_filter_header')}**")
            
            c_topic, c_limit = st.columns([3, 1])
            with c_topic:
                topic = st.text_input(
                    i18n.get_text("topic_input_label"),
                    placeholder="Tech, AI, Medical...",
                    label_visibility="collapsed"
                )
            with c_limit:
                filter_max_items = st.number_input(
                    i18n.get_text("filter_max_items_label"),
                    min_value=1,
                    max_value=20,
                    value=5,
                    help=i18n.get_text("filter_max_items_help"),
                    label_visibility="collapsed"
                )
            
            if st.button(i18n.get_text("generate_filtered_version_button"), use_container_width=True):
                if topic:
                    with st.spinner(i18n.get_text("filtering_spinner")):
                        # Lazy import to avoid circular dependency issues if any
                        from core.topic_filter import topic_filter
                        # selected_version_path is defined in col_status block
                        if selected_version_path:
                            result = topic_filter.filter_and_save_version(
                                selected_version_path, 
                                topic,
                                max_items=filter_max_items
                            )
                            
                            if result and not result.startswith("Error") and not result.startswith("No"):
                                st.success(f"Success! {os.path.basename(result)}")
                                st.rerun()
                            else:
                                st.error(result)
                        else:
                            st.error("No version selected.")
                else:
                    st.warning("Please enter a topic.")

    st.divider()

    # Split View Editor
    if today_content:
        # Load content again to be safe
        post = frontmatter.loads(today_content)
        
        col_editor, col_preview = st.columns(2)
        
        with col_editor:
            st.subheader(i18n.get_text("editor_header"))
            # We separate metadata from content for editing, or just edit the body?
            # Ideally we only edit the body. Metadata is handled by system.
            
            # Using st.text_area for body editing
            edited_body = st.text_area(
                i18n.get_text("content_label"), 
                value=post.content, 
                height=800,
                label_visibility="collapsed"
            )
            
            # Save button
            if st.button(i18n.get_text("save_changes_button")):
                # Update content
                post.content = edited_body
                # Write back to file
                new_file_content = frontmatter.dumps(post)
                # filepath = news_generator.get_today_filepath()
                filepath = selected_version_path
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                st.toast(i18n.get_text("changes_saved_toast"))
                st.rerun()

        with col_preview:
            st.subheader(i18n.get_text("live_preview_header"))
            st.markdown(edited_body, unsafe_allow_html=True)

        st.divider()
        
        # Push Section
        st.subheader(i18n.get_text("publish_header"))
        
        # Notification Settings
        st.markdown("#### " + i18n.get_text("notifications_header"))
        
        current_config = config_manager.config
        webhook_url = st.text_input(
            i18n.get_text("webhook_url_label"),
            value=current_config["notification"].get("webhook_url", ""),
            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
        )
        
        if st.button(i18n.get_text("save_config_button"), key="save_webhook"):
            new_config = current_config.copy()
            new_config["notification"]["webhook_url"] = webhook_url
            config_manager.save(new_config)
            st.success(i18n.get_text("config_saved_success"))
            
        # Test Connection
        st.markdown("#### " + i18n.get_text("test_connection_header"))
        if st.button(i18n.get_text("test_webhook_button"), key="test_webhook"):
            if webhook_url:
                with st.spinner(i18n.get_text("sending_test_msg")):
                    success, msg = test_webhook(webhook_url)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
            else:
                st.warning(i18n.get_text("enter_webhook_warning"))

        st.divider()

        # --- Smart Format Adjustment ---
        st.subheader(i18n.get_text("smart_format_adjustment_header"))
        
        format_options = {
            "markdown": i18n.get_text("format_standard_markdown"),
            "news_custom": i18n.get_text("format_news"),
            "markdown_custom": i18n.get_text("format_markdown_v2")
        }
        
        selected_format_key = st.radio(
            i18n.get_text("push_format_label"),
            list(format_options.keys()),
            format_func=lambda x: format_options[x],
            horizontal=True
        )
        
        if selected_format_key == "markdown_custom":
            st.caption("ℹ️ Note: Markdown V2 format does not support images.")

        
        # State management for parsed payload
        if 'parsed_payload' not in st.session_state:
            st.session_state['parsed_payload'] = None
        if 'parse_counter' not in st.session_state:
            st.session_state['parse_counter'] = 0
            
        if selected_format_key != "markdown":
            # Show Smart Parse Button
            if st.button(i18n.get_text("smart_parse_button"), type="secondary"):
                with st.spinner(i18n.get_text("parsing_spinner")):
                    # Determine target format type for LLM
                    target_type = "news" if selected_format_key == "news_custom" else "markdown"
                    # Use the latest content from file (user should save first)
                    parsed_result = llm_engine.convert_to_format(post.content, target_type)
                    st.session_state['parsed_payload'] = parsed_result
                    st.session_state['parse_counter'] += 1
            
            # Show Editor for Parsed Payload
            if st.session_state.get('parsed_payload'):
                col_json, col_preview_json = st.columns(2)
                
                with col_json:
                    st.markdown(f"**{i18n.get_text('parsed_json_label')}**")
                    json_str = st.text_area(
                        "JSON Payload",
                        value=json.dumps(st.session_state['parsed_payload'], indent=2, ensure_ascii=False),
                        height=400,
                        label_visibility="collapsed",
                        key=f"json_payload_{st.session_state['parse_counter']}"
                    )
                    
                    # Try to parse edits back to JSON
                    try:
                        st.session_state['parsed_payload'] = json.loads(json_str)
                    except json.JSONDecodeError:
                        st.error(i18n.get_text("json_parse_error"))

                with col_preview_json:
                    st.markdown(f"**{i18n.get_text('preview_parsed_header')}**")
                    payload = st.session_state['parsed_payload']
                    
                    if selected_format_key == "news_custom":
                        # Render News Preview
                        articles = payload.get("news", {}).get("articles", [])
                        if articles:
                            for art in articles:
                                with st.container(border=True):
                                    if art.get("picurl"):
                                        st.image(art["picurl"], use_column_width=True)
                                    st.markdown(f"**{art.get('title', 'No Title')}**")
                                    st.caption(art.get("description", ""))
                                    if art.get("url"):
                                        st.markdown(f"[Read More]({art['url']})")
                        else:
                            st.info("No articles found in payload.")
                            
                    elif selected_format_key == "markdown_custom":
                        # Render Markdown Preview
                        md_content = payload.get("markdown_v2", {}).get("content", "")
                        st.markdown(md_content)
        else:
            # Clear custom payload if switched back to standard
            if st.session_state.get('parsed_payload'):
                st.session_state['parsed_payload'] = None

        st.divider()

        col_push_btn, col_push_info = st.columns([1, 4])
        
        with col_push_btn:
            if st.button(i18n.get_text("confirm_push_button"), type="primary"):
                with st.spinner(i18n.get_text("pushing_spinner")):
                    # Decide what to push
                    if selected_format_key != "markdown" and st.session_state.get('parsed_payload'):
                        success = pusher.push(st.session_state['parsed_payload'])
                    else:
                        success = pusher.push(post.content)
                    
                if success:
                    st.success(i18n.get_text("push_success"))
                    # Update status
                    post.metadata['status'] = 'published'
                    new_file_content = frontmatter.dumps(post)
                    # filepath = news_generator.get_today_filepath()
                    filepath = selected_version_path
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_file_content)
                    st.rerun()
                else:
                    st.error(i18n.get_text("push_failed"))

if __name__ == "__main__":
    main()
