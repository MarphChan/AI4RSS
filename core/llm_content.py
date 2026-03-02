import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ContentMixin:
    def summarize(self, content: str) -> Dict:
        """
        Summarize article content into title, summary (30 words), and image prompt.
        """
        system_prompt = """
你是一个专业的 AI 科技新闻编辑。你的任务是阅读给定的新闻内容，并将其总结为中文。

必须遵守的规则：
1. 标题：必须翻译成中文，简练吸引人，不超过 20 个字。
2. 摘要：必须是中文，直击要点。严格限制在 30 个字以内。不要使用“本文介绍了”、“这篇文章说”等废话，直接陈述事实。
3. 格式：直接返回 JSON 格式，不要包含 Markdown 代码块标记。

JSON 结构：
{
  "title": "中文标题",
  "summary": "30字以内的中文摘要",
  "image_prompt": "一段英文的绘画提示词，描述新闻核心画面，风格为扁平化科技插画"
}
"""
        user_prompt = f"""
请分析以下内容：
[内容开始]
{content[:5000]} 
[内容结束]

请提取并返回 JSON 数据。
"""
        try:
            # Use unified generate_response with JSON mode
            result = self.generate_response(system_prompt, user_prompt, json_mode=True)
            if not result:
                raise Exception("Empty response from LLM")
            return json.loads(result)
        except Exception as e:
            logger.error(f"LLM Summarization Error: {e}")
            return {
                "title": "Summary Failed", 
                "summary": "AI generation failed. Please check logs.", 
                "image_prompt": ""
            }
