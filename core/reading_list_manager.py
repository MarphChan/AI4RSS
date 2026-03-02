import json
import os
import re
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(v: Any) -> str:
    return str(v) if v is not None else ""


def _url_to_id(url: str) -> str:
    u = url.strip()
    return hashlib.sha1(u.encode("utf-8")).hexdigest()


def _extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        host = parsed.netloc or ""
        return host.replace("www.", "")
    except Exception:
        return ""


def _normalize_url(url: str) -> str:
    return url.strip()


URL_RE = re.compile(r"https?://[^\s<>\"]+")


@dataclass
class ReadingItem:
    id: str
    url: str
    title: str = ""
    image_url: str = ""
    source: str = ""
    added_at: str = ""


class ReadingListManager:
    def __init__(self, storage_path: str = os.path.join("history", "reading_list.json")):
        self.storage_path = storage_path

    def _ensure_storage_dir(self) -> None:
        d = os.path.dirname(os.path.abspath(self.storage_path))
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    def _load_raw(self) -> Dict[str, Any]:
        self._ensure_storage_dir()
        if not os.path.exists(self.storage_path):
            return {"version": 1, "items": {}, "unread": [], "read": []}
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {"version": 1, "items": {}, "unread": [], "read": []}
            data.setdefault("version", 1)
            data.setdefault("items", {})
            data.setdefault("unread", [])
            data.setdefault("read", [])
            return data
        except Exception:
            return {"version": 1, "items": {}, "unread": [], "read": []}

    def _save_raw(self, data: Dict[str, Any]) -> None:
        self._ensure_storage_dir()
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_url(
        self,
        url: str,
        title: Optional[str] = None,
        image_url: Optional[str] = None,
        source: Optional[str] = None,
        default_status: str = "unread",
        preserve_order_if_exists: bool = True,
    ) -> ReadingItem:
        normalized_url = _normalize_url(url)
        item_id = _url_to_id(normalized_url)
        data = self._load_raw()

        in_unread = item_id in data.get("unread", [])
        in_read = item_id in data.get("read", [])

        existing = data["items"].get(item_id)
        if existing:
            if title and not existing.get("title"):
                existing["title"] = _safe_str(title)
            if image_url and not existing.get("image_url"):
                existing["image_url"] = _safe_str(image_url)
            if source and not existing.get("source"):
                existing["source"] = _safe_str(source)
            data["items"][item_id] = existing
        else:
            new_item = ReadingItem(
                id=item_id,
                url=normalized_url,
                title=_safe_str(title),
                image_url=_safe_str(image_url),
                source=_safe_str(source),
                added_at=_utc_now_iso(),
            )
            data["items"][item_id] = asdict(new_item)

        if not (preserve_order_if_exists and existing and (in_unread or in_read)):
            data["unread"] = [x for x in data["unread"] if x != item_id]
            data["read"] = [x for x in data["read"] if x != item_id]

            if default_status == "read":
                data["read"].insert(0, item_id)
            else:
                data["unread"].insert(0, item_id)
        else:
            if not in_unread and not in_read:
                if default_status == "read":
                    data["read"].append(item_id)
                else:
                    data["unread"].append(item_id)

        self._save_raw(data)
        stored = data["items"][item_id]
        return ReadingItem(**stored)

    def sync_articles(self, articles_meta: List[Dict[str, Any]]) -> int:
        added = 0
        for art in articles_meta or []:
            url = _safe_str(art.get("original_url") or art.get("url"))
            if not url:
                continue
            title = _safe_str(art.get("title"))
            image_url = _safe_str(art.get("picurl") or art.get("image_url") or art.get("logo"))
            before = self.exists(url)
            self.add_url(
                url,
                title=title,
                image_url=image_url,
                source="generated",
                default_status="unread",
                preserve_order_if_exists=True,
            )
            if not before:
                added += 1
        return added

    def exists(self, url: str) -> bool:
        normalized_url = _normalize_url(url)
        item_id = _url_to_id(normalized_url)
        data = self._load_raw()
        return item_id in data.get("items", {})

    def get_lists(self) -> Tuple[List[ReadingItem], List[ReadingItem]]:
        data = self._load_raw()
        items = data.get("items", {})
        unread = []
        read = []
        for item_id in data.get("unread", []):
            raw = items.get(item_id)
            if raw:
                unread.append(ReadingItem(**raw))
        for item_id in data.get("read", []):
            raw = items.get(item_id)
            if raw:
                read.append(ReadingItem(**raw))
        return unread, read

    def set_read_status(self, item_id: str, is_read: bool, insert_to_top: bool = True) -> None:
        if not item_id:
            return
        data = self._load_raw()
        if item_id not in data.get("items", {}):
            return

        data["unread"] = [x for x in data.get("unread", []) if x != item_id]
        data["read"] = [x for x in data.get("read", []) if x != item_id]

        if is_read:
            if insert_to_top:
                data["read"].insert(0, item_id)
            else:
                data["read"].append(item_id)
        else:
            if insert_to_top:
                data["unread"].insert(0, item_id)
            else:
                data["unread"].append(item_id)

        self._save_raw(data)

    def delete_items(self, item_ids: List[str]) -> int:
        ids = [x for x in (item_ids or []) if x]
        if not ids:
            return 0

        data = self._load_raw()
        existing = data.get("items", {}) or {}
        deleted = 0

        for item_id in ids:
            if item_id in existing:
                existing.pop(item_id, None)
                deleted += 1

        data["items"] = existing
        data["unread"] = [x for x in data.get("unread", []) if x not in ids]
        data["read"] = [x for x in data.get("read", []) if x not in ids]

        if deleted > 0:
            self._save_raw(data)
        return deleted

    def update_from_drag_labels(self, unread_labels: List[str], read_labels: List[str]) -> None:
        data = self._load_raw()
        unread_ids = [self._label_to_id(x) for x in unread_labels]
        read_ids = [self._label_to_id(x) for x in read_labels]
        unread_ids = [x for x in unread_ids if x]
        read_ids = [x for x in read_ids if x]

        data["unread"] = unread_ids
        data["read"] = read_ids
        self._save_raw(data)

    def make_label(self, item: ReadingItem) -> str:
        domain = _extract_domain(item.url)
        base_title = item.title.strip() if item.title else item.url
        return f"{item.id} | {base_title} {('— ' + domain) if domain else ''}".strip()

    def _label_to_id(self, label: str) -> str:
        if not label:
            return ""
        parts = label.split("|", 1)
        if not parts:
            return ""
        maybe = parts[0].strip()
        return maybe if re.fullmatch(r"[0-9a-f]{40}", maybe) else ""

    def extract_first_url(self, text: str) -> str:
        m = URL_RE.search(text or "")
        return m.group(0) if m else ""


reading_list_manager = ReadingListManager()
