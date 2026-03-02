import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class FormatMixin:
    def convert_to_format(self, content: str, format_type: str) -> Dict:
        """
        Convert markdown content to a specific JSON payload format for WeCom.
        format_type: 'news' or 'markdown'
        """
        if format_type == "news":
            system_prompt = """
你是一个企业微信消息格式转换助手。
请将给定的 Markdown 新闻内容转换为企业微信 Webhook 的【图文消息】(news) JSON 格式。

输出必须严格遵守以下 JSON 结构：
{
    "msgtype": "news",
    "news": {
       "articles" : [
           {
               "title" : "新闻标题",
               "description" : "简短的新闻摘要或描述",
               "url" : "文章链接（如果没有具体链接，可填官网或留空）",
               "picurl" : "图片链接（如果有图片，提取第一张；如果没有，留空或填默认图）"
           }
        ]
    }
}
注意：
1. 如果有多条新闻，请在 articles 数组中生成多个对象（最多 8 条）。
2. 请从原文中提取最匹配的信息填充字段。
3. 仅返回 JSON，不要包含 Markdown 代码块标记。
"""
        elif format_type == "markdown":
            system_prompt = """
            你是一个企业微信消息格式转换助手。
            请将给定的 Markdown 新闻内容转换为企业微信 Webhook 的【Markdown】 JSON 格式。
            用户特别要求使用 `markdown_v2` 结构（以此为准）。
            
            输出必须严格遵守以下 JSON 结构：
            {
                "msgtype": "markdown_v2",
                "markdown_v2": {
                    "content": "这里是经过优化的 Markdown 内容字符串。请保留原文的标题、列表、引用等格式，并确保在企业微信中显示美观。"
                }
            }
            注意：
            1. content 字段的值必须是转义后的 Markdown 字符串。
            2. 仅返回 JSON，不要包含 Markdown 代码块标记。
            3. markdown_v2 格式不支持图片，请移除所有图片链接。
            """
        else:
            return {}

        user_prompt = f"""
请转换以下内容：
[内容开始]
{content[:10000]}
[内容结束]
"""
        try:
            result = self.generate_response(system_prompt, user_prompt, json_mode=True)
            if not result:
                return {}
            return json.loads(result)
        except Exception as e:
            logger.error(f"LLM Format Conversion Error: {e}")
            return {}
