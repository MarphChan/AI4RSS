import os
import logging
from datetime import datetime
import frontmatter
import yaml
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.fetcher import fetcher
from core.llm import llm_engine
from core.deduplicator import deduplicator
from core.source_manager import source_manager
from core.image_gen import image_generator
from core.config_manager import config_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _builtin_default_image_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "images", "ai_news.svg"))

class NewsGenerator:
    def __init__(self, data_dir: str = "history"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def get_today_versions(self) -> List[str]:
        """Return a list of filepaths for today's news versions, sorted by version (newest first)."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        files = []
        
        if not os.path.exists(self.data_dir):
            return []

        for f in os.listdir(self.data_dir):
            if f.startswith(today_str) and f.endswith(".md"):
                files.append(os.path.join(self.data_dir, f))
        
        def sort_key(filepath):
            filename = os.path.basename(filepath)
            # Extract version
            parts = filename.replace(".md", "").split("-v")
            if len(parts) == 2:
                try:
                    return float(parts[1])
                except ValueError:
                    return 0.0
            return 0.0 # Fallback for non-versioned files
            
        files.sort(key=sort_key, reverse=True)
        return files

    def get_next_version_filepath(self) -> str:
        today_str = datetime.now().strftime("%Y-%m-%d")
        versions = self.get_today_versions()
        
        if not versions:
            return os.path.join(self.data_dir, f"{today_str}-v1.0.md")
            
        # Parse latest version
        latest_file = versions[0]
        filename = os.path.basename(latest_file)
        
        # Check if it follows the version pattern
        if "-v" in filename:
            try:
                # filename looks like "2023-10-27-v1.0.md"
                # split by "-v" gives ["2023-10-27", "1.0.md"]
                version_part = filename.split("-v")[1].replace(".md", "")
                current_v = float(version_part)
                next_v = int(current_v) + 1
                return os.path.join(self.data_dir, f"{today_str}-v{next_v}.0.md")
            except ValueError:
                pass
                
        # Fallback if existing file doesn't match version pattern or parsing fails
        # If we have "2023-10-27.md", we might want to start with v1.0 or v2.0?
        # Let's assume v1.0 if we can't parse a version.
        return os.path.join(self.data_dir, f"{today_str}-v1.0.md")

    def load_news(self, filepath: str) -> Optional[str]:
        """Load news content from a specific file."""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def delete_news(self, filepath: str) -> bool:
        """Delete a news file."""
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError as e:
                logger.error(f"Error deleting file {filepath}: {e}")
                return False
        return False

    def get_today_filepath(self) -> str:
        """Deprecated: Return the path for today's latest news file or default."""
        versions = self.get_today_versions()
        if versions:
            return versions[0]
        return self.get_next_version_filepath()

    def load_daily_news(self) -> Optional[str]:
        """Load today's latest news content if it exists."""
        filepath = self.get_today_filepath()
        if os.path.exists(filepath):
            return self.load_news(filepath)
        return None

    def _process_single_item(self, item: Dict, idx: int) -> Optional[Dict]:
        """Process a single news item (Summary + Image)."""
        content_to_summarize = item.get('content', '')
        if not content_to_summarize:
            return None

        # Summarize
        try:
            summary_data = llm_engine.summarize(content_to_summarize)
        except Exception as e:
            logger.error(f"Error summarizing item {idx}: {e}")
            return None
        
        # Image Handling
        # Priority 1: Extracted image from source (picurl)
        image_url = item.get('picurl', '')
        
        # Priority 2: AI Generation (if no image found and enabled)
        if not image_url and config_manager.config.get("image", {}).get("enable_generation", False):
            prompt = summary_data.get("image_prompt", "")
            if prompt:
                 # Rate limit or cost consideration needed here in real app
                 pass 
                 # image_url = image_generator.generate_image(prompt) 
        
        # Priority 3: Source Logo (Fallback)
        if not image_url and item.get('source_id'):
             source = source_manager.get_source(item['source_id'])
             if source and source.get('logo'):
                 image_url = source['logo'] 
        
        # Priority 4: Default Image (Fallback)
        if not image_url:
             default_images = config_manager.config.get("image", {}).get("default_images", [])
             if default_images:
                 image_url = default_images[idx % len(default_images)]
             else:
                 candidate = _builtin_default_image_path()
                 if os.path.exists(candidate):
                     image_url = candidate

        article_meta = {
            "id": f"art_{idx}",
            "source_id": item.get('source_id'),
            "original_url": item.get('url'),
            "title": summary_data.get('title', item.get('title')),
            "summary": summary_data.get('summary', ''),
            "image_prompt": summary_data.get('image_prompt', ''),
            "image_url": image_url,
            "picurl": item.get('picurl', '') # Store original picurl as well just in case
        }
        return article_meta

    def generate_daily_news(self, progress_callback=None, target_groups: Optional[List[str]] = None, max_items: int = 20) -> str:
        """
        Orchestrate the full generation pipeline.
        progress_callback: function(str, float) -> None
        target_groups: Optional list of groups to filter sources by.
        max_items: Limit the number of items to process (default: 20).
        """
        if progress_callback: progress_callback("Fetching sources...", 0.1)
        
        # 1. Fetch
        sources = source_manager.get_enabled_sources(target_groups=target_groups)
        if not sources:
            return "No enabled sources found for the selected groups."
            
        raw_items = fetcher.fetch_all(sources)
        if not raw_items:
            return "No news found in the last 24 hours."

        # Sort by pub_date descending (newest first)
        raw_items.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        
        # Deduplicate
        raw_items = deduplicator.filter_duplicates(raw_items)

        # Apply max_items limit
        if len(raw_items) > max_items:
            raw_items = raw_items[:max_items]

        if progress_callback: progress_callback(f"Found {len(raw_items)} items. Summarizing...", 0.3)

        # 2. Process & Summarize
        processed_articles = []
        total_items = len(raw_items)
        
        # Use ThreadPoolExecutor for concurrent processing
        # We can increase max_workers if needed, but 5 is a safe starting point
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Create a map of future -> item index
            future_to_idx = {
                executor.submit(self._process_single_item, item, idx): idx 
                for idx, item in enumerate(raw_items)
            }
            
            completed_count = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    article_meta = future.result()
                    if article_meta:
                        processed_articles.append(article_meta)
                except Exception as e:
                    logger.error(f"Error processing item {idx}: {e}")
                
                completed_count += 1
                if progress_callback:
                    # Update progress bar from 0.3 to 0.9
                    progress = 0.3 + (0.6 * completed_count / total_items)
                    title = article_meta['title'] if article_meta else "Skipped"
                    # Truncate title if too long
                    if len(title) > 20: title = title[:20] + "..."
                    progress_callback(f"Processed {completed_count}/{total_items}: {title}", progress)

        # Sort by ID to maintain original order
        # The ID format is art_{idx}, so we can sort by idx
        processed_articles.sort(key=lambda x: int(x['id'].split('_')[1]))

        # 3. Compile Markdown
        if progress_callback: progress_callback("Compiling Markdown...", 0.9)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Determine filepath and version
        filepath = self.get_next_version_filepath()
        filename = os.path.basename(filepath)
        # Extract version string (e.g., "v1.0")
        try:
            version_str = filename.split("-")[-1].replace(".md", "")
        except:
            version_str = "v1.0"

        # Front Matter
        front_matter = {
            "date": today_str,
            "version": version_str,
            "status": "pending_review",
            "push_time": config_manager.config.get("system", {}).get("push_time", "09:30"),
            "articles_meta": processed_articles
        }
        
        # Markdown Body
        md_body = f"# 📅 {today_str} AI Daily News ({version_str})\n\n"
        
        for i, art in enumerate(processed_articles):
            md_body += f"## {i+1}. {art['title']}\n"
            if art['image_url']:
                md_body += f"![]({art['image_url']})\n"
            md_body += f"> **摘要**：{art['summary']}\n"
            md_body += f"> *来源：[{art.get('source_id', 'Link')}]({art['original_url']})*\n\n"
            md_body += "---\n\n"

        # Combine
        post = frontmatter.Post(md_body, **front_matter)
        final_content = frontmatter.dumps(post)
        
        # Save
        # filepath is already determined above
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        if progress_callback: progress_callback("Done!", 1.0)
        
        return final_content

    def generate_daily_news_from_urls(
        self,
        urls: List[str],
        meta_by_url: Optional[Dict[str, Dict]] = None,
        generated_from: str = "reading_list",
        progress_callback=None,
        max_items: int = 20,
    ) -> str:
        normalized_urls = [u.strip() for u in (urls or []) if u and str(u).strip()]
        if not normalized_urls:
            return "No URLs provided."

        if len(normalized_urls) > max_items:
            normalized_urls = normalized_urls[:max_items]

        if progress_callback:
            progress_callback("Fetching pages...", 0.1)

        fetched_items = []
        meta_by_url = meta_by_url or {}

        def _fetch_one(u: str) -> Optional[Dict]:
            meta = meta_by_url.get(u) or {}
            title = meta.get("title") or ""
            picurl = meta.get("image_url") or meta.get("picurl") or ""
            items = fetcher._fetch_web(u, "Reading List", "reading_list")
            if not items:
                return None
            item = items[0]
            if title:
                item["title"] = title
            if picurl:
                item["picurl"] = picurl
            item["url"] = u
            return item

        total_fetch = len(normalized_urls)
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(_fetch_one, u): u for u in normalized_urls}
            fetched_count = 0
            for future in as_completed(futures):
                u = futures[future]
                try:
                    item = future.result()
                    if item:
                        fetched_items.append(item)
                except Exception as e:
                    logger.error(f"Error fetching url {u}: {e}")
                fetched_count += 1
                if progress_callback:
                    progress = 0.1 + (0.2 * fetched_count / max(total_fetch, 1))
                    progress_callback(f"Fetched {fetched_count}/{total_fetch}", progress)

        item_by_url = {x.get("url"): x for x in fetched_items if x.get("url")}
        ordered_items = [item_by_url[u] for u in normalized_urls if u in item_by_url]
        if not ordered_items:
            return "No content fetched from provided URLs."

        if progress_callback:
            progress_callback(f"Found {len(ordered_items)} pages. Summarizing...", 0.3)

        processed_articles = []
        total_items = len(ordered_items)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_idx = {
                executor.submit(self._process_single_item, item, idx): idx
                for idx, item in enumerate(ordered_items)
            }
            completed_count = 0
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    article_meta = future.result()
                    if article_meta:
                        processed_articles.append(article_meta)
                except Exception as e:
                    logger.error(f"Error processing item {idx}: {e}")
                completed_count += 1
                if progress_callback:
                    progress = 0.3 + (0.6 * completed_count / max(total_items, 1))
                    title = article_meta['title'] if article_meta else "Skipped"
                    if len(title) > 20:
                        title = title[:20] + "..."
                    progress_callback(f"Processed {completed_count}/{total_items}: {title}", progress)

        processed_articles.sort(key=lambda x: int(x['id'].split('_')[1]))

        if progress_callback:
            progress_callback("Compiling Markdown...", 0.9)

        today_str = datetime.now().strftime("%Y-%m-%d")
        filepath = self.get_next_version_filepath()
        filename = os.path.basename(filepath)
        try:
            version_str = filename.split("-")[-1].replace(".md", "")
        except:
            version_str = "v1.0"

        front_matter = {
            "date": today_str,
            "version": version_str,
            "status": "pending_review",
            "push_time": config_manager.config.get("system", {}).get("push_time", "09:30"),
            "articles_meta": processed_articles,
            "generated_from": generated_from,
        }

        md_body = f"# 📅 {today_str} AI Daily News ({version_str})\n\n"
        for i, art in enumerate(processed_articles):
            md_body += f"## {i+1}. {art['title']}\n"
            if art['image_url']:
                md_body += f"![]({art['image_url']})\n"
            md_body += f"> **摘要**：{art['summary']}\n"
            md_body += f"> *来源：[{art.get('source_id', 'Link')}]({art['original_url']})*\n\n"
            md_body += "---\n\n"

        post = frontmatter.Post(md_body, **front_matter)
        final_content = frontmatter.dumps(post)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)

        if progress_callback:
            progress_callback("Done!", 1.0)

        return final_content

# Global instance
news_generator = NewsGenerator()
