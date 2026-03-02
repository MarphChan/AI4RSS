import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from core.config_manager import config_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Fetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
        }

    def fetch_all(self, sources: List[Dict]) -> List[Dict]:
        """Fetch all enabled sources concurrently."""
        results = []
        enabled_sources = [s for s in sources if s.get('enabled', True)]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._fetch_single_source, source): source for source in enabled_sources}
            for future in futures:
                try:
                    items = future.result()
                    results.extend(items)
                except Exception as e:
                    logger.error(f"Error fetching source: {e}")
        
        return results

    def _fetch_single_source(self, source: Dict) -> List[Dict]:
        """Dispatch to correct fetch method based on type."""
        source_type = source.get('type', 'rss')
        url = source.get('url')
        name = source.get('name')
        
        logger.info(f"Fetching {name} ({url})...")
        
        if source_type == 'rss':
            return self._fetch_rss(url, name, source['id'])
        elif source_type == 'web_crawl':
            return self._fetch_web(url, name, source['id'])
        else:
            logger.warning(f"Unknown source type: {source_type}")
            return []

    def _fetch_rss(self, url: str, source_name: str, source_id: str) -> List[Dict]:
        """Parse RSS feed."""
        try:
            feed = feedparser.parse(url)
            items = []
            
            # Get configured time period (default 24 hours)
            time_period = config_manager.get("system.time_period", 24)
            cutoff_time = datetime.now() - timedelta(hours=time_period)
            
            for entry in feed.entries:
                # Handle publication date
                published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                if published_parsed:
                    pub_date = datetime.fromtimestamp(time.mktime(published_parsed))
                else:
                    pub_date = datetime.now() # Fallback

                # Filter last 24h
                if pub_date > cutoff_time:
                    # Extract image
                    picurl = self._extract_image_from_rss_entry(entry)
                    # If no image found in RSS, try fetching the original page (optional, but requested)
                    if not picurl and entry.get('link'):
                        picurl = self._fetch_page_image(entry.get('link'))

                    items.append({
                        "title": entry.get('title', 'No Title'),
                        "url": entry.get('link', ''),
                        "content": self._clean_html(entry.get('summary', '') or entry.get('description', '')),
                        "pub_date": pub_date.isoformat(),
                        "source_name": source_name,
                        "source_id": source_id,
                        "picurl": picurl,
                        "raw_data": entry
                    })
            
            return items
        except Exception as e:
            logger.error(f"RSS error for {url}: {e}")
            return []

    def _fetch_web(self, url: str, source_name: str, source_id: str) -> List[Dict]:
        """
        Simple web fetcher with specialized parser support (e.g. for WeChat). 
        """
        try:
            # Check for specialized parser (Jina Reader)
            parser_config = config_manager.config.get("parser", {}).get("jina_reader", {})
            use_jina = parser_config.get("enabled", False)
            
            # WeChat articles are notorious for anti-scraping, use Jina if enabled
            if use_jina and "mp.weixin.qq.com" in url:
                jina_url = f"{parser_config.get('base_url', 'https://r.jina.ai/')}{url}"
                logger.info(f"Using Jina Reader for WeChat article: {url}")
                try:
                    resp = requests.get(jina_url, headers=self.headers, timeout=20)
                    # Check for Jina's error message even if status is 200
                    if resp.status_code == 200 and "No content fetched from provided URLs" not in resp.text:
                        return [{
                            "type": "markdown",
                            "content": resp.text, # Jina returns clean markdown
                            "url": url,
                            "source_name": source_name,
                            "source_id": source_id,
                            "picurl": self._extract_image_from_html(resp.text, url), # Heuristic
                            "pub_date": datetime.now().isoformat()
                        }]
                    else:
                        logger.warning(f"Jina Reader failed or returned error message for {url}, falling back to standard fetch.")
                except Exception as e:
                    logger.warning(f"Jina Reader request failed for {url}: {e}, falling back to standard fetch.")
            
            # Fallback to standard requests
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                html_content = resp.text
                
                # Specialized parsing for WeChat if needed
                if "mp.weixin.qq.com" in url:
                    soup = BeautifulSoup(html_content, 'lxml')
                    # WeChat content is usually in #js_content
                    js_content = soup.find('div', id='js_content')
                    if js_content:
                        html_content = str(js_content)
                
                picurl = self._extract_image_from_html(html_content, url)
                return [{
                    "type": "raw_html",
                    "content": self._clean_html(html_content), 
                    "url": url,
                    "source_name": source_name,
                    "source_id": source_id,
                    "picurl": picurl,
                    "pub_date": datetime.now().isoformat()
                }]
            return []
        except Exception as e:
            logger.error(f"Web fetch error for {url}: {e}")
            return []

    def _extract_image_from_rss_entry(self, entry) -> str:
        """Extract image URL from RSS entry."""
        # 1. Enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href', '')
        
        # 2. Media content (media:content)
        if hasattr(entry, 'media_content') and entry.media_content:
             for media in entry.media_content:
                if media.get('type', '').startswith('image/') or media.get('medium') == 'image':
                    return media.get('url', '')

        # 3. Content/Summary/Description HTML
        content = ""
        if hasattr(entry, 'content') and entry.content:
            # Atom uses 'content' list
            for c in entry.content:
                if c.get('type') == 'text/html':
                    content = c.get('value', '')
                    break
        
        if not content:
            content = entry.get('summary', '') or entry.get('description', '')
        
        if content:
            img_url = self._extract_first_img_src(content)
            if img_url: 
                return img_url
        
        return ""

    def _extract_image_from_html(self, html_content: str, base_url: str = "") -> str:
        """Extract main image from HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 1. og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']
            
            # 2. twitter:image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image['content']

            # 3. First img tag in main content (heuristic)
            for img in soup.find_all('img'):
                # Handle standard src and WeChat's data-src
                src = img.get('src') or img.get('data-src')
                if src:
                    # skip small icons/tracking pixels? (hard without size info)
                    if 'icon' in src or 'logo' in src:
                        continue
                    
                    if not src.startswith('http'):
                        if base_url:
                            src = urljoin(base_url, src)
                        else:
                            continue
                    
                    return src
        except Exception as e:
            logger.error(f"Error extracting image from HTML: {e}")
            pass
        return ""

    def _extract_first_img_src(self, html: str) -> str:
        """Helper to find first img src in HTML fragment."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            img = soup.find('img')
            if img and img.get('src'):
                return img['src']
        except Exception as e:
            logger.error(f"Error extracting first img src: {e}")
            pass
        return ""

    def _fetch_page_image(self, url: str) -> str:
        """Fetch a page solely to extract its main image."""
        try:
            # Use a short timeout to avoid blocking too long
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                return self._extract_image_from_html(resp.text, url)
        except Exception:
            pass
        return ""

    def _clean_html(self, html_content: str) -> str:
        """Remove script/style tags and get text."""
        soup = BeautifulSoup(html_content, 'lxml')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        return soup.get_text(separator=' ', strip=True)[:10000] # Limit context window

    def check_availability(self, url: str, source_type: str = 'rss') -> bool:
        """Check if a source is reachable and valid."""
        try:
            if source_type == 'rss':
                feed = feedparser.parse(url)
                # Check if it has entries or at least a title/description
                # feedparser usually returns a 'bozo' exception if malformed, but not always for HTTP errors
                # We can check feed.status if available (HTTP status)
                if hasattr(feed, 'status'):
                     if feed.status >= 400:
                         return False
                # If entries exist, it's definitely good
                if feed.entries:
                    return True
                # If no entries but has feed.feed (metadata), it might be an empty feed but valid
                if hasattr(feed, 'feed') and (feed.feed.get('title') or feed.feed.get('description')):
                    return True
                return False
            else:
                resp = requests.head(url, headers=self.headers, timeout=5)
                if resp.status_code < 400:
                    return True
                # Fallback to get if head fails (some servers block head)
                resp = requests.get(url, headers=self.headers, timeout=5)
                return resp.status_code < 400
        except Exception as e:
            logger.warning(f"Availability check failed for {url}: {e}")
            return False

# Global instance
fetcher = Fetcher()
