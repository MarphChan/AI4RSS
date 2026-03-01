# Frontend Guidelines (Streamlit Specifics)

## 1. Design Philosophy
- **Zero-Config UI:** Streamlit handles most layout.
- **Minimalist:** Clean, single-purpose pages.
- **Information Density:** High density for sources list, moderate for settings, distraction-free for workspace.
- **Consistency:** Use Streamlit's native components for all interactions. No custom HTML/CSS unless absolutely necessary (e.g., specific image styling).

## 2. Layout & Structure
### 2.1 Global Settings (`st.set_page_config`)
- **Title:** "AI Daily News Assistant"
- **Layout:** "wide" (Crucial for the split-screen editor)
- **Initial Sidebar State:** "expanded"
- **Icon:** "📰"

### 2.2 Navigation (Sidebar)
- Use `st.sidebar` for navigation between pages.
- **Items:**
  1. ⚙️ Settings (System configuration)
  2. 📡 Sources (Manage feeds)
  3. 📝 Workspace (Daily operations)
- **Status Indicator:** Place a small status area at the bottom of the sidebar showing "Last run: [Time]" and "Next run: [Time]".

## 3. Component Standards

### 3.1 Input Fields
- **API Keys:** Always use `st.text_input(..., type="password")` to mask input.
- **URLs:** Use `st.text_input` with placeholder examples (e.g., `https://example.com/rss.xml`).
- **Time Selection:** Use `st.time_input` for scheduling.

### 3.2 Action Buttons
- **Primary Actions:** Place at the top or bottom of forms (e.g., "Save Configuration", "Start Generation").
- **Destructive Actions:** Use `st.error` or `st.warning` confirmation dialogs if possible (Streamlit's `st.popover` or simple confirmation check).
- **Feedback:** Always use `st.success("Message")`, `st.error("Error")`, or `st.toast("Notification")` after an action.

### 3.3 Data Display
- **Source List:** Use `st.dataframe` or `st.data_editor` for editable tables.
  - Columns: Name, Type, URL, Status (Checkbox), Last Fetched.
  - Configuration: `use_container_width=True`, hide index.

### 3.4 The Workspace Editor
- Workspace 使用 4 步子页面组织内容，顶部提供步骤切换（segmented control / tabs）与 Next/Back。
- Step 1.1 数据源管理仅做“类型筛选 + 启用/禁用 + 生成触发”，不在此处提供新增/删除；类型默认 tech 且记住上次选择。
- Step 1.3 内提供编辑器双列布局：
  - **Left Column:** `st.text_area`（编辑 Markdown body）
  - **Right Column:** `st.markdown`（实时预览）

### 3.5 Reading List (Unread/Read)
- Step 1.2 提供“阅读清单”区块，来源包括生成条目与外部链接。
- 每条阅读项前使用 checkbox 标记已读；勾选后移动到已读列表。
- 保留拖拽能力用于排序（可选），但“已读/未读”判断以 checkbox 为准。
- 提供多选删除能力：用户勾选“待删除”后点击删除按钮批量移除条目。

## 4. Typography & Styling (Markdown)
- **Headers:**
  - H1 (`# Title`): Page titles only.
  - H2 (`## Section`): Major sections within a page.
  - H3 (`### Subsection`): Detailed groupings.
- **Blockquotes:** Used for AI summaries (`> Summary...`).
- **Lists:** Standard bullet points (`* Item`) or numbered lists.
- **Images:** `![]()` syntax. Ensure images are responsive (Streamlit handles this by default).

## 5. Mobile Responsiveness
- Streamlit is responsive by default.
- **Constraint:** The "Workspace" split view might stack vertically on mobile. This is acceptable for MVP.
- **Recommendation:** Use `st.columns` with caution on mobile; ensure critical content is visible without horizontal scrolling.
