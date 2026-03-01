import os
import tempfile
import unittest

from core.reading_list_manager import ReadingListManager


class TestReadingListManager(unittest.TestCase):
    def test_add_url_persists_and_default_unread(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "reading_list.json")
            mgr = ReadingListManager(storage_path=path)

            item = mgr.add_url("https://example.com/a", title="A", source="manual")
            self.assertEqual(item.url, "https://example.com/a")

            unread, read = mgr.get_lists()
            self.assertEqual(len(unread), 1)
            self.assertEqual(len(read), 0)
            self.assertEqual(unread[0].url, "https://example.com/a")

            mgr2 = ReadingListManager(storage_path=path)
            unread2, read2 = mgr2.get_lists()
            self.assertEqual(len(unread2), 1)
            self.assertEqual(len(read2), 0)
            self.assertEqual(unread2[0].url, "https://example.com/a")

    def test_drag_updates_order_and_status(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "reading_list.json")
            mgr = ReadingListManager(storage_path=path)

            i1 = mgr.add_url("https://example.com/a", title="A", source="manual")
            i2 = mgr.add_url("https://example.com/b", title="B", source="manual")

            l1 = mgr.make_label(i1)
            l2 = mgr.make_label(i2)

            mgr.update_from_drag_labels([l1], [l2])

            unread, read = mgr.get_lists()
            self.assertEqual([x.url for x in unread], ["https://example.com/a"])
            self.assertEqual([x.url for x in read], ["https://example.com/b"])

    def test_sync_articles_preserves_existing_order(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "reading_list.json")
            mgr = ReadingListManager(storage_path=path)

            i1 = mgr.add_url("https://example.com/a", title="A", source="manual")
            i2 = mgr.add_url("https://example.com/b", title="B", source="manual")

            l1 = mgr.make_label(i1)
            l2 = mgr.make_label(i2)
            mgr.update_from_drag_labels([l2, l1], [])

            articles_meta = [
                {"original_url": "https://example.com/a", "title": "A"},
                {"original_url": "https://example.com/b", "title": "B"},
            ]
            mgr.sync_articles(articles_meta)

            unread, _ = mgr.get_lists()
            self.assertEqual([x.url for x in unread], ["https://example.com/b", "https://example.com/a"])

    def test_set_read_status_moves_between_lists(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "reading_list.json")
            mgr = ReadingListManager(storage_path=path)

            i1 = mgr.add_url("https://example.com/a", title="A", source="manual")
            unread, read = mgr.get_lists()
            self.assertEqual([x.id for x in unread], [i1.id])
            self.assertEqual(len(read), 0)

            mgr.set_read_status(i1.id, True)
            unread2, read2 = mgr.get_lists()
            self.assertEqual(len(unread2), 0)
            self.assertEqual([x.id for x in read2], [i1.id])

            mgr.set_read_status(i1.id, False)
            unread3, read3 = mgr.get_lists()
            self.assertEqual([x.id for x in unread3], [i1.id])
            self.assertEqual(len(read3), 0)

    def test_delete_items_removes_from_lists_and_storage(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "reading_list.json")
            mgr = ReadingListManager(storage_path=path)

            i1 = mgr.add_url("https://example.com/a", title="A", source="manual")
            i2 = mgr.add_url("https://example.com/b", title="B", source="manual")
            mgr.set_read_status(i2.id, True)

            deleted = mgr.delete_items([i1.id, i2.id])
            self.assertEqual(deleted, 2)

            unread, read = mgr.get_lists()
            self.assertEqual(len(unread), 0)
            self.assertEqual(len(read), 0)

            mgr2 = ReadingListManager(storage_path=path)
            unread2, read2 = mgr2.get_lists()
            self.assertEqual(len(unread2), 0)
            self.assertEqual(len(read2), 0)


if __name__ == "__main__":
    unittest.main()
