import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import Fetcher

class TestFetcherIntegration(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher()

    @patch('core.fetcher.feedparser.parse')
    def test_fetch_rss_integration(self, mock_parse):
        # Mock RSS feed
        mock_feed = MagicMock()
        mock_entry = MagicMock()
        # Ensure 'get' method works on mock_entry for dict-like access if needed
        mock_entry.get.side_effect = lambda k, d=None: getattr(mock_entry, k, d)
        
        mock_entry.title = "Test Article"
        mock_entry.link = "http://example.com/article"
        # Use current time to pass the time filter
        mock_entry.published_parsed = time.localtime()
        mock_entry.summary = "Test summary"
        mock_entry.description = "Test description"
        
        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        sources = [{
            "id": "1",
            "name": "Test Source",
            "type": "rss",
            "url": "http://example.com/feed.xml",
            "enabled": True
        }]

        results = self.fetcher.fetch_all(sources)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test Article")
        self.assertEqual(results[0]['source_name'], "Test Source")

    @patch('core.fetcher.requests.get')
    def test_fetch_web_integration(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><h1>Test Web Article</h1></body></html>"
        mock_get.return_value = mock_resp

        sources = [{
            "id": "2",
            "name": "Test Web Source",
            "type": "web_crawl",
            "url": "http://example.com/page",
            "enabled": True
        }]

        results = self.fetcher.fetch_all(sources)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], "raw_html")
        self.assertEqual(results[0]['source_name'], "Test Web Source")

if __name__ == '__main__':
    unittest.main()
