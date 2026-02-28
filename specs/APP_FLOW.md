# Application Flow (User Journeys)

## 1. Onboarding & Configuration (First Run)
**Goal:** Initialize the system with necessary keys and schedules.

1. **Start App:** User runs `streamlit run app.py`.
2. **Landing:** User lands on `Settings` page (if config is missing/empty).
3. **Configure LLM:**
   - User selects `Provider` (e.g., DashScope).
   - User enters `API Key`.
   - User inputs `Model Name` (e.g., qwen-max).
4.12→4. **Configure Schedule:**
13→   - User sets `Fetch Time` (e.g., 08:00).
14→   - User sets `Push Time` (e.g., 09:30).
15→   - User selects `Fetch Time Period` (e.g., 24h, 3 days, 7 days, Custom).
16→5. **Configure Notifications:**
   - User enters `WeCom Webhook URL`.
   - User clicks `Test Connection`.
   - **System:** Sends a "Hello World" to the webhook.
   - **Feedback:** "Success" toast or "Error" message.
6. **Save:**
   - User clicks `Save Configuration`.
   - **System:** Writes to `config.yaml`.
   - **Feedback:** "Configuration saved successfully."

## 2. Managing Data Sources
**Goal:** Define where the news comes from.

1. **Navigation:** User clicks `Source Manager` in sidebar.
2. **Add New Source:**
   - User enters `Name` (e.g., "TechCrunch").
   - User selects `Type` (RSS / Web).
   - User enters `URL`.
   - User clicks `Add`.
   - **System:** Appends to `sources.json`.
   - **Feedback:** Table refreshes, showing new source.
   - **Group Management:** User can assign a group (e.g., "Tech", "Finance") to each source for organized fetching.

3. **Manage Existing:**
   - User toggles `Enabled` switch to pause a source.
   - User clicks `Delete` icon to remove a source.
   - **Batch Delete:** User selects multiple rows and clicks `Delete Selected`.
   - User edits `Group` column to reorganize sources.
   - User clicks `Test Fetch` on a specific row.
   - **System:** Fetches the URL immediately and shows the raw title/content found (limited to first item).
   - **Feedback:** Modal/Expander shows "Found: [Article Title]" or "Error: Timeout".

4. **Batch Import (New Feature):**
   - User clicks `Batch Import` tab/button.
   - User pastes a list of URLs or unstructured text containing RSS feeds.
   - User clicks `Analyze with AI`.
   - **System:** Sends text to LLM to extract potential RSS feeds (Name, URL).
   - **System:** Displays a candidate list with checkboxes.
   - User selects desired feeds, assigns a target Group, and clicks `Import Selected`.
   - **System:** Appends valid entries to `sources.json`.
   - **Feedback:** "Successfully imported X sources."

## 3. Daily Workflow (The "Workspace")
**Goal:** Generate, Review, and Push the daily news.

1. **Navigation:** User clicks `Workspace` in sidebar.
2. **View Status:**
   - System displays "Last run: [Time]" or "No data for today".
3. **Trigger Generation:**
   - User selects target Groups (optional, default: All Enabled).
   - User clicks `Start Generation`.
   - **System:**
67→     - Shows progress bar.
68→     - Fetches enabled sources matching selected groups (parallel).
69→     - Filters based on configured time period (default 24h).
70→     - Calls LLM for summarization.
     - Generates images (optional).
     - Writes `data/YYYY-MM-DD-vX.0.md` (incrementing version if file exists for today).
   - **Feedback:** Page reloads with the generated content.
4. **Review & Edit:**
   - User sees split view: `Editor` (Left) vs `Preview` (Right).
   - User edits text in Markdown editor (fixes typos, removes irrelevant items).
   - Preview updates in real-time.
5. **Refine Images (Optional):**
   - User is unhappy with an image.
   - User clicks `Regenerate Image` button under a specific news item (if implemented as component) OR modifies the image URL/Prompt in the markdown frontmatter (advanced) - *Simplified for MVP: User just deletes the image line if bad.*
6. **Smart Format Adjustment (New Feature):**
   - User selects push format: `Markdown` or `News`.
   - User clicks `Smart Parse Format`.
   - **System:** Uses LLM to convert the current markdown content into the target format structure (JSON).
   - **System:** Displays the parsed result (JSON editor or form).
   - User reviews and adjusts the parsed content.

7. **Push:**
   - User clicks `Confirm & Push`.
   - **System:**
     - Reads final parsed content (JSON payload).
     - Sends POST request to WeCom Webhook.
     - Updates `status` in Front Matter to `published`.
   - **Feedback:** "News pushed to Enterprise WeChat!"

## 4. Background Automation
**Goal:** Run tasks without user intervention (as long as app is running).

1. **Scheduler Loop:**
   - App starts a background thread on launch.
   - Checks system time every minute.
2. **Auto-Fetch:**
   - If time == `cron_schedule`:
     - Triggers `Generation` workflow (same as step 3.3 but headless).
     - Saves `data/YYYY-MM-DD-vX.0.md` with status `pending_review`.
3. **Auto-Push:**
   - If time == `push_time` AND `data/YYYY-MM-DD-vX.0.md` (latest version) exists AND status == `pending_review`:
     - **Constraint:** Ideally, we want a human review.
     - **Decision:** For MVP, if `Auto-Push` is enabled in config, it pushes. If not, it waits.
     - *Correction based on PRD:* "User completes 'Configure -> Fetch -> Edit -> Push'". The "Auto-Push" in PRD suggests fully automated mode is possible, but the "Workspace" implies manual review.
     - *Refined Logic:* Auto-fetch creates the draft. Auto-push sends it ONLY IF user has reviewed (status=published) OR if a "Fully Automated" toggle is set.
     - *Default Behavior:* Auto-fetch creates draft. User gets notification (if possible) or just checks app. User manually pushes. (To keep MVP simple).
