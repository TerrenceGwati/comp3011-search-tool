"""
test_search.py - unit tests for the search module
tests single word, multi-word, edge cases, and result ranking
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from search import find_pages, display_results


# a small sample index to use across all tests
SAMPLE_INDEX = {
    "good": {
        "http://example.com/1": {"frequency": 5, "positions": [0, 3, 7, 10, 14]},
        "http://example.com/2": {"frequency": 1, "positions": [2]},
    },
    "friends": {
        "http://example.com/1": {"frequency": 2, "positions": [1, 8]},
        "http://example.com/3": {"frequency": 3, "positions": [0, 4, 9]},
    },
    "indifference": {
        "http://example.com/4": {"frequency": 1, "positions": [5]},
    },
}


class TestFindPages(unittest.TestCase):
    """tests for the find command / search logic"""

    def test_single_word_found(self):
        """a word that exists should return matching urls"""
        results = find_pages(SAMPLE_INDEX, "good")
        urls = [r[0] for r in results]
        self.assertIn("http://example.com/1", urls)
        self.assertIn("http://example.com/2", urls)

    def test_word_not_in_index(self):
        """searching for a word not in the index should return empty list"""
        results = find_pages(SAMPLE_INDEX, "flibbertigibbet")
        self.assertEqual(results, [])

    def test_multi_word_intersection(self):
        """multi-word query should only return pages with ALL words"""
        results = find_pages(SAMPLE_INDEX, "good friends")
        urls = [r[0] for r in results]
        # only page 1 has both 'good' and 'friends'
        self.assertIn("http://example.com/1", urls)
        self.assertNotIn("http://example.com/2", urls)  # has 'good' but not 'friends'
        self.assertNotIn("http://example.com/3", urls)  # has 'friends' but not 'good'

    def test_multi_word_one_missing(self):
        """if one query word isn't in the index at all, return empty"""
        results = find_pages(SAMPLE_INDEX, "good notaword")
        self.assertEqual(results, [])

    def test_results_sorted_by_score(self):
        """results should be sorted highest score first"""
        results = find_pages(SAMPLE_INDEX, "good")
        scores = [r[1] for r in results]
        # check scores are in descending order
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_higher_frequency_ranks_higher(self):
        """page with more occurrences of the search word should rank higher"""
        results = find_pages(SAMPLE_INDEX, "good")
        # page 1 has frequency 5, page 2 has frequency 1 - page 1 should be first
        self.assertEqual(results[0][0], "http://example.com/1")

    def test_empty_query_returns_empty(self):
        """empty query should return empty list without crashing"""
        results = find_pages(SAMPLE_INDEX, "")
        self.assertEqual(results, [])

    def test_whitespace_only_query(self):
        """a query of only spaces should return empty list"""
        results = find_pages(SAMPLE_INDEX, "   ")
        self.assertEqual(results, [])

    def test_none_index_handled(self):
        """if no index is loaded, should handle gracefully not crash"""
        try:
            results = find_pages(None, "good")
            self.assertEqual(results, [])
        except Exception as e:
            self.fail(f"find_pages raised unexpectedly with None index: {e}")

    def test_case_insensitive_search(self):
        """searching 'Good' should find the same results as 'good'"""
        results_lower = find_pages(SAMPLE_INDEX, "good")
        results_upper = find_pages(SAMPLE_INDEX, "Good")
        self.assertEqual(results_lower, results_upper)

    def test_single_result(self):
        """a word on only one page should return exactly one result"""
        results = find_pages(SAMPLE_INDEX, "indifference")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "http://example.com/4")

    def test_result_is_list_of_tuples(self):
        """results should be a list of (url, score) tuples"""
        results = find_pages(SAMPLE_INDEX, "good")
        self.assertIsInstance(results, list)
        for item in results:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)


class TestDisplayResults(unittest.TestCase):
    """tests for the display function - mainly checking it doesn't crash"""

    def test_empty_results_no_crash(self):
        """displaying empty results should not raise"""
        try:
            display_results([], "test")
        except Exception as e:
            self.fail(f"display_results raised unexpectedly: {e}")

    def test_normal_results_no_crash(self):
        """displaying a normal result set should not raise"""
        results = [("http://example.com/1", 5), ("http://example.com/2", 2)]
        try:
            display_results(results, "good")
        except Exception as e:
            self.fail(f"display_results raised unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()