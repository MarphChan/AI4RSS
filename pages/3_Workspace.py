import streamlit as st
import sys
import os
import requests
import frontmatter
from datetime import datetime
import pandas as pd
import re

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import news_generator
from core.config_manager import config_manager
from core.source_manager import source_manager
from core.llm import llm_engine
from core.pusher import pusher
from core.reading_list_manager import reading_list_manager
from core import i18n
from core.ui_nav import render_sidebar_navigation
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

def _init_workspace_state():
    if "workspace_step" not in st.session_state:
        st.session_state["workspace_step"] = "1.1 数据源设置与管理"
    if "parsed_payload" not in st.session_state:
        st.session_state["parsed_payload"] = None
    if "parse_counter" not in st.session_state:
        st.session_state["parse_counter"] = 0

def _render_version_bar(today_versions):
    selected_version_path = None
    today_content = None

    if not today_versions:
        st.warning(i18n.get_text("no_news_warning"))
        return selected_version_path, today_content

    c_ver, c_info, c_del = st.columns([2, 2, 0.5])
    with c_ver:
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
            key="version_selector",
        )
        selected_version_path = label_to_path[selected_label]
        today_content = news_generator.load_news(selected_version_path)

    with c_info:
        if today_content:
            post = frontmatter.loads(today_content)
            status = post.metadata.get("status", "unknown")
            status_display = i18n.get_text(f"status_{status}", status)
            st.info(f"📅 {datetime.now().strftime('%Y-%m-%d')} | {status_display}")

    with c_del:
        confirm_key = f"_confirm_del_{os.path.basename(selected_version_path or 'none')}"
        if not st.session_state.get(confirm_key):
            if st.button("🗑️", help="删除此版本（需二次确认）", type="secondary"):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            if st.button("⚠️确认", help="确认删除，不可恢复", type="primary"):
                st.session_state.pop(confirm_key, None)
                if news_generator.delete_news(selected_version_path):
                    st.rerun()
                else:
                    st.error("Failed")
            if st.button("取消", key="cancel_del_btn"):
                st.session_state.pop(confirm_key, None)
                st.rerun()

    return selected_version_path, today_content

def _render_step_selector():
    steps = [
        "1.1 数据源设置与管理",
        "1.2 阅读清单",
        "1.3 新闻预览与查看",
        "1.4 发布通知设置和格式设置",
    ]
    step_labels = {
        "1.1 数据源设置与管理": "数据源管理",
        "1.2 阅读清单": "阅读清单",
        "1.3 新闻预览与查看": "新闻预览",
        "1.4 发布通知设置和格式设置": "发布设置",
    }
    cols = st.columns([1.3, 0.15, 1.0, 0.15, 1.0, 0.15, 1.0])
    current = st.session_state.get("workspace_step", steps[0])
    for idx, step in enumerate(steps):
        with cols[idx * 2]:
            is_current = current == step
            if st.button(
                step_labels.get(step, step),
                key=f"workspace_breadcrumb_{idx}",
                type="primary" if is_current else "secondary",
                use_container_width=True,
            ):
                st.session_state["workspace_step"] = step
                st.rerun()
        if idx < len(steps) - 1:
            with cols[idx * 2 + 1]:
                st.markdown("**>**")

def _render_step_sources():
    st.subheader("1.1 数据源设置与管理")

    available_groups = source_manager.get_all_groups()
    if not available_groups:
        st.info(i18n.get_text("no_sources_info"))
        return
    group_options = ["全部"] + available_groups
    preferred_group = config_manager.get("workspace.source_group", "tech")
    if preferred_group not in group_options:
        preferred_group = "tech" if "tech" in available_groups else "全部"

    def _persist_workspace_source_group():
        cfg = dict(config_manager.config or {})
        workspace_cfg = cfg.get("workspace") or {}
        workspace_cfg["source_group"] = st.session_state.get("workspace_source_group")
        cfg["workspace"] = workspace_cfg
        config_manager.save(cfg)

    selected_group = st.selectbox(
        "数据源类型",
        group_options,
        index=group_options.index(preferred_group) if preferred_group in group_options else 0,
        key="workspace_source_group",
        on_change=_persist_workspace_source_group,
    )
    target_groups = None if selected_group == "全部" else [selected_group]

    max_items = st.number_input(
        i18n.get_text("max_items_label"),
        min_value=1,
        max_value=30,
        value=config_manager.get("system.max_items", 20),
        help=i18n.get_text("max_items_help"),
    )

    selected_sources = source_manager.get_enabled_sources(target_groups=target_groups)
    st.caption(f"Selected {len(selected_sources)} sources.")

    if st.button(i18n.get_text("start_generation_button"), type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(msg, value):
            status_text.text(msg)
            progress_bar.progress(value)

        try:
            final_content = news_generator.generate_daily_news(
                progress_callback=update_progress,
                target_groups=target_groups,
                max_items=max_items,
            )
            if final_content.startswith("ERROR:"):
                st.error(final_content)
            else:
                st.success(i18n.get_text("generation_complete_success"))
                st.session_state["workspace_step"] = "1.2 阅读清单"
                st.rerun()
        except Exception as e:
            st.error(i18n.get_text("generation_error", e))

    st.divider()

    with st.expander("快速管理数据源", expanded=True):
        sources = source_manager.get_all_sources()
        if not sources:
            st.info(i18n.get_text("no_sources_info"))
            return
        if selected_group != "全部":
            sources = [s for s in sources if s.get("group", "Default") == selected_group]

        df = pd.DataFrame(sources)
        display_columns = ["enabled", "group", "name", "type", "url", "logo", "last_crawl_time", "id"]
        available_cols = [c for c in display_columns if c in df.columns]
        if "group" not in df.columns:
            df["group"] = "Default"
            available_cols.insert(1, "group")
        if "logo" not in df.columns:
            df["logo"] = ""
            if "logo" in display_columns and "logo" not in available_cols:
                available_cols.insert(5, "logo")

        df_display = df[available_cols]
        disabled_cols = [c for c in df_display.columns if c != "enabled"]
        edited_df = st.data_editor(
            df_display,
            column_config={
                "enabled": st.column_config.CheckboxColumn(i18n.get_text("active_column_label"), default=True),
                "group": st.column_config.TextColumn(i18n.get_text("source_group_label"), width="small"),
                "name": i18n.get_text("source_name_label"),
                "type": i18n.get_text("source_type_label"),
                "url": st.column_config.LinkColumn(i18n.get_text("source_url_label")),
                "logo": st.column_config.TextColumn("Logo URL", width="medium"),
                "last_crawl_time": st.column_config.DatetimeColumn(i18n.get_text("last_fetched_column_label"), disabled=True),
                "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=disabled_cols,
            key="workspace_source_editor",
        )

        if not df_display.equals(edited_df):
            any_saved = False
            for _, row in edited_df.iterrows():
                source_id = row["id"]
                original_rows = df[df["id"] == source_id]
                if original_rows.empty:
                    continue
                original_row = original_rows.iloc[0]

                updates = {}
                if bool(row["enabled"]) != bool(original_row["enabled"]):
                    updates["enabled"] = bool(row["enabled"])

                if updates:
                    source_manager.update_source(source_id, updates)
                    any_saved = True

            if any_saved:
                # Use session flag so toast is visible after rerun
                st.session_state["_workspace_source_saved"] = True
                st.rerun()

        if st.session_state.pop("_workspace_source_saved", False):
            st.toast("已保存")

def _render_step_reading_list(selected_version_path, today_content):
    st.subheader("1.2 阅读清单")

    if today_content:
        post_for_reading = frontmatter.loads(today_content)
        articles_meta = post_for_reading.metadata.get("articles_meta", []) or []
        reading_list_manager.sync_articles(articles_meta)
    else:
        st.caption("未选择今日版本，将展示历史阅读清单；如需同步最新生成条目，请先在 1.1 生成或选择版本。")

    feishu_cfg = (config_manager.config or {}).get("feishu", {}) or {}
    if feishu_cfg.get("receiver_enabled", False):
        host = feishu_cfg.get("receiver_host", "127.0.0.1")
        port = int(feishu_cfg.get("receiver_port", 8765))
        token_hint = "（已配置 Token）" if feishu_cfg.get("receiver_token") else ""
        st.caption(f"飞书接收地址: http://{host}:{port}/feishu {token_hint}")

    c_add, c_btn = st.columns([4, 1])
    with c_add:
        new_url = st.text_input("添加阅读链接（URL）", placeholder="https://...")
    with c_btn:
        if st.button("加入未读", use_container_width=True):
            if new_url and new_url.strip():
                reading_list_manager.add_url(
                    new_url.strip(),
                    source="manual",
                    default_status="unread",
                    preserve_order_if_exists=False,
                )
                st.toast("已加入未读")
                st.rerun()
            else:
                st.warning("请输入有效的 URL")

    unread_items, read_items = reading_list_manager.get_lists()

    rows = []
    for item in unread_items:
        rows.append(
            {
                "read": False,
                "title": item.title.strip() if item.title else item.url,
                "url": item.url,
                "source": item.source,
                "added_at": item.added_at,
                "id": item.id,
            }
        )
    for item in read_items:
        rows.append(
            {
                "read": True,
                "title": item.title.strip() if item.title else item.url,
                "url": item.url,
                "source": item.source,
                "added_at": item.added_at,
                "id": item.id,
            }
        )

    if not rows:
        st.info("阅读清单为空。")
        return

    df = pd.DataFrame(rows)
    df["delete"] = False
    editor_key = "workspace_reading_list_editor"
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "read": st.column_config.CheckboxColumn("已读", default=False),
            "delete": st.column_config.CheckboxColumn("删除", default=False),
            "title": st.column_config.TextColumn("标题", disabled=True),
            "url": st.column_config.LinkColumn("链接", display_text="打开"),
            "source": st.column_config.TextColumn("来源", disabled=True, width="small"),
            "added_at": st.column_config.TextColumn("添加时间", disabled=True, width="small"),
            "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        },
        disabled=["title", "source", "added_at", "id"],
        key=editor_key,
    )

    col_del, col_del_info = st.columns([1, 4])
    with col_del:
        if st.button("删除选中", type="secondary", use_container_width=True, key="reading_list_delete_btn"):
            if "delete" in edited.columns:
                # Ensure boolean type and handle NaNs
                ids = edited.loc[edited["delete"].fillna(False).astype(bool), "id"].tolist()
            else:
                ids = []
            
            ids = [str(x) for x in ids if x]
            deleted = reading_list_manager.delete_items(ids)
            if deleted > 0:
                st.toast(f"已删除 {deleted} 条")
                st.rerun()
            else:
                st.info("未选择要删除的条目")
    with col_del_info:
        st.caption("勾选“删除”后点击删除选中，可批量移除未读/已读条目。")

    changed = edited[edited["read"] != df["read"]]
    if not changed.empty:
        for _, row in changed.iterrows():
            reading_list_manager.set_read_status(row["id"], bool(row["read"]))
        st.rerun()

    st.divider()
    has_items = bool(rows)
    col_next, col_hint = st.columns([1, 4])
    with col_next:
        if st.button("下一步：新闻预览", type="primary", disabled=not has_items):
            st.session_state["workspace_step"] = "1.3 新闻预览与查看"
            st.rerun()
    with col_hint:
        if not has_items:
            st.caption("请先加入阅读清单再进行预览。")
        else:
            st.caption("勾选“已读”即会移动到已读列表；取消勾选会回到未读。")

def _render_step_preview(selected_version_path, today_content):
    st.subheader("1.3 新闻预览与查看")

    if not today_content:
        st.info("先在 1.1 生成新闻，或选择一个已有版本。")
        return

    if selected_version_path:
        st.caption(f"当前版本：{os.path.basename(selected_version_path)}")

    post = frontmatter.loads(today_content)

    st.markdown("**基于阅读清单生成预览版本**")
    unread_items, read_items = reading_list_manager.get_lists()
    c_opt, c_limit, c_btn = st.columns([2, 1, 1])
    with c_opt:
        use_unread_only = st.checkbox("仅使用未读", value=True)
    with c_limit:
        preview_max_items = st.number_input(
            "最多条数",
            min_value=1,
            max_value=30,
            value=config_manager.get("system.max_items", 20),
            label_visibility="collapsed",
        )
    with c_btn:
        if st.button("生成预览版本", type="primary", use_container_width=True):
            items = unread_items if use_unread_only else (unread_items + read_items)
            urls = [x.url for x in items if x.url]
            meta_by_url = {x.url: {"title": x.title, "image_url": x.image_url} for x in items if x.url}
            if not urls:
                st.warning("阅读清单为空，无法生成预览。")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(msg, value):
                    status_text.text(msg)
                    progress_bar.progress(value)

                result = news_generator.generate_daily_news_from_urls(
                    urls=urls,
                    meta_by_url=meta_by_url,
                    progress_callback=update_progress,
                    max_items=int(preview_max_items),
                )
                if result.startswith("ERROR:"):
                    st.error(result)
                else:
                    st.success("已生成预览版本")
                    st.session_state.pop("version_selector", None)
                    st.rerun()

    st.divider()

    st.markdown(f"**{i18n.get_text('topic_filter_header')}**")
    c_topic, c_limit = st.columns([3, 1])
    with c_topic:
        topic = st.text_input(i18n.get_text("topic_input_label"), placeholder="Tech, AI, Medical...", label_visibility="collapsed")
    with c_limit:
        filter_max_items = st.number_input(
            i18n.get_text("filter_max_items_label"),
            min_value=1,
            max_value=20,
            value=5,
            help=i18n.get_text("filter_max_items_help"),
            label_visibility="collapsed",
        )

    if st.button(i18n.get_text("generate_filtered_version_button")):
        if topic:
            with st.spinner(i18n.get_text("filtering_spinner")):
                from core.topic_filter import topic_filter
                if selected_version_path:
                    result = topic_filter.filter_and_save_version(
                        selected_version_path,
                        topic,
                        max_items=filter_max_items,
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

    col_editor, col_preview = st.columns(2)
    editor_key = f"workspace_body_{os.path.basename(selected_version_path or 'current')}"
    if editor_key not in st.session_state:
        st.session_state[editor_key] = post.content

    with col_editor:
        st.subheader(i18n.get_text("editor_header"))
        st.text_area(
            i18n.get_text("content_label"),
            value=st.session_state[editor_key],
            height=800,
            label_visibility="collapsed",
            key=editor_key,
        )
        if st.button(i18n.get_text("save_changes_button")):
            post.content = st.session_state[editor_key]
            new_file_content = frontmatter.dumps(post)
            filepath = selected_version_path
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_file_content)
            st.toast(i18n.get_text("changes_saved_toast"))
            st.rerun()

    with col_preview:
        st.subheader(i18n.get_text("live_preview_header"))
        st.markdown(st.session_state[editor_key])

    st.divider()
    col_next, col_hint = st.columns([1, 4])
    with col_next:
        if st.button("下一步：发布设置", type="primary"):
            st.session_state["workspace_step"] = "1.4 发布通知设置和格式设置"
            st.rerun()
    with col_hint:
        st.caption("确认内容无误后进入发布步骤。")

def _render_step_publish(selected_version_path, today_content):
    st.subheader("1.4 发布通知设置和格式设置")

    if not today_content:
        st.info("先在 1.1 生成新闻，或选择一个已有版本。")
        return

    post = frontmatter.loads(today_content)

    st.markdown("#### " + i18n.get_text("notifications_header"))

    current_config = config_manager.config
    webhook_url = st.text_input(
        i18n.get_text("webhook_url_label"),
        value=current_config["notification"].get("webhook_url", ""),
        placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...",
    )

    if st.button(i18n.get_text("save_config_button"), key="save_webhook"):
        new_config = current_config.copy()
        new_config["notification"]["webhook_url"] = webhook_url
        config_manager.save(new_config)
        st.success(i18n.get_text("config_saved_success"))

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

    st.subheader(i18n.get_text("smart_format_adjustment_header"))

    format_options = {
        "markdown": i18n.get_text("format_standard_markdown"),
        "news_custom": i18n.get_text("format_news"),
        "markdown_custom": i18n.get_text("format_markdown_v2"),
    }

    selected_format_key = st.radio(
        i18n.get_text("push_format_label"),
        list(format_options.keys()),
        format_func=lambda x: format_options[x],
        horizontal=True,
        key="workspace_format_key",
    )

    if selected_format_key == "markdown_custom":
        st.caption("ℹ️ Note: Markdown V2 format does not support images.")

    if selected_format_key != "markdown":
        if st.button(i18n.get_text("smart_parse_button"), type="secondary"):
            with st.spinner(i18n.get_text("parsing_spinner")):
                target_type = "news" if selected_format_key == "news_custom" else "markdown"
                parsed_result = llm_engine.convert_to_format(post.content, target_type)
                st.session_state["parsed_payload"] = parsed_result
                st.session_state["parse_counter"] += 1

        if st.session_state.get("parsed_payload"):
            col_json, col_preview_json = st.columns(2)

            with col_json:
                st.markdown(f"**{i18n.get_text('parsed_json_label')}**")
                json_str = st.text_area(
                    "JSON Payload",
                    value=json.dumps(st.session_state["parsed_payload"], indent=2, ensure_ascii=False),
                    height=400,
                    label_visibility="collapsed",
                    key=f"json_payload_{st.session_state['parse_counter']}",
                )

                try:
                    st.session_state["parsed_payload"] = json.loads(json_str)
                except json.JSONDecodeError:
                    st.error(i18n.get_text("json_parse_error"))

            with col_preview_json:
                st.markdown(f"**{i18n.get_text('preview_parsed_header')}**")
                payload = st.session_state["parsed_payload"]

                if selected_format_key == "news_custom":
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
                    md_content = payload.get("markdown_v2", {}).get("content", "")
                    st.markdown(md_content)
    else:
        if st.session_state.get("parsed_payload"):
            st.session_state["parsed_payload"] = None

    st.divider()

    col_push_btn, col_push_info = st.columns([1, 4])
    with col_push_btn:
        if st.button(i18n.get_text("confirm_push_button"), type="primary"):
            with st.spinner(i18n.get_text("pushing_spinner")):
                if selected_format_key != "markdown" and st.session_state.get("parsed_payload"):
                    success = pusher.push(st.session_state["parsed_payload"])
                else:
                    success = pusher.push(post.content)

            if success:
                st.success(i18n.get_text("push_success"))
                post.metadata["status"] = "published"
                new_file_content = frontmatter.dumps(post)
                filepath = selected_version_path
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_file_content)
                st.rerun()
            else:
                st.error(i18n.get_text("push_failed"))

def _compile_markdown_from_articles(articles_meta, title: str):
    md_body = f"# {title}\n\n"
    for i, art in enumerate(articles_meta or []):
        md_body += f"## {i+1}. {art.get('title','')}\n"
        image_url = art.get("image_url") or art.get("picurl") or ""
        if image_url:
            md_body += f"![]({image_url})\n"
        summary = art.get("summary") or ""
        if summary:
            md_body += f"> **摘要**：{summary}\n"
        original_url = art.get("original_url") or art.get("url") or ""
        if original_url:
            md_body += f"> *来源：[{art.get('source_id', 'Link')}]({original_url})*\n\n"
        else:
            md_body += "\n"
        md_body += "---\n\n"
    return md_body

def _extract_urls_from_text(text: str):
    pattern = re.compile(r"https?://[^\s<>\"]+")
    urls = pattern.findall(text or "")
    seen = set()
    result = []
    for u in urls:
        u = u.strip()
        if u and u not in seen:
            seen.add(u)
            result.append(u)
    return result

def _render_manual_tab():
    st.subheader("手动信息收集和发布")

    st.markdown("**Webhook 配置**")
    current_config = config_manager.config
    manual_webhook = st.text_input(
        i18n.get_text("manual_webhook_url_label"),
        value=current_config["notification"].get("manual_webhook_url", ""),
        placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...",
        help=i18n.get_text("manual_webhook_help"),
    )
    if st.button("保存并测试 Webhook", key="save_manual_webhook"):
        new_config = current_config.copy()
        if "notification" not in new_config:
            new_config["notification"] = {}
        new_config["notification"]["manual_webhook_url"] = manual_webhook
        config_manager.save(new_config)
        
        if manual_webhook:
            success, msg = test_webhook(manual_webhook)
            if success:
                st.success("配置已保存并测试成功！")
            else:
                st.warning(f"配置已保存，但测试失败：{msg}")
        else:
            st.success("配置已保存")

    st.divider()
    st.markdown("**添加阅读链接**")
    c_input, c_add = st.columns([4, 1])
    with c_input:
        manual_text = st.text_area("批量粘贴链接", placeholder="每行一个 URL 或直接粘贴一段包含多个 URL 的文本", height=120, label_visibility="collapsed")
    with c_add:
        if st.button("加入列表", type="primary", use_container_width=True):
            urls = _extract_urls_from_text(manual_text)
            if not urls:
                st.warning("未检测到有效 URL")
            else:
                for u in urls:
                    reading_list_manager.add_url(
                        u,
                        source="manual",
                        default_status="unread",
                        preserve_order_if_exists=True,
                    )
                st.toast(f"已加入 {len(urls)} 条链接")
                st.rerun()

    unread_items, read_items = reading_list_manager.get_lists()
    manual_items = [x for x in (unread_items + read_items) if x.source == "manual"]

    st.divider()
    st.markdown("**手动链接列表**")
    if not manual_items:
        st.info("暂无手动链接。")
        return

    rows = []
    for item in manual_items:
        rows.append(
            {
                "delete": False,
                "title": item.title.strip() if item.title else item.url,
                "url": item.url,
                "added_at": item.added_at,
                "id": item.id,
            }
        )
    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "delete": st.column_config.CheckboxColumn("删除", default=False, width="small"),
            "title": st.column_config.TextColumn("标题", disabled=True),
            "url": st.column_config.LinkColumn("链接", display_text="打开"),
            "added_at": st.column_config.TextColumn("添加时间", disabled=True, width="small"),
            "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        },
        disabled=["title", "added_at", "id"],
        key="manual_links_editor",
    )

    # 先展示"最多解析条数"，再放操作按钮，避免用户直接点击生成而忽略条数设置
    c_max_label, c_max_input = st.columns([1, 2])
    with c_max_label:
        st.caption("最多解析条数（1-30）")
    with c_max_input:
        manual_max_items = st.number_input("最多解析条数", min_value=1, max_value=30, value=10, label_visibility="collapsed")

    c_del, c_gen = st.columns([1, 1])
    with c_del:
        if st.button("删除选中", type="secondary", use_container_width=True, key="manual_list_delete_btn"):
            ids = edited.loc[edited["delete"].fillna(False).astype(bool), "id"].tolist()
            ids = [str(x) for x in ids if x]
            deleted = reading_list_manager.delete_items(ids)
            if deleted > 0:
                st.toast(f"已删除 {deleted} 条")
                st.rerun()
            else:
                st.info("未选择要删除的条目")

    with c_gen:
        if st.button("AI解析生成草稿", type="primary", use_container_width=True):
            urls = [str(x) for x in edited["url"].tolist() if x]
            meta_by_url = {}
            for item in manual_items:
                meta_by_url[item.url] = {"title": item.title, "image_url": item.image_url}
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(msg, value):
                status_text.text(msg)
                progress_bar.progress(value)

            result = news_generator.generate_daily_news_from_urls(
                urls=urls,
                meta_by_url=meta_by_url,
                generated_from="manual_tab",
                progress_callback=update_progress,
                max_items=int(manual_max_items),
            )
            if result.startswith("ERROR:"):
                st.error(result)
            else:
                latest = news_generator.get_today_versions()
                if latest:
                    st.session_state["manual_selected_version_path"] = latest[0]
                st.success("已生成草稿版本")
                st.rerun()

    st.divider()
    st.markdown("**草稿版本编辑与发布**")

    today_versions = news_generator.get_today_versions()
    manual_versions = []
    for p in today_versions:
        content = news_generator.load_news(p)
        if not content:
            continue
        try:
            post = frontmatter.loads(content)
        except Exception:
            continue
        if post.metadata.get("generated_from") == "manual_tab":
            manual_versions.append(p)

    if not manual_versions:
        st.info("尚未生成草稿版本。")
        return

    preferred = st.session_state.get("manual_selected_version_path")
    labels = []
    label_to_path = {}
    for p in manual_versions:
        fname = os.path.basename(p)
        labels.append(fname)
        label_to_path[fname] = p

    default_index = 0
    if preferred:
        preferred_name = os.path.basename(preferred)
        if preferred_name in labels:
            default_index = labels.index(preferred_name)

    selected_label = st.selectbox("选择草稿版本", options=labels, index=default_index, key="manual_version_selector")
    selected_path = label_to_path[selected_label]
    content = news_generator.load_news(selected_path)
    if not content:
        st.error("无法读取版本文件")
        return

    post = frontmatter.loads(content)
    articles_meta = post.metadata.get("articles_meta", []) or []
    if not articles_meta:
        st.warning("该版本没有可编辑条目")
        return

    art_rows = []
    for art in articles_meta:
        art_rows.append(
            {
                "delete": False,
                "id": art.get("id", ""),
                "title": art.get("title", ""),
                "summary": art.get("summary", ""),
                "image_url": art.get("image_url") or art.get("picurl") or "",
                "original_url": art.get("original_url") or art.get("url") or "",
            }
        )
    art_df = pd.DataFrame(art_rows)
    edited_articles = st.data_editor(
        art_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "delete": st.column_config.CheckboxColumn("删除", default=False, width="small"),
            "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
            "title": st.column_config.TextColumn("标题"),
            "summary": st.column_config.TextColumn("摘要（≤30字）"),
            "image_url": st.column_config.TextColumn("图片URL"),
            "original_url": st.column_config.TextColumn("原文链接"),
        },
        disabled=["id"],
        key=f"manual_articles_editor_{os.path.basename(selected_path)}",
    )

    c_save, c_status = st.columns([1, 4])
    with c_save:
        if st.button("保存条目更改", type="primary"):
            kept = edited_articles.loc[edited_articles["delete"] != True].copy()
            new_articles = []
            for _, r in kept.iterrows():
                new_articles.append(
                    {
                        "id": r.get("id", ""),
                        "source_id": "manual",
                        "original_url": r.get("original_url", ""),
                        "title": r.get("title", ""),
                        "summary": r.get("summary", ""),
                        "image_url": r.get("image_url", ""),
                        "picurl": r.get("image_url", ""),
                    }
                )
            today_str = post.metadata.get("date") or datetime.now().strftime("%Y-%m-%d")
            version_str = post.metadata.get("version") or "v1.0"
            post.metadata["articles_meta"] = new_articles
            post.content = _compile_markdown_from_articles(new_articles, f"📅 {today_str} AI Daily News ({version_str})")
            with open(selected_path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
            st.toast("已保存")
            st.rerun()
    with c_status:
        st.caption(f"当前草稿：{os.path.basename(selected_path)}")

    st.divider()
    st.markdown("**格式转换与发布**")
    format_options = {
        "markdown": "Markdown（原文）",
        "news_custom": "图文消息（news）",
        "markdown_custom": "Markdown V2（markdown_v2）",
    }
    selected_format_key = st.radio(
        "选择发布格式",
        list(format_options.keys()),
        format_func=lambda x: format_options[x],
        horizontal=True,
        key="manual_format_key",
    )

    if selected_format_key != "markdown":
        if st.button("智能转换", type="secondary", key="manual_parse_btn"):
            with st.spinner("正在转换..."):
                target_type = "news" if selected_format_key == "news_custom" else "markdown"
                parsed_result = llm_engine.convert_to_format(post.content, target_type)
                st.session_state["manual_parsed_payload"] = parsed_result

    payload = st.session_state.get("manual_parsed_payload")
    if selected_format_key != "markdown" and payload:
        st.text_area(
            "JSON Payload",
            value=json.dumps(payload, indent=2, ensure_ascii=False),
            height=260,
        )

    if st.button("发布", type="primary", key="manual_push_btn"):
        with st.spinner("正在发布..."):
            manual_webhook_url = config_manager.config["notification"].get("manual_webhook_url")
            # Fallback to global webhook if manual one is empty
            if not manual_webhook_url:
                manual_webhook_url = config_manager.config["notification"].get("webhook_url")
                
            if selected_format_key != "markdown" and payload:
                success = pusher.push(payload, webhook_url=manual_webhook_url)
            else:
                success = pusher.push(post.content, webhook_url=manual_webhook_url)
        if success:
            st.success("发布成功")
            post.metadata["status"] = "published"
            with open(selected_path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
            st.rerun()
        else:
            st.error("发布失败")

def main():
    i18n.init_language()
    render_sidebar_navigation(active="workspace")
    _init_workspace_state()
    
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

    tabs = st.tabs(["自动化信息收集与发布", "手动信息收集和发布"])
    with tabs[0]:
        today_versions = news_generator.get_today_versions()
        selected_version_path, today_content = _render_version_bar(today_versions)

        _render_step_selector()
        st.divider()

        step = st.session_state.get("workspace_step")
        if step == "1.1 数据源设置与管理":
            _render_step_sources()
        elif step == "1.2 阅读清单":
            _render_step_reading_list(selected_version_path, today_content)
        elif step == "1.3 新闻预览与查看":
            _render_step_preview(selected_version_path, today_content)
        else:
            _render_step_publish(selected_version_path, today_content)
    with tabs[1]:
        _render_manual_tab()

if __name__ == "__main__":
    main()
