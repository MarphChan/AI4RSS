import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm import LLMEngine
from core.fetcher import Fetcher

class TestDiscovery(unittest.TestCase):
    def setUp(self):
        self.llm = LLMEngine()
        self.fetcher = Fetcher()

    @patch('core.llm_base.OpenAI')
    def test_find_rss_sources(self, mock_openai):
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # We need to re-init client in llm because it's created in __init__
        self.llm.client = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        [
          {"name": "Test Source", "url": "http://test.com/rss", "type": "rss"}
        ]
        '''
        mock_client.chat.completions.create.return_value = mock_response

        sources = self.llm.find_rss_sources("Test Topic")
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]['name'], "Test Source")

    @patch('core.fetcher.feedparser.parse')
    def test_check_availability_rss(self, mock_parse):
        # Mock valid feed
        mock_feed = MagicMock()
        mock_feed.status = 200
        mock_feed.entries = [{'title': 'Test'}]
        mock_parse.return_value = mock_feed
        
        is_valid = self.fetcher.check_availability("http://test.com/rss", "rss")
        self.assertTrue(is_valid)
        
        # Mock invalid feed
        mock_feed.status = 404
        mock_feed.entries = []
        mock_feed.feed = {} # Empty metadata
        is_valid = self.fetcher.check_availability("http://test.com/rss", "rss")
        self.assertFalse(is_valid)

    @patch('core.fetcher.requests.head')
    def test_check_availability_web(self, mock_head):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_head.return_value = mock_resp
        
        is_valid = self.fetcher.check_availability("http://test.com", "web_crawl")
        self.assertTrue(is_valid)

if __name__ == '__main__':
    unittest.main()
