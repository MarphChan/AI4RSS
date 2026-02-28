import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import NewsGenerator

class TestGeneratorDefaults(unittest.TestCase):
    def setUp(self):
        self.generator = NewsGenerator(data_dir="tests/temp_history")

    @patch('core.generator.source_manager')
    @patch('core.generator.fetcher')
    @patch('core.generator.llm_engine')
    @patch('core.generator.config_manager')
    @patch('core.generator.deduplicator')
    def test_default_image_fallback(self, mock_deduplicator, mock_config, mock_llm, mock_fetcher, mock_source_manager):
        # Mock dependencies
        mock_source_manager.get_enabled_sources.return_value = [{'id': '1', 'url': 'http://test.com'}]
        mock_source_manager.get_source.return_value = {'id': '1', 'url': 'http://test.com'} # No logo
        
        # Mock items without images
        mock_items = [
            {'title': f'News {i}', 'content': f'Content {i}', 'url': f'http://test.com/{i}', 'picurl': '', 'source_id': '1'} 
            for i in range(5)
        ]
        mock_fetcher.fetch_all.return_value = mock_items
        mock_deduplicator.filter_duplicates.side_effect = lambda x: x
        
        # Mock LLM
        mock_llm.summarize.return_value = {"title": "Summary", "summary": "Summary", "image_prompt": "Prompt"}
        
        # Mock config with default images
        default_images = ["http://img1.com", "http://img2.com"]
        mock_config.config = {
            "image": {
                "enable_generation": False,
                "default_images": default_images
            },
            "system": {"push_time": "09:30"}
        }
        
        # Generate
        content = self.generator.generate_daily_news(max_items=5)
        
        import frontmatter
        post = frontmatter.loads(content)
        articles = post.metadata['articles_meta']
        
        self.assertEqual(len(articles), 5)
        self.assertEqual(articles[0]['image_url'], "http://img1.com")
        self.assertEqual(articles[1]['image_url'], "http://img2.com")
        self.assertEqual(articles[2]['image_url'], "http://img1.com")
        self.assertEqual(articles[3]['image_url'], "http://img2.com")
        self.assertEqual(articles[4]['image_url'], "http://img1.com")

    def tearDown(self):
        import shutil
        if os.path.exists("tests/temp_history"):
            shutil.rmtree("tests/temp_history")

if __name__ == '__main__':
    unittest.main()
