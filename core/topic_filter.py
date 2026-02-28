import frontmatter
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from core.llm import llm_engine
from core.generator import news_generator

logger = logging.getLogger(__name__)

class TopicFilter:
    def __init__(self):
        pass

    def filter_and_save_version(self, source_filepath: str, topic: str, max_items: int = 5) -> Optional[str]:
        """
        Filter articles from a source file by topic and save as a new version.
        Returns the new filepath if successful, or an error message string (starting with "Error" or "No").
        """
        # 1. Load content
        content = news_generator.load_news(source_filepath)
        if not content:
            return "Error: Could not load source file."
            
        post = frontmatter.loads(content)
        articles = post.metadata.get('articles_meta', [])
        
        if not articles:
            return "Error: No articles found in source file."

        # 2. Filter using LLM
        selected_ids = self._get_relevant_article_ids(articles, topic, max_items)
        
        if not selected_ids:
            return "No relevant articles found for this topic."

        # 3. Create new content
        filtered_articles = [a for a in articles if a['id'] in selected_ids]
        
        # New Front Matter
        new_metadata = post.metadata.copy()
        original_version = new_metadata.get('version', 'v1.0')
        
        # Determine new version number
        # Increment minor version: v1.0 -> v1.1
        try:
            v_num = float(original_version.replace('v', ''))
            new_v_num = round(v_num + 0.1, 1)
            new_version = f"v{new_v_num}"
        except:
            new_version = "v1.1"
            
        new_metadata['version'] = new_version
        new_metadata['topic_filter'] = topic
        new_metadata['articles_meta'] = filtered_articles
        new_metadata['status'] = 'pending_review' # Reset status
        
        # New Markdown Body
        today_str = datetime.now().strftime("%Y-%m-%d")
        md_body = f"# 📅 {today_str} AI Daily News ({new_version}) - {topic}\n\n"
        
        for i, art in enumerate(filtered_articles):
            md_body += f"## {i+1}. {art['title']}\n"
            if art.get('image_url'):
                md_body += f"![]({art['image_url']})\n"
            md_body += f"> **摘要**：{art['summary']}\n"
            md_body += f"> *来源：[{art.get('source_id', 'Link')}]({art.get('original_url')})*\n\n"
            md_body += "---\n\n"
            
        # 4. Save
        new_post = frontmatter.Post(md_body, **new_metadata)
        final_content = frontmatter.dumps(new_post)
        
        # Construct new filepath
        dirname = os.path.dirname(source_filepath)
        filename = os.path.basename(source_filepath)
        # 2024-02-28-v1.0.md -> 2024-02-28-v1.1.md
        parts = filename.split('-v')
        base_name = parts[0]
        new_filename = f"{base_name}-{new_version}.md"
        new_filepath = os.path.join(dirname, new_filename)
        
        with open(new_filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        return new_filepath

    def _get_relevant_article_ids(self, articles: List[Dict], topic: str, max_items: int) -> List[str]:
        # Prepare article list for LLM
        articles_simple = []
        for a in articles:
            # Include more details if available for better judgement
            item = {
                "id": a.get("id"),
                "title": a.get("title"),
                "summary": a.get("summary"),
            }
            # If original source name is available, it might help with "influence"
            if a.get("source_id"):
                item["source"] = a.get("source_id")
            articles_simple.append(item)
        
        system_prompt = """
        You are an expert news editor with a keen eye for industry trends and impact.
        Your task is to select the most relevant and impactful articles for a specific topic from a provided list.
        
        Selection Criteria (Scoring Strategy):
        1. **Relevance (High Priority)**: Does the article directly address the topic?
        2. **Industry Influence**: Does the event have significant impact on the industry?
        3. **Entity Prominence**: Does it involve well-known companies, organizations, or figures?
        4. **Event Scope**: Is this a global/major event or a niche/local one?
        
        You should weigh these factors to select the best articles.
        """
        
        user_prompt = f"""
        Target Topic: "{topic}"
        Max Items to Select: {max_items}
        
        Below is the list of candidate articles:
        {json.dumps(articles_simple, ensure_ascii=False, indent=2)}
        
        Instructions:
        1. Analyze each article based on the Selection Criteria.
        2. Select the top {max_items} articles that are most relevant and impactful.
        3. If fewer than {max_items} articles are relevant, select only the relevant ones.
        4. Return the result in JSON format with a single key "selected_ids" containing the list of article IDs.
        
        Example Output:
        {{
            "selected_ids": ["art_1", "art_5", "art_2"]
        }}
        """
        
        try:
            response = llm_engine.generate_response(system_prompt, user_prompt, json_mode=True)
            if not response:
                return []
                
            data = json.loads(response)
            selected_ids = data.get("selected_ids", [])
            
            # Ensure we don't exceed max_items (though LLM should handle it)
            if len(selected_ids) > max_items:
                selected_ids = selected_ids[:max_items]
                
            return selected_ids
        except Exception as e:
            logger.error(f"Error in topic filtering: {e}")
            return []

# Global instance
topic_filter = TopicFilter()
