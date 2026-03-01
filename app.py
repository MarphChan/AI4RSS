import streamlit as st
import os
from core.scheduler import scheduler_service
from core.config_manager import config_manager
from core.feishu_receiver import FeishuReceiverService
from core import i18n

# Set page configuration first!
st.set_page_config(
    page_title="AI Daily News Assistant",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Start scheduler on app launch
# Use st.cache_resource to ensure it only starts once
@st.cache_resource
def start_scheduler():
    scheduler_service.start()
    return True

start_scheduler()

@st.cache_resource
def start_feishu_receiver():
    feishu_cfg = (config_manager.config or {}).get("feishu", {}) or {}
    if not feishu_cfg.get("receiver_enabled", False):
        return None
    service = FeishuReceiverService(
        host=str(feishu_cfg.get("receiver_host", "127.0.0.1")),
        port=int(feishu_cfg.get("receiver_port", 8765)),
        token=str(feishu_cfg.get("receiver_token", "")),
    )
    service.start()
    return service

start_feishu_receiver()

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
        st.title(i18n.get_text("page_title"))
    
    st.markdown(i18n.get_text("welcome_message"))

    # Sidebar Status
    st.sidebar.title(i18n.get_text("navigation"))
    st.sidebar.success(i18n.get_text("system_ready"))
    
    # Check if config exists
    if not os.path.exists("config.yaml"):
        st.warning(i18n.get_text("config_not_found"))

if __name__ == "__main__":
    main()
