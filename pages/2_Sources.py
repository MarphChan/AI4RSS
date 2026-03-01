import streamlit as st
import sys
import os
import pandas as pd

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.source_manager import source_manager
from core.llm import llm_engine
from core.fetcher import fetcher
from core import i18n

st.set_page_config(page_title="Source Manager", page_icon="📡", layout="wide")

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
        st.title(i18n.get_text("data_source_manager_title"))
    
    # --- Add New Source Section ---
    with st.expander(i18n.get_text("add_new_source_expander"), expanded=True):
        tab1, tab2 = st.tabs([i18n.get_text("add_source_tab_single"), i18n.get_text("add_source_tab_batch")])
        
        with tab1:
            with st.form("add_source_form"):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
                
                with col1:
                    new_name = st.text_input(i18n.get_text("source_name_label"), placeholder="e.g. OpenAI Blog")
                
                with col2:
                    new_type = st.selectbox(i18n.get_text("source_type_label"), ["rss", "web_crawl", "social"])
                
                with col3:
                    new_group = st.text_input(i18n.get_text("source_group_label"), placeholder="Default")
                
                with col4:
                    new_url = st.text_input(i18n.get_text("source_url_label"), placeholder="https://example.com/rss.xml")
                
                new_logo = st.text_input("Logo URL", placeholder="https://example.com/logo.png", help="Optional logo for this source")
                
                submitted = st.form_submit_button(i18n.get_text("add_source_button"))
                
                if submitted:
                    if new_name and new_url:
                        group_val = new_group if new_group.strip() else "Default"
                        source_manager.add_source(new_name, new_type, new_url, group_val, new_logo)
                        st.success(i18n.get_text("added_source_success", new_name))
                        st.rerun()
                    else:
                        st.error(i18n.get_text("name_url_required_error"))

        with tab2:
            st.caption(i18n.get_text("batch_import_instruction"))
            
            # Discovery Mode
            mode = st.radio(
                i18n.get_text("discovery_mode_label"),
                [i18n.get_text("mode_parse_text"), i18n.get_text("mode_topic_search")],
                horizontal=True,
                label_visibility="collapsed"
            )

            # Group input (shared)
            batch_group = st.text_input(i18n.get_text("source_group_batch_label"), placeholder="Default", key="batch_group_input")
            
            if mode == i18n.get_text("mode_parse_text"):
                batch_text = st.text_area("Batch Input", height=150, label_visibility="collapsed")
                if st.button(i18n.get_text("analyze_button")):
                    if batch_text:
                        with st.spinner(i18n.get_text("analyzing_spinner")):
                            candidates = llm_engine.parse_rss_sources(batch_text)
                            if candidates:
                                for c in candidates: c['import'] = True
                                st.session_state['batch_candidates'] = candidates
                            else:
                                st.warning(i18n.get_text("no_sources_found_warning"))
                                if 'batch_candidates' in st.session_state: del st.session_state['batch_candidates']
            else:
                col_topic, col_verify_chk = st.columns([3, 1])
                with col_topic:
                    topic_input = st.text_input(i18n.get_text("topic_search_placeholder"), label_visibility="collapsed")
                with col_verify_chk:
                    verify_connectivity = st.checkbox(i18n.get_text("verify_sources_label"), value=True, help=i18n.get_text("verify_sources_help"))
                
                if st.button(i18n.get_text("search_sources_button")):
                    if topic_input:
                        with st.spinner(i18n.get_text("searching_spinner")):
                            raw_candidates = llm_engine.find_rss_sources(topic_input)
                            
                            if raw_candidates:
                                # Verification step
                                if verify_connectivity:
                                    with st.spinner(i18n.get_text("verifying_spinner")):
                                        valid_candidates = []
                                        for c in raw_candidates:
                                            is_valid = fetcher.check_availability(c['url'], c.get('type', 'rss'))
                                            if is_valid:
                                                c['import'] = True
                                                c['status'] = "✅ Verified"
                                                valid_candidates.append(c)
                                        candidates = valid_candidates
                                else:
                                    for c in raw_candidates: c['import'] = True
                                    candidates = raw_candidates
                                
                                if candidates:
                                    st.session_state['batch_candidates'] = candidates
                                else:
                                    st.warning(i18n.get_text("no_sources_found_warning"))
                                    if 'batch_candidates' in st.session_state: del st.session_state['batch_candidates']
                            else:
                                st.warning(i18n.get_text("no_sources_found_warning"))
                                if 'batch_candidates' in st.session_state: del st.session_state['batch_candidates']

            # Display Candidates
            if 'batch_candidates' in st.session_state and st.session_state['batch_candidates']:
                st.divider()
                
                candidates_df = pd.DataFrame(st.session_state['batch_candidates'])
                
                # Config columns
                col_config = {
                    "import": st.column_config.CheckboxColumn("Import?", default=True),
                    "name": "Name",
                    "url": "URL",
                    "type": "Type"
                }
                if "status" in candidates_df.columns:
                    col_config["status"] = "Status"

                edited_candidates = st.data_editor(
                    candidates_df,
                    column_config=col_config,
                    hide_index=True,
                    use_container_width=True,
                    key="batch_editor"
                )

                st.session_state["batch_candidates"] = edited_candidates.to_dict("records")
                
                if st.button(i18n.get_text("import_selected_button")):
                    count = 0
                    target_group = batch_group if batch_group.strip() else "Default"
                    for index, row in edited_candidates.iterrows():
                        if row.get('import', False):
                            source_manager.add_source(row['name'], row.get('type', 'rss'), row['url'], target_group)
                            count += 1
                    
                    if count > 0:
                        st.success(i18n.get_text("batch_import_success", count))
                        del st.session_state['batch_candidates']
                        st.rerun()

    st.divider()

    # --- Manage Existing Sources Section ---
    st.subheader(i18n.get_text("manage_sources_header"))
    
    sources = source_manager.get_all_sources()
    
    if not sources:
        st.info(i18n.get_text("no_sources_info"))
    else:
        # Prepare data for display
        df = pd.DataFrame(sources)
        
        # We want to make "enabled" editable. 
        # Streamlit's data_editor is perfect for this.
        
        # Reorder columns for better UX
        display_columns = ["enabled", "group", "name", "type", "url", "logo", "last_crawl_time", "id"]
        
        # Check if columns exist (safety)
        available_cols = [c for c in display_columns if c in df.columns]
        # If group is missing in older sources, fill it
        if "group" not in df.columns:
            df["group"] = "Default"
            available_cols.insert(1, "group")
        # If logo is missing
        if "logo" not in df.columns:
            df["logo"] = ""
            if "logo" in display_columns and "logo" not in available_cols:
                available_cols.insert(5, "logo")

        df_display = df[available_cols]

        edited_df = st.data_editor(
            df_display,
            column_config={
                "enabled": st.column_config.CheckboxColumn(
                    i18n.get_text("active_column_label"),
                    help=i18n.get_text("active_column_help"),
                    default=True,
                ),
                "group": st.column_config.TextColumn(
                    i18n.get_text("source_group_label"),
                    help=i18n.get_text("source_group_placeholder"),
                    width="small"
                ),
                "name": i18n.get_text("source_name_label"),
                "type": i18n.get_text("source_type_label"),
                "url": st.column_config.LinkColumn(i18n.get_text("source_url_label")),
                "logo": st.column_config.TextColumn("Logo URL", width="medium"),
                "last_crawl_time": st.column_config.DatetimeColumn(
                    i18n.get_text("last_fetched_column_label"),
                    format="D MMM YYYY, HH:mm",
                    disabled=True
                ),
                "id": st.column_config.TextColumn("ID", disabled=True, width="small")
            },
            hide_index=True,
            use_container_width=True,
            key="source_editor"
        )
        
        # Detect changes in "enabled" status or other fields
        # Ideally, we compare edited_df with original sources.
        # But st.data_editor returns the new state. We need to sync back to JSON.
        
        if not df_display.equals(edited_df):
            # Find changed rows
            # Iterate through edited_df and update source_manager
            # This is a bit heavy for every interaction, but safe for small lists.
            
            for index, row in edited_df.iterrows():
                source_id = row['id']
                # Check if this row changed from original
                # Handle case where original df might not have group if it was just added in memory
                original_rows = df[df['id'] == source_id]
                if original_rows.empty: continue
                original_row = original_rows.iloc[0]
                
                updates = {}
                if row['enabled'] != original_row['enabled']:
                    updates['enabled'] = row['enabled']
                if row.get('group') != original_row.get('group', 'Default'):
                    updates['group'] = row['group']
                if row['name'] != original_row['name']:
                    updates['name'] = row['name']
                if row['type'] != original_row['type']:
                    updates['type'] = row['type']
                if row['url'] != original_row['url']:
                    updates['url'] = row['url']
                if row.get('logo') != original_row.get('logo', ''):
                    updates['logo'] = row['logo']
                
                if updates:
                    source_manager.update_source(source_id, updates)
            
            # st.toast("Changes saved automatically.") 
            # Rerun might be annoying here if it happens on every click, 
            # but needed to sync internal state if we had complex logic.
            # Streamlit data_editor handles state well, so maybe we don't need explicit rerun 
            # unless we want to refresh the "original" df.
            
        # Delete Buttons (Row-wise actions are hard in data_editor)
        # Batch Delete using checkboxes from data_editor (if we add a selection column)
        # Current data_editor has 'enabled', but maybe we add a 'select' column?
        # Streamlit 1.32 data_editor supports row selection if configured? 
        # Actually, adding a boolean column "Delete?" is the easiest way.
        
        st.divider()
        st.subheader(i18n.get_text("batch_delete_button").replace("🗑️ ", ""))
        
        # We need a new dataframe for selection
        df_for_selection = df_display.copy()
        df_for_selection.insert(0, "Select", False)
        
        # Use data editor for selection
        # Note: We need to use a different key to avoid conflicts
        
        edited_selection_df = st.data_editor(
            df_for_selection,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    default=False,
                    width="small"
                ),
                "enabled": st.column_config.CheckboxColumn(
                    i18n.get_text("active_column_label"),
                    default=True,
                    disabled=True # Disable editing other fields here to avoid confusion
                ),
                "group": st.column_config.TextColumn(
                    i18n.get_text("source_group_label"),
                    disabled=True
                ),
                "name": st.column_config.TextColumn(
                     i18n.get_text("source_name_label"),
                     disabled=True
                ),
                "type": st.column_config.TextColumn(
                     i18n.get_text("source_type_label"),
                     disabled=True
                ),
                "url": st.column_config.LinkColumn(i18n.get_text("source_url_label"), disabled=True),
                "last_crawl_time": st.column_config.DatetimeColumn(
                    i18n.get_text("last_fetched_column_label"),
                    format="D MMM YYYY, HH:mm",
                    disabled=True
                ),
                "id": st.column_config.TextColumn("ID", disabled=True, width="small")
            },
            hide_index=True,
            use_container_width=True,
            key="delete_selector"
        )

        col_batch_del, col_batch_test = st.columns([1, 1])
        
        with col_batch_del:
            if st.button(i18n.get_text("batch_delete_button"), type="primary"):
                # Collect IDs to delete
                ids_to_delete = []
                # edited_selection_df might be a delta or the full df depending on how streamlit handles it
                # data_editor returns the edited dataframe
                
                # Iterate through the returned dataframe
                for index, row in edited_selection_df.iterrows():
                    if row["Select"]:
                        ids_to_delete.append(row["id"])
                
                if ids_to_delete:
                    count = source_manager.delete_sources(ids_to_delete)
                    st.success(i18n.get_text("batch_delete_success", count))
                    st.rerun()
                else:
                    st.warning(i18n.get_text("batch_delete_warning"))
        
        with col_batch_test:
            if st.button(i18n.get_text("batch_test_fetch_button")):
                # Collect IDs to test
                ids_to_test = []
                for index, row in edited_selection_df.iterrows():
                    if row["Select"]:
                        ids_to_test.append(row["id"])
                
                if ids_to_test:
                     # Get source objects
                     sources_to_test = [s for s in sources if s['id'] in ids_to_test]
                     # Ensure enabled
                     for s in sources_to_test:
                         s['enabled'] = True
                     
                     with st.spinner(i18n.get_text("fetching_spinner")):
                         results = fetcher.fetch_all(sources_to_test)
                     
                     st.divider()
                     st.subheader(i18n.get_text("test_fetch_results_title"))
                     if results:
                         st.success(i18n.get_text("test_fetch_success", len(results), len(sources_to_test)))
                         
                         # Simplified display for batch
                         results_df = pd.DataFrame(results)
                         if not results_df.empty:
                            st.dataframe(
                                results_df[['source_name', 'title', 'pub_date', 'url']],
                                column_config={
                                    "url": st.column_config.LinkColumn("URL"),
                                    "pub_date": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, HH:mm")
                                },
                                use_container_width=True
                            )
                     else:
                         st.warning(i18n.get_text("test_fetch_no_results"))
                else:
                    st.warning(i18n.get_text("batch_delete_warning"))



if __name__ == "__main__":
    main()
