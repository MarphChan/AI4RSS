import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DiscoveryMixin:
    def discover_links(self, html_content: str, current_timestamp: str) -> List[Dict]:
        """
        Extract news links from raw HTML.
        """
        system_prompt = """
你是一个爬虫辅助助手。你的任务是从杂乱的 HTML 文本中提取出过去 24 小时内发布的文章链接。

要求：
1. 仅提取“发布时间”在当前时间前 24 小时内的文章。
2. 如果 HTML 中没有明确时间，但标题包含“Today”、“今天”或“刚刚”，也算作有效。
3. 返回结果必须是 JSON 格式列表：
[
  {"title": "文章标题", "url": "完整URL", "date_str": "原文中的时间字符串"}
]
如果找不到任何符合条件的文章，返回空列表 []。
"""
        user_prompt = f"""
当前系统时间：{current_timestamp}

请分析以下 HTML 内容：
[HTML开始]
{html_content[:15000]}
[HTML结束]
"""
        try:
            result = self.generate_response(system_prompt, user_prompt, json_mode=True)
            if not result:
                return []
            # Handle potential wrapper keys if LLM wraps list in object
            data = json.loads(result)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try to find the list inside
                for key, val in data.items():
                    if isinstance(val, list):
                        return val
            return []
        except Exception as e:
            logger.error(f"LLM Discovery Error: {e}")
            return []

    def parse_rss_sources(self, content: str) -> List[Dict]:
        """
        Extract RSS/Web sources from unstructured text.
        Returns a list of dicts: [{"name": "...", "url": "...", "type": "rss"}]
        """
        system_prompt = """
        你是一个辅助用户整理 RSS 订阅源的助手。
        用户的输入可能是一段包含多个 RSS 地址的文本，或者是通过 Markdown/HTML 格式列出的博客列表。
        你的任务是提取出所有有效的 RSS 订阅源信息。
        
        要求：
        1. 识别文本中的 网站名称 (Name) 和 订阅地址 (URL)。
        2. 如果只有 URL，尝试从 URL 中推断名称。
        3. 默认类型 (type) 均为 "rss"，除非明确标注是社交媒体 (social) 或需要网页抓取 (web_crawl)。
        4. 返回 JSON 列表格式：
        [
          {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss"},
          {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "rss"}
        ]
        5. 如果找不到任何源，返回空列表 []。
        """
        user_prompt = f"""
        请分析以下文本，提取 RSS 源：
        [文本开始]
        {content[:10000]}
        [文本结束]
        """
        try:
            result = self.generate_response(system_prompt, user_prompt, json_mode=True)
            if not result:
                return []
            data = json.loads(result)
            
            # Handle wrapper
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        return val
            return []
        except Exception as e:
            logger.error(f"LLM RSS Parsing Error: {e}")
            return []

    def find_rss_sources(self, topic: str) -> List[Dict]:
        """
        Find RSS sources for a given topic.
        """
        system_prompt = """
        你是一个专业的 RSS 源推荐助手。用户会提供一个感兴趣的主题（如“人工智能”、“金融”等），你的任务是推荐相关的、高质量的 RSS 订阅源。

        要求：
        1. 推荐 5-10 个相关的 RSS 源。
        2. 优先推荐知名、更新活跃的源。
        3. 返回 JSON 列表格式：
        [
          {"name": "源名称", "url": "RSS地址", "type": "rss"},
          {"name": "源名称", "url": "RSS地址", "type": "rss"}
        ]
        4. 确保 URL 是有效的 RSS/Atom feed 地址（以 .xml, /feed, /rss 等结尾）。
        5. 如果不确定 URL，可以提供网站主页，将 type 设为 "web_crawl"。
        """
        user_prompt = f"请推荐关于“{topic}”的 RSS 订阅源。"
        
        try:
            result = self.generate_response(system_prompt, user_prompt, json_mode=True)
            if not result:
                return []
            data = json.loads(result)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        return val
            return []
        except Exception as e:
            logger.error(f"LLM RSS Discovery Error: {e}")
            return []
