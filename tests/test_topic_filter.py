import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import frontmatter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.topic_filter import TopicFilter

class TestTopicFilter(unittest.TestCase):
    def setUp(self):
        self.topic_filter = TopicFilter()
        self.test_file = "tests/test_history/2024-02-28-v1.0.md"
        if not os.path.exists("tests/test_history"):
            os.makedirs("tests/test_history")
        
        # Create a dummy news file
        metadata = {
            "version": "v1.0",
            "articles_meta": [
                {"id": "art_1", "title": "AI News", "summary": "AI is great"},
                {"id": "art_2", "title": "Finance News", "summary": "Money is great"},
            ]
        }
        post = frontmatter.Post("Content", **metadata)
        with open(self.test_file, 'w') as f:
            f.write(frontmatter.dumps(post))

    def tearDown(self):
        if os.path.exists("tests/test_history"):
            import shutil
            shutil.rmtree("tests/test_history")

    @patch('core.topic_filter.llm_engine')
    @patch('core.topic_filter.news_generator')
    def test_filter_and_save_version(self, mock_generator, mock_llm):
        # Mock load_news
        with open(self.test_file, 'r') as f:
            content = f.read()
        mock_generator.load_news.return_value = content
        
        # Mock LLM response
        mock_llm.generate_response.return_value = '{"selected_ids": ["art_1"]}'
        
        # Run filter
        new_filepath = self.topic_filter.filter_and_save_version(self.test_file, "AI", max_items=5)
        
        # Check result
        self.assertTrue(new_filepath.endswith("v1.1.md"))
        self.assertTrue(os.path.exists(new_filepath))
        
        # Verify content
        post = frontmatter.load(new_filepath)
        self.assertEqual(len(post.metadata['articles_meta']), 1)
        self.assertEqual(post.metadata['articles_meta'][0]['id'], "art_1")
        self.assertEqual(post.metadata['topic_filter'], "AI")

    @patch('core.topic_filter.llm_engine')
    def test_get_relevant_article_ids_max_items(self, mock_llm):
        articles = [
            {"id": "art_1", "title": "Title 1", "summary": "Summary 1"},
            {"id": "art_2", "title": "Title 2", "summary": "Summary 2"},
        ]
        
        # Mock LLM response
        mock_llm.generate_response.return_value = '{"selected_ids": ["art_1"]}'
        
        # Call method
        self.topic_filter._get_relevant_article_ids(articles, "Test Topic", max_items=3)
        
        # Verify LLM called with correct prompt containing max_items
        args, _ = mock_llm.generate_response.call_args
        user_prompt = args[1]
        self.assertIn("Max Items to Select: 3", user_prompt)
        self.assertIn("Select the top 3", user_prompt)

if __name__ == '__main__':
    unittest.main()
