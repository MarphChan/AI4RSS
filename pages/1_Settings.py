import streamlit as st
import sys
import os
from datetime import time

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import config_manager
from core.llm import llm_engine
from core import i18n
from core.ui_nav import render_sidebar_navigation

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

def main():
    i18n.init_language()
    render_sidebar_navigation(active="settings")
    
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
        st.title(i18n.get_text("system_settings_title"))
    
    # Load current config
    current_config = config_manager.config
    
    with st.form("settings_form"):
        # Section 1: LLM Configuration
        st.subheader(i18n.get_text("llm_config_header"))
        col1, col2 = st.columns(2)
        
        provider_options = ["dashscope", "openai", "volcengine", "deepseek", "moonshot", "yi", "custom"]
        current_provider = current_config["llm"].get("provider", "dashscope")
        if current_provider not in provider_options:
            current_provider = "dashscope"

        with col1:
            provider = st.selectbox(
                i18n.get_text("llm_provider_label"), 
                provider_options,
                index=provider_options.index(current_provider)
            )
            model_name = st.text_input(
                i18n.get_text("model_name_label"), 
                value=current_config["llm"].get("model_name", "qwen-max"),
                help="e.g. qwen-max, gpt-4-turbo, deepseek-chat"
            )
        
        with col2:
            api_key = st.text_input(
                i18n.get_text("api_key_label"), 
                value=current_config["llm"].get("api_key", ""),
                type="password",
                help="Your API Key from the provider"
            )
            
            # Base URL (Advanced)
            base_url_val = current_config["llm"].get("base_url", "https://api.openai.com/v1")
            base_url = st.text_input(
                "Base URL (Custom)",
                value=base_url_val,
                help="Required if provider is 'custom'. Ignored for others unless overridden."
            )
            
        st.divider()
        
        # Section 2: Image Configuration
        st.subheader(i18n.get_text("image_config_header"))
        
        enable_image = st.checkbox(
            i18n.get_text("enable_image_gen_label"), 
            value=current_config["image"].get("enable_generation", True)
        )
        
        default_images_list = current_config["image"].get("default_images", [])
        default_images_str = "\n".join(default_images_list) if default_images_list else ""
        
        default_images_input = st.text_area(
            i18n.get_text("default_images_label"),
            value=default_images_str,
            help=i18n.get_text("default_images_help"),
            height=100
        )

        st.divider()

        # Section 3: Schedule & System
        st.subheader(i18n.get_text("schedule_system_header"))
        col3, col4 = st.columns(2)
        
        with col3:
            # Parse existing time strings "HH:MM" to datetime.time objects
            fetch_time_str = current_config["system"].get("fetch_time", "08:00")
            push_time_str = current_config["system"].get("push_time", "09:30")
            
            try:
                ft_h, ft_m = map(int, fetch_time_str.split(':'))
                pt_h, pt_m = map(int, push_time_str.split(':'))
                default_fetch = time(ft_h, ft_m)
                default_push = time(pt_h, pt_m)
            except:
                default_fetch = time(8, 0)
                default_push = time(9, 30)

            fetch_time = st.time_input(i18n.get_text("auto_fetch_time_label"), value=default_fetch)
            push_time = st.time_input(i18n.get_text("auto_push_time_label"), value=default_push)
            
        with col4:
            timezone = st.text_input(
                i18n.get_text("timezone_label"), 
                value=current_config["system"].get("timezone", "Asia/Shanghai"),
                disabled=True,
                help="Currently fixed to Asia/Shanghai"
            )

            # Time Period Selection
            current_period = current_config["system"].get("time_period", 24)
            
            # Map integer to selection label
            period_options = {
                24: i18n.get_text("time_period_24h"),
                72: i18n.get_text("time_period_3d"),
                168: i18n.get_text("time_period_7d"),
            }
            
            # Determine initial selection
            selected_label = i18n.get_text("time_period_custom")
            if current_period in period_options:
                selected_label = period_options[current_period]
            
            # Create the list of options for the selectbox
            options_list = list(period_options.values()) + [i18n.get_text("time_period_custom")]
            
            selected_option = st.selectbox(
                i18n.get_text("fetch_time_period_label"),
                options_list,
                index=options_list.index(selected_label)
            )
            
            custom_hours = current_period
            if selected_option == i18n.get_text("time_period_custom"):
                custom_hours = st.number_input(
                    i18n.get_text("custom_hours_label"),
                    min_value=1,
                    value=current_period if current_period not in period_options else 24,
                    step=1
                )

        st.divider()

        st.subheader("飞书转发链接接入")
        feishu_cfg = current_config.get("feishu", {})

        feishu_enabled = st.checkbox(
            "启用本地接收服务",
            value=bool(feishu_cfg.get("receiver_enabled", False)),
            help="开启后会在本机启动一个 HTTP 服务，用于接收飞书转发的链接并写入未读清单。"
        )

        c_f1, c_f2, c_f3 = st.columns([2, 1, 2])
        with c_f1:
            feishu_host = st.text_input(
                "监听地址",
                value=str(feishu_cfg.get("receiver_host", "127.0.0.1")),
                help="一般保持 127.0.0.1；若需局域网访问可改为 0.0.0.0"
            )
        with c_f2:
            feishu_port = st.number_input(
                "端口",
                min_value=1,
                max_value=65535,
                value=int(feishu_cfg.get("receiver_port", 8765)),
                step=1
            )
        with c_f3:
            feishu_token = st.text_input(
                "Token（可选）",
                value=str(feishu_cfg.get("receiver_token", "")),
                type="password",
                help="若设置 Token，请在回调 URL 上携带 ?token=... 用于简单校验"
            )

        st.divider()

        submitted = st.form_submit_button(i18n.get_text("save_config_button"))
        
        if submitted:
            # Update config object
            new_config = current_config.copy()
            
            # LLM
            new_config["llm"]["provider"] = provider
            new_config["llm"]["api_key"] = api_key
            new_config["llm"]["model_name"] = model_name
            new_config["llm"]["base_url"] = base_url
            
            # Image
            new_config["image"]["enable_generation"] = enable_image
            
            # Parse default images
            default_images_list = [
                line.strip() 
                for line in default_images_input.split('\n') 
                if line.strip()
            ]
            new_config["image"]["default_images"] = default_images_list
            
            # System
            new_config["system"]["fetch_time"] = fetch_time.strftime("%H:%M")
            new_config["system"]["push_time"] = push_time.strftime("%H:%M")
            
            # Handle Time Period
            if selected_option == i18n.get_text("time_period_custom"):
                new_config["system"]["time_period"] = int(custom_hours)
            else:
                # Find key by value from period_options
                rev_options = {v: k for k, v in period_options.items()}
                new_config["system"]["time_period"] = rev_options[selected_option]
            
            # Save to disk
            new_config.setdefault("feishu", {})
            new_config["feishu"]["receiver_enabled"] = bool(feishu_enabled)
            new_config["feishu"]["receiver_host"] = feishu_host
            new_config["feishu"]["receiver_port"] = int(feishu_port)
            new_config["feishu"]["receiver_token"] = feishu_token

            config_manager.save(new_config)
            llm_engine.reload()
            st.success(i18n.get_text("config_saved_success"))
            
            # Force reload to update state if needed, but not strictly necessary here

if __name__ == "__main__":
    main()
