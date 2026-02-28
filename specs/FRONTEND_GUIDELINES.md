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
- **Left Column:** `st.text_area`
  - Label: "Edit Markdown Content"
  - Height: `600px` minimum.
  - Value: Loaded from `data/YYYY-MM-DD-vX.0.md` (content body).
- **Right Column:** `st.markdown`
  - Content: Rendered markdown from the left column.
  - Images: Should render correctly if URLs are valid.

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
