import json
import os
import uuid
from typing import List, Dict, Optional

class SourceManager:
    def __init__(self, sources_path: str = "sources.json"):
        self.sources_path = sources_path
        self._sources = self._load_sources()

    def _load_sources(self) -> List[Dict]:
        """Load sources from JSON file."""
        if not os.path.exists(self.sources_path):
            self._save_sources([])
            return []
        
        try:
            with open(self.sources_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_sources(self, sources: List[Dict]):
        """Save sources to JSON file."""
        with open(self.sources_path, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=2, ensure_ascii=False)

    def get_all_sources(self) -> List[Dict]:
        """Return all sources."""
        return self._sources

    def get_enabled_sources(self, target_groups: Optional[List[str]] = None) -> List[Dict]:
        """
        Return only enabled sources.
        If target_groups is provided, filter by group as well.
        """
        sources = [s for s in self._sources if s.get('enabled', False)]
        if target_groups:
            # If target_groups is provided, only keep sources whose group is in the list
            # Default empty group to "Default" for safety
            sources = [s for s in sources if s.get('group', 'Default') in target_groups]
        return sources

    def get_all_groups(self) -> List[str]:
        """Return a list of all unique groups found in sources."""
        groups = set()
        for s in self._sources:
            groups.add(s.get('group', 'Default'))
        return sorted(list(groups))

    def get_source(self, source_id: str) -> Optional[Dict]:
        """Get a source by ID."""
        for s in self._sources:
            if s['id'] == source_id:
                return s
        return None

    def add_source(self, name: str, source_type: str, url: str, group: str = "Default", logo: str = "") -> Dict:
        """Add a new source."""
        new_source = {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": source_type,
            "url": url,
            "group": group,
            "logo": logo,
            "enabled": True,
            "last_crawl_time": None
        }
        self._sources.append(new_source)
        self._save_sources(self._sources)
        return new_source

    def update_source(self, source_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing source."""
        for source in self._sources:
            if source['id'] == source_id:
                source.update(updates)
                self._save_sources(self._sources)
                return source
        return None

    def update_sources_bulk(self, updates_by_id: Dict[str, Dict]) -> int:
        """Update multiple sources and persist once. Returns count of updated items."""
        if not updates_by_id:
            return 0

        updated_count = 0
        for source in self._sources:
            source_id = source.get("id")
            if source_id in updates_by_id:
                source.update(updates_by_id[source_id])
                updated_count += 1

        if updated_count > 0:
            self._save_sources(self._sources)
        return updated_count

    def delete_source(self, source_id: str) -> bool:
        """Delete a source."""
        original_len = len(self._sources)
        self._sources = [s for s in self._sources if s['id'] != source_id]
        if len(self._sources) < original_len:
            self._save_sources(self._sources)
            return True
        return False

    def delete_sources(self, source_ids: List[str]) -> int:
        """Delete multiple sources. Returns count of deleted items."""
        original_len = len(self._sources)
        self._sources = [s for s in self._sources if s['id'] not in source_ids]
        deleted_count = original_len - len(self._sources)
        if deleted_count > 0:
            self._save_sources(self._sources)
        return deleted_count

# Global instance
source_manager = SourceManager()
