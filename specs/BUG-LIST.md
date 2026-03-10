##BUG列表：

##已解决任务：
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
