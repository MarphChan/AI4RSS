##BUG列表：

##已解决任务：
- [x] **[scheduler.py]** 定时推送直接发送含 YAML frontmatter 的原始文件内容，导致企业微信收到乱码（修复：用 frontmatter.loads 提取 post.content 后再推送）
- [x] **[generator.py]** 错误返回值用 `"No"` 前缀，与正常内容无法可靠区分（修复：改为 `"ERROR:"` 前缀，前端用 startswith("ERROR:") 判断）
- [x] **[generator.py]** Markdown 编译时文章字段为 None 会输出字符串 `"None"`（修复：全部加 `or ''` 兜底）
- [x] **[config_manager.py]** `_merge_defaults` 空列表被跳过合并，用户无法清空 default_images（修复：移除特殊 elif 分支）
- [x] **[3_Workspace.py]** `del st.session_state["version_selector"]` 可能 KeyError（修复：改为 .pop()）
- [x] **[3_Workspace.py]** 数据源启用开关 toast 被 rerun 覆盖用户看不到（修复：用 session_state flag 延迟显示）
- [x] **[3_Workspace.py]** manual tab 删除用 == True 类型不安全（修复：.fillna(False).astype(bool)）
- [x] **[3_Workspace.py]** 版本删除无确认弹窗（修复：两步确认按钮）
- [x] **[3_Workspace.py]** 阅读清单为空时"下一步"仍可点击（修复：disabled=not has_items）
- [x] **[3_Workspace.py]** unsafe_allow_html=True XSS 风险（修复：移除该参数）
- [x] **[3_Workspace.py]** 手动添加 URL 后冗余 step 赋值（修复：移除）
- [x] **[2_Sources.py]** 批量测试直接修改原始 source 对象（修复：使用 dict 浅拷贝）
- [x] **[2_Sources.py]** batch_candidates 跨模式持久不清理（修复：检测模式切换后自动清理）
- [x] **[1_Settings.py / i18n.py]** 飞书配置区硬编码中文未接入 i18n（修复：新增 i18n key，Settings 改用 get_text）
- [x] **[fetcher.py]** N+1 额外 HTTP 请求拖慢 RSS 抓取（修复：改为 system.fetch_article_images 配置控制，默认 False）
- [x] **[llm_base.py]** API key 为空静默失败（修复：warning 日志增加 provider 名称和指引）
- [x] **[generator.py / 1_Settings.py]** 图片生成 pass 占位符无效果但设置页面未提示（修复：Settings 添加 help 说明）
- [x] **[generator.py L224/L364]** NameError 潜在崩溃 (原因：`article_meta` 赋值在 try 块内，异常时未定义；修复：在 try 块外预初始化 `article_meta = None`)
- [x] **[generator.py L244/L379]** 裸 `except:` 子句 (原因：捕获 BaseException 包括 SystemExit/KeyboardInterrupt；修复：改为 `except Exception:`)
- [x] **[fetcher.py L75]** RSS 无日期条目 fallback 为 `datetime.now()` (原因：旧文章被视为最新内容；修复：无日期条目直接 `continue` 跳过)
- [x] **[fetcher.py L34]** `fetch_all()` 未使用 `as_completed` (原因：按提交顺序阻塞，削弱并发；修复：改为 `for future in as_completed(futures)`，并补充 import)
- [x] **[config_manager.py L47]** `_load_config` 返回 `DEFAULT_CONFIG` 引用 (原因：直接返回类变量引用，后续修改污染默认值；修复：改为 `copy.deepcopy(self.DEFAULT_CONFIG)`，补充 `import copy`)
- [x] 阅读清单删除不work，请定位原因，找出问题并修复 (原因：Streamlit data_editor 返回的 DataFrame 可能包含 NaN 或混合类型，导致布尔筛选失败。已增强筛选逻辑，使用 fillna(False).astype(bool) 确保类型安全)
- [x] 修改数据源时报错，错误提示见下方粘贴，什么原因，应该怎么解决 (原因：Streamlit data_editor 返回 numpy 类型数据(如 bool_)，JSON 序列化时不支持。已在 SourceManager 中添加数据清洗逻辑，自动将 numpy 类型转换为 Python 原生类型)
- [x] 7. 阅读清单有多条信息，但是生成的预览只有2条新闻，什么原因，怎么解决 (原因：由于网络超时或反爬虫导致部分 URL 获取失败，原逻辑静默跳过了失败项，现已在预览中增加失败 URL 列表提示)
- [x] 6. 在阅读清单页报错，请检查，并解决，To fix this error, please pass a unique key argument to st.button.![alt text](image-4.png) (原因：多个页面存在同名 "删除选中" 按钮且未指定 unique key，导致 Streamlit 渲染冲突)
- [x] 5. 定时发布的任务没有成功，服务是在线的，什么原因，怎么解决 (原因：调度器每分钟无条件刷新导致任务被重置跳过)
- [x] 4. 智能解析格式、总结概要等和AI相关的功能都不work，原因是 Base URL 配置在 Provider 为 openai 时被忽略，且配置修改后 LLM 引擎未热重载
- [x] 1. 左侧栏图标显示异常，有两个icon，去掉1个icon
- [x] 2. 解析微信公众号文章，报错：No content fetched from provided URLs.
- [x] 3. 获取数据源报错，什么原因，怎么解决 (原因：sources.json 包含非法的 NaN 值)


#你的工作
1. 从##bug列表中，选择未解决的任务解决，直到bug完全被解决，通过测试，并将已经解决的任务标注为已解决，移动到##已解决任务，格式为：`- [x] 任务描述`
1. 记录本次错误和原因到specs/lessons.md，格式参考文档中现有的格式内容，未来需要严格避免
