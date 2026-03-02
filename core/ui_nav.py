import streamlit as st

from core import i18n


def render_sidebar_navigation(active: str):
    # Hide the default Streamlit sidebar navigation
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title(i18n.get_text("navigation"))

    items = [
        ("home", i18n.get_text("nav_home"), "app.py", "🏠"),
        ("settings", i18n.get_text("nav_settings"), "pages/1_Settings.py", "⚙️"),
        ("sources", i18n.get_text("nav_sources"), "pages/2_Sources.py", "📡"),
        ("workspace", i18n.get_text("nav_workspace"), "pages/3_Workspace.py", "📝"),
    ]

    for key, label, page_path, icon in items:
        st.sidebar.page_link(
            page_path,
            label=label,
            icon=icon,
        )
    
    st.sidebar.success(i18n.get_text("system_ready"))
