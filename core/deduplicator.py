import difflib
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self):
        pass

    def filter_duplicates(self, items: List[Dict], similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Filter out duplicate items based on URL and Title similarity.
        Keeps the first occurrence (so items should be sorted by priority/date before calling).
        
        Args:
            items: List of dicts, each containing 'url' and 'title'.
            similarity_threshold: Float between 0 and 1. Titles with similarity > threshold are considered duplicates.
            
        Returns:
            List of unique items.
        """
        unique_items = []
        seen_urls = set()
        seen_titles = []

        for item in items:
            # 1. Exact URL Match
            url = item.get('url')
            if url and url in seen_urls:
                continue
            
            # 2. Title Similarity Match
            title = item.get('title', '')
            if not title:
                # If no title, just check URL (already done) or keep it
                if url:
                    seen_urls.add(url)
                    unique_items.append(item)
                continue

            is_duplicate = False
            for seen_title in seen_titles:
                # Use SequenceMatcher for similarity
                ratio = difflib.SequenceMatcher(None, title, seen_title).ratio()
                if ratio > similarity_threshold:
                    is_duplicate = True
                    logger.info(f"Duplicate found: '{title}' similar to '{seen_title}' (ratio: {ratio:.2f})")
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.append(title)
                if url:
                    seen_urls.add(url)
        
        return unique_items

# Global instance
deduplicator = Deduplicator()
