import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import Fetcher

class MockEntry(dict):
    """Mock feedparser entry that supports both dict and attribute access"""
    def __getattr__(self, name):
        return self.get(name)

class TestFetcherImage(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher()

    def test_extract_image_from_html_og(self):
        html = """
        <html>
        <head>
            <meta property="og:image" content="http://example.com/og.jpg" />
        </head>
        <body>
            <img src="http://example.com/body.jpg" />
        </body>
        </html>
        """
        url = self.fetcher._extract_image_from_html(html)
        self.assertEqual(url, "http://example.com/og.jpg")

    def test_extract_image_from_html_first_img(self):
        html = """
        <html>
        <body>
            <p>Text</p>
            <img src="http://example.com/body.jpg" />
        </body>
        </html>
        """
        url = self.fetcher._extract_image_from_html(html)
        self.assertEqual(url, "http://example.com/body.jpg")

    def test_extract_image_from_html_relative(self):
        html = """
        <html>
        <body>
            <img src="/images/body.jpg" />
        </body>
        </html>
        """
        url = self.fetcher._extract_image_from_html(html, base_url="http://example.com")
        self.assertEqual(url, "http://example.com/images/body.jpg")

    def test_extract_image_from_rss_enclosure(self):
        entry = MockEntry({
            'enclosures': [{'type': 'image/jpeg', 'href': 'http://example.com/enc.jpg'}]
        })
        url = self.fetcher._extract_image_from_rss_entry(entry)
        self.assertEqual(url, "http://example.com/enc.jpg")

    def test_extract_image_from_rss_media(self):
        entry = MockEntry({
            'media_content': [{'type': 'image/png', 'url': 'http://example.com/media.png'}]
        })
        url = self.fetcher._extract_image_from_rss_entry(entry)
        self.assertEqual(url, "http://example.com/media.png")

    def test_extract_image_from_rss_description(self):
        entry = MockEntry({
            'summary': 'Summary <img src="http://example.com/desc.jpg"> text'
        })
        url = self.fetcher._extract_image_from_rss_entry(entry)
        self.assertEqual(url, "http://example.com/desc.jpg")

    @patch('core.fetcher.requests.get')
    def test_fetch_page_image(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '<html><meta property="og:image" content="http://example.com/fetched.jpg"></html>'
        mock_get.return_value = mock_resp

        url = self.fetcher._fetch_page_image("http://example.com/article")
        self.assertEqual(url, "http://example.com/fetched.jpg")

if __name__ == '__main__':
    unittest.main()
