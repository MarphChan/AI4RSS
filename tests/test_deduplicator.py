import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.deduplicator import Deduplicator

class TestDeduplicator(unittest.TestCase):
    def setUp(self):
        self.deduplicator = Deduplicator()

    def test_filter_duplicates_exact_url(self):
        items = [
            {'title': 'Test News 1', 'url': 'http://test.com/1'},
            {'title': 'Test News 1 Modified', 'url': 'http://test.com/1'}, # Duplicate URL
            {'title': 'Another News', 'url': 'http://test.com/2'}
        ]
        unique = self.deduplicator.filter_duplicates(items)
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]['url'], 'http://test.com/1')
        self.assertEqual(unique[1]['url'], 'http://test.com/2')

    def test_filter_duplicates_similar_title(self):
        items = [
            {'title': 'OpenAI releases GPT-5 today', 'url': 'http://test.com/1'},
            {'title': 'OpenAI releases GPT-5 today!', 'url': 'http://test.com/2'}, # Very similar
        ]
        unique = self.deduplicator.filter_duplicates(items, similarity_threshold=0.9)
        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0]['url'], 'http://test.com/1')

    def test_filter_duplicates_different(self):
        items = [
            {'title': 'News A', 'url': 'http://test.com/1'},
            {'title': 'News B', 'url': 'http://test.com/2'}
        ]
        unique = self.deduplicator.filter_duplicates(items)
        self.assertEqual(len(unique), 2)

if __name__ == '__main__':
    unittest.main()
