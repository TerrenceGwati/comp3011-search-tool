"""
test_crawler.py - unit tests for the crawler module
tests link extraction, text extraction, and edge cases
uses mocking so we don't actually hit the network during testing
"""

import unittest
from unittest.mock import patch, MagicMock

# add the src directory to path so we can import our modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from crawler import extract_internal_links, extract_text_from_html, get_all_pages
from bs4 import BeautifulSoup


class TestExtractInternalLinks(unittest.TestCase):
    """tests for the link extraction function"""

    def test_relative_link_converted_to_absolute(self):
        """relative links like /page/2 should become full urls"""
        html = '<a href="/page/2">Next</a>'
        soup = BeautifulSoup(html, "html.parser")
        links = extract_internal_links(soup, "https://quotes.toscrape.com", "https://quotes.toscrape.com")
        self.assertIn("https://quotes.toscrape.com/page/2", links)

    def test_external_links_excluded(self):
        """links to other domains should not be included"""
        html = '<a href="https://google.com">Google</a>'
        soup = BeautifulSoup(html, "html.parser")
        links = extract_internal_links(soup, "https://quotes.toscrape.com", "https://quotes.toscrape.com")
        self.assertNotIn("https://google.com", links)

    def test_no_duplicate_links(self):
        """the same link appearing multiple times should only be added once"""
        html = '<a href="/page/2">Next</a><a href="/page/2">Also Next</a>'
        soup = BeautifulSoup(html, "html.parser")
        links = extract_internal_links(soup, "https://quotes.toscrape.com", "https://quotes.toscrape.com")
        self.assertEqual(links.count("https://quotes.toscrape.com/page/2"), 1)

    def test_fragment_links_stripped(self):
        """anchors with # should have the fragment part removed"""
        html = '<a href="/page/2#section">Link</a>'
        soup = BeautifulSoup(html, "html.parser")
        links = extract_internal_links(soup, "https://quotes.toscrape.com", "https://quotes.toscrape.com")
        # should not contain the fragment version
        self.assertNotIn("https://quotes.toscrape.com/page/2#section", links)

    def test_no_links_returns_empty(self):
        """a page with no links should return an empty list"""
        html = "<p>No links here</p>"
        soup = BeautifulSoup(html, "html.parser")
        links = extract_internal_links(soup, "https://quotes.toscrape.com", "https://quotes.toscrape.com")
        self.assertEqual(links, [])


class TestExtractTextFromHtml(unittest.TestCase):
    """tests for the text extraction function"""

    def test_basic_text_extracted(self):
        """should pull out the visible text from a simple page"""
        html = "<p>Hello world</p>"
        text = extract_text_from_html(html)
        self.assertIn("Hello world", text)

    def test_script_tags_removed(self):
        """script tag content should not appear in extracted text"""
        html = "<p>Visible</p><script>var x = 1;</script>"
        text = extract_text_from_html(html)
        self.assertNotIn("var x = 1", text)
        self.assertIn("Visible", text)

    def test_style_tags_removed(self):
        """style tag content should not appear in extracted text"""
        html = "<p>Visible</p><style>body { color: red; }</style>"
        text = extract_text_from_html(html)
        self.assertNotIn("color: red", text)

    def test_empty_html_returns_string(self):
        """empty html should return a string (possibly empty), not an error"""
        result = extract_text_from_html("")
        self.assertIsInstance(result, str)

    def test_whitespace_collapsed(self):
        """excessive whitespace should be collapsed to single spaces"""
        html = "<p>Hello     world</p>"
        text = extract_text_from_html(html)
        self.assertNotIn("     ", text)


class TestGetAllPages(unittest.TestCase):
    """tests for the main crawl function - uses mocking to avoid real network calls"""

    @patch("crawler.requests.get")
    @patch("crawler.time.sleep")  # patch sleep so tests run fast
    def test_crawl_returns_pages(self, mock_sleep, mock_get):
        """should return at least one page when the site responds ok"""
        # set up a fake response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>Test page</p></body></html>"
        mock_get.return_value = mock_response

        pages = get_all_pages("https://quotes.toscrape.com", delay=0)
        self.assertGreater(len(pages), 0)
        self.assertIn("url", pages[0])
        self.assertIn("html", pages[0])

    @patch("crawler.requests.get")
    @patch("crawler.time.sleep")
    def test_crawl_skips_failed_pages(self, mock_sleep, mock_get):
        """pages that return non-200 status should be skipped"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        pages = get_all_pages("https://quotes.toscrape.com", delay=0)
        # with a 404, no pages should be in the results
        self.assertEqual(len(pages), 0)

    @patch("crawler.requests.get")
    @patch("crawler.time.sleep")
    def test_crawl_handles_network_error(self, mock_sleep, mock_get):
        """network errors should be caught without crashing"""
        import requests as req
        mock_get.side_effect = req.exceptions.RequestException("Connection refused")

        # should not raise, just handle gracefully
        try:
            pages = get_all_pages("https://quotes.toscrape.com", delay=0)
            self.assertEqual(len(pages), 0)
        except Exception as e:
            self.fail(f"get_all_pages raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()