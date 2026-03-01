import unittest

from core.feishu_receiver import _find_first_url_in_payload


class TestFeishuReceiver(unittest.TestCase):
    def test_find_first_url_in_payload(self):
        payload = {"text": {"content": "please read https://example.com/a thanks"}}
        self.assertEqual(_find_first_url_in_payload(payload), "https://example.com/a")


if __name__ == "__main__":
    unittest.main()

