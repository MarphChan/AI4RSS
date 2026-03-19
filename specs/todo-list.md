##任务列表：

### 🔴 P1 - 代码逻辑 Bug（影响功能正确性）

1. ✅ **[scheduler.py L97-107]** 定时推送内容包含 YAML frontmatter：`_job_push` 调用 `load_daily_news()` 返回原始文件内容（含 `---` frontmatter 头），直接传给 `pusher.push()` 发送 markdown，导致企业微信收到 YAML 元信息乱码。修复：先用 `frontmatter.loads()` 提取 `post.content` 再推送。

2. ✅ **[generator.py L132-137]** 图片生成功能虽在设置页面开放配置，但生成逻辑为 `pass` 占位符从未执行，用户开启"启用图片生成"无任何效果，应移除该误导性配置项或补全实现。→ 已在 Settings 中添加明确提示"该功能尚未激活"。

3. ✅ **[3_Workspace.py L183 / L417]** 错误检测用字符串前缀 `result.startswith("No")` 判断失败，若正常新闻标题包含"No"开头（如"Nobel Prize..."）会被误判为错误。应改用明确的错误标志（如异常或特定返回码）。→ generator.py 错误返回改为 `"ERROR:"` 前缀，Workspace 统一用 `startswith("ERROR:")` 判断。

4. ✅ **[3_Workspace.py L745]** 手动 tab 删除逻辑使用 `edited["delete"] == True` 而非安全类型转换，data_editor 返回 numpy.bool_ 时会导致删除失效（阅读清单 L341 已用 `.fillna(False).astype(bool)` 修复，manual tab 未同步修复）。→ 已同步修复。

5. ✅ **[3_Workspace.py L421]** 生成预览版本后执行 `del st.session_state["version_selector"]`，若版本选择器 Widget 从未渲染（空版本列表场景），会抛出 KeyError 崩溃。应改用 `st.session_state.pop("version_selector", None)`。→ 已修复。

6. ✅ **[generator.py L260-264 / L394-399]** Markdown 编译时 `art['source_id']`、`art['original_url']`、`art['summary']` 若为 None，会输出字符串 `"None"` 进入文档。应加 `or ''` 兜底处理。→ 已修复两处编译逻辑。

7. ✅ **[config_manager.py L68]** `_merge_defaults` 逻辑：当 config.yaml 中 list 字段为空时 `continue` 跳过，导致用户清空 `default_images` 列表后仍被默认值覆盖，无法真正清空。应将空 list 视为有效值进行合并。→ 已移除 elif 空列表跳过逻辑。

8. ✅ **[3_Workspace.py L233-249]** 数据源启用开关：`st.toast("已保存")` 之后立即 `st.rerun()`，用户永远看不到 toast 反馈。应将 rerun 放在下一个条件分支或使用 `time.sleep(0.3)` 短暂延迟（或改为仅在有实际变更时才 rerun）。→ 改用 session_state flag，rerun 后再显示 toast。

9. ✅ **[2_Sources.py L315-317]** 批量测试抓取按钮将所有被测数据源在内存中强制设为 `s['enabled'] = True`，会影响后续来自 `sources` 列表的读取逻辑，且不会还原。应使用临时副本而非修改原始对象。→ 已改为 `dict(s, enabled=True)` 浅拷贝。

---

### 🟡 P2 - 使用体验问题（影响操作流畅度）

10. ✅ **[3_Workspace.py L91]** 删除版本文件（🗑️ 按钮）无确认弹窗，单击即不可撤销删除。应增加 `st.dialog` 或二次确认机制。→ 已实现基于 session_state 的两步确认：点击后显示"⚠️确认"和"取消"按钮。

11. ✅ **[3_Workspace.py L366-368]** "下一步：新闻预览"按钮在阅读清单为空时仍可点击，跳转后展示空白步骤，用户体验差。应在阅读清单为空时禁用或提示该按钮。→ 已加 `disabled=not has_items` 及提示文字。

12. ✅ **[3_Workspace.py L488]** 内容编辑器预览使用 `unsafe_allow_html=True`，若新闻内容来自外部 URL 含恶意 HTML/JS，存在 XSS 风险。应移除该参数或对内容进行 HTML 转义。→ 已移除 `unsafe_allow_html=True`。

13. ✅ **[2_Sources.py L132-155]** `batch_candidates` 在 session_state 中跨模式持久化，用户从"解析文本"切换到"按主题搜索"后，仍显示旧结果。每次切换模式或点击搜索/分析按钮时应清除旧候选列表。→ 已在模式切换时自动清理 `batch_candidates`。

14. ✅ **[1_Settings.py L161-191]** 飞书接入配置区域的所有标签（"启用本地接收服务"、"监听地址"、"端口"、"Token"等）均为硬编码中文，未接入 i18n 系统，切换英文界面后该区域标签不变。→ 已在 i18n.py 新增飞书相关 key，Settings 改用 `i18n.get_text()` 调用。

15. ✅ **[3_Workspace.py L757 / L761]** 手动 tab 中"最多解析条数"数字输入框位置在"AI解析生成草稿"按钮旁边但视觉上不够突出，用户容易忽略该参数直接点击生成，建议调整布局或增加说明文字。→ 已将"最多解析条数"提到按钮行之前单独显示。

16. ✅ **[3_Workspace.py L281]** 手动添加阅读链接后 `st.session_state["workspace_step"] = "1.2 阅读清单"` 是多余赋值（当前已在该步骤），可直接 `st.rerun()` 即可，无实际影响但代码冗余。→ 已移除冗余赋值。

---

### 🟢 P3 - 性能与代码质量

17. ✅ **[fetcher.py L85-86]** 每个无图片的 RSS 条目都额外发起独立 HTTP 请求获取页面图片（N+1 请求），20 条 RSS 最多触发 20 次额外请求，显著拖慢抓取速度。建议将此行为改为可选（默认关闭），或在 `fetch_all` 并发中合并处理。→ 已通过 `system.fetch_article_images`（默认 False）配置控制，用户可在 config.yaml 手动开启。

18. ⏭️ **[deduplicator.py L43-49]** 标题相似度去重使用 O(n²) 算法（每条与所有已见标题比对），数据量大时性能急剧下降。→ 当前 max_items 上限 30，实际影响可忽略，暂不优化。

19. ⏭️ **[reading_list_manager.py L224-232]** `update_from_drag_labels` 方法定义但在整个 UI 层从未被调用（拖拽功能未实现），属于死代码，建议清理。→ 该方法有测试覆盖（tests/ 中使用），保留待拖拽功能实现时使用。

20. ✅ **[llm_base.py L44]** API key 为空时跳过初始化但无用户提示，直到调用时才以隐晦错误失败。应在 `_init_clients` 中当 key 为空时记录更友好的警告日志，提示用户在设置页配置。→ 已改为带有 provider 名称和指引的 warning 日志。

##已完成任务：
1. 【已完成】手动信息收集和发布前，也需要配置webhook链接，且链接需要缓存
2. 【已完成】在系统配置中增加默认图片URL链接配置，当新闻没有图片url时，使用默认图片url，支持设置多个默认url，每次使用按顺序使用，直到使用完所有默认url
2. 【已完成】markdown-V2格式不需要支持展示图片，这个功能在llm.py中
2. 【已完成】拆分llm.py，将不同的功能拆分到不同的.py程序中，不要写在一个文件中，并做好注释和命名，每个.py程序的功能要清晰，存放路径 /Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/core
3. 【已完成】将整个前端页面做调整，参考/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/todo-list.md 文档
4. 【已完成】增加更多的LLM提供商支持，例如DeepSeek, Claude等，并在设置页面中支持选择
2. 【已完成】在这个话题筛选中，需要补充提示词，相关性排序，需要考虑行业影响力、公司知名度、事件影响范围、和关键词的相关性等角度综合判断，话题筛选的代码： /Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/core/topic_filter.py
2. 【已完成】增加测试抓取功能，支持多选筛选或测试数据源
2. 【已完成】增加AI自动寻找RSS数据源的功能，支持用户输入关键主题，AI搜索RSS数据源，并进行自动化数据源链接性测试，可以接通获取数据才回进入备选RSS列表
3. 【已完成】为每一个数据源增加logo，logo的url存储列表中，每次生成发布的图文格式时，从数据库中获取logo的url作为图片信息
4. 【已完成】在获取新闻后，通过新闻链接获取这个新闻第一个配图，然后获取这个配图的url，作为"picurl": ""获取和存储
2. 【已完成】 限制处理数量（推荐） ：生成筛选版本时，增加一个筛选框，支持输入最多新闻条数，让AI根据主题匹配度、 新闻重要程度，做判断和筛选，这里主要调整的功能应该在/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/core/topic_filter.py，你可以doublecheck一下
3. 【已完成】 限制处理数量（推荐） ：在配置或代码中增加 max_items 限制（每次只处理最新的 20 条），避免一次性处理数百条新闻。把这个限制作为生成前的设置信息，支持设置1-30
3. 【已完成】 改为并行处理 ：修改 generator.py ，使用多线程并发调用 LLM 进行总结，大幅提高生成速度
4. 【已完成】增加生成内容的内容去重功能 ：在生成的新闻中，增加去重功能，避免重复新闻的出现，用一个新的py文件实现这个功能，py文件的路径为/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/core ，名称要表达功能的含义
5. 【已完成】增加输入框，在生成后，增加按钮和输入框，支持用户设置关注的领域（例如：科技、金融、医疗等），并根据用户设置，在生成的新闻提取，只包含用户关注的领域的新闻，形成一个新的版本，叫Va.X，其中X不断变化，V1.0为初始版本，每次生成后，X加1。这个功能通过大语言模型实现。用一个新的py文件实现这个功能，py文件的路径为/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/core ，名称要表达功能的含义
6. 【已完成】在默认配置中预置 ai_news.svg 作为无图回退，并在生成时兜底使用
7. 【已完成】将目前的收集结果呈现为列表，并将每条新闻做成 todo list 的形式，默认在【未阅读】区域，用户可以拖拽到【已阅读】区域
8. 【已完成】增加一个能力，支持手机将阅读链接通过飞书转发给此应用，并增加在【未阅读】区域
9. 【已完成】将 workspace 重构为 4 步子页面流程：数据源管理→阅读清单(checkbox)→新闻预览→发布设置
10. 【已完成】todo-workspace 中的数据源管理仅支持按“数据源类型”筛选；不支持新增/删除；默认【tech】并缓存上次选择
11. 【已完成】todo-workspace 的阅读清单包含：上一次根据数据源搜索到的信息 + 用户通过飞书传来的数据（未选择版本时也展示历史）
12. 【已完成】todo-workspace 的 4 步流程使用面包屑式导航展示与跳转
13. 【已完成】todo-支持多选删除阅读清单的内容
14. 【已完成】管理源和批量删除选中源在一个列表交互即可
15. 【已完成】管理源中无法调整网站的类型，调整后恢复初始值
16. 【已完成】调整管理源中的类型，每调整两次列表就会刷新位置，导致无法定位正在查看的网址
17. 【已完成】每次生成【新闻预览】均需要按照上一页的【阅读清单】来生成
18. 【已完成】将目前已有的功能整理到一个tab中，这个tab叫-【自动化信息收集与发布】
19. 【已完成】新增一个和自动化相关的tab，叫-【手动信息收集和发布】，这里面有几个核心功能：a.支持手动添加阅读链接 b. AI根据链接解析列表中的所有文章url、文章标题、内容总结（30字以内）、首图url等信息 c. 支持手动编辑标题、内容、图片等信息 d. 支持自动化转化格式【markdown-V2】和【图文格式】，功能和core/llm_format.py 相同，复用 e. 支持手动和自动化发布文章。以上功能如果与/core 中的功能相似，请复用 
20. 【已完成】左侧tab栏也根据用户设置的中文/英文 切换语言显示

##你的工作：
1. 得到todo之后，先根据todo的内容，判断是增加功能还是修改功能，并在/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/PRD.md 中基于todo更新PRD
2. /Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/IMPLEMENTATION_PLAN.md 中基于todo更新实现计划
3. /Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/FRONTEND_GUIDELINES.md中基于todo更新前端设计，需要基于/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/frontend-design.md 来做前端设计
4. 具体开发工作需要基于/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs中的所有文档指导来进行
5. 每次执行一条 ##任务列表 中未完成的任务，并在任务完成时，对这个任务标记已完成，移动到 ##已完成任务 列表中
6. 修改代码后，需要进行单元测试，如果没有通过单元测试，则需要调整优化代码
7. 在 specs 的各个文档中同步需求变更，确保所有文档都能及时更新
8. 完成上一条任务执行后，需要继续执行任务，直到所有任务都标记【已完成】
9. 需要特别关注/Volumes/KIOXIA-1T-Marph/claude's code/AI_RSS/specs/lessons.md 中记录的过去的错误，需要严格避免
