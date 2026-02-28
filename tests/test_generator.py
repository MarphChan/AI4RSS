import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import NewsGenerator

class TestNewsGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = NewsGenerator(data_dir="tests/test_history")
        
    def tearDown(self):
        # Clean up test history
        if os.path.exists("tests/test_history"):
            import shutil
            shutil.rmtree("tests/test_history")

    @patch('core.generator.source_manager')
    @patch('core.generator.fetcher')
    @patch('core.generator.llm_engine')
    @patch('core.generator.config_manager')
    @patch('core.generator.deduplicator')
    def test_generate_daily_news_max_items(self, mock_deduplicator, mock_config, mock_llm, mock_fetcher, mock_source_manager):
        # Mock dependencies
        mock_source_manager.get_enabled_sources.return_value = [{'id': '1', 'url': 'http://test.com'}]
        mock_deduplicator.filter_duplicates.side_effect = lambda x: x # Pass through all items
        
        # Mock fetcher to return 30 items
        # Make content distinct enough to avoid deduplication
        mock_items = [{'title': f'This is a very unique news title number {i} which is definitely not a duplicate of others', 'content': f'Content for news item number {i} which is very unique and different from others {i*100}', 'url': f'http://test.com/{i}'} for i in range(30)]
        mock_fetcher.fetch_all.return_value = mock_items
        
        # Mock LLM to return simple summary
        mock_llm.summarize.return_value = {
            "title": "Summary Title",
            "summary": "Summary Content",
            "image_prompt": "Image Prompt"
        }
        
        # Mock config
        mock_config.config = {"image": {"enable_generation": False}, "system": {"push_time": "09:30"}}
        
        # Test with max_items=5
        self.generator.generate_daily_news(max_items=5)
        
        # Verify LLM was called 5 times
        self.assertEqual(mock_llm.summarize.call_count, 5)
        
        # Test with max_items=20
        mock_llm.reset_mock()
        self.generator.generate_daily_news(max_items=20)
        self.assertEqual(mock_llm.summarize.call_count, 20)

    @patch('core.generator.source_manager')
    @patch('core.generator.fetcher')
    @patch('core.generator.llm_engine')
    @patch('core.generator.config_manager')
    @patch('core.generator.deduplicator')
    def test_generate_daily_news_with_logo(self, mock_deduplicator, mock_config, mock_llm, mock_fetcher, mock_source_manager):
        # Mock source with logo
        mock_source_manager.get_enabled_sources.return_value = [{'id': '1', 'url': 'http://test.com', 'logo': 'http://test.com/logo.png'}]
        mock_source_manager.get_source.return_value = {'id': '1', 'url': 'http://test.com', 'logo': 'http://test.com/logo.png'}
        
        # Mock item without image
        mock_items = [{'title': 'News Logo Test', 'content': 'Content for logo test', 'url': 'http://test.com/1', 'picurl': '', 'source_id': '1'}]
        mock_fetcher.fetch_all.return_value = mock_items
        mock_deduplicator.filter_duplicates.side_effect = lambda x: x
        
        # Mock LLM
        mock_llm.summarize.return_value = {"title": "Summary", "summary": "Summary", "image_prompt": "Prompt"}
        
        # Mock config
        mock_config.config = {"image": {"enable_generation": False}, "system": {"push_time": "09:30"}}
        
        # Generate
        content = self.generator.generate_daily_news(max_items=1)
        
        # Check if logo is used in markdown
        self.assertIn('http://test.com/logo.png', content)

if __name__ == '__main__':
    unittest.main()
