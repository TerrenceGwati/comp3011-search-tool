"""
test_indexer.py - unit tests for the indexer module
tests tokenisation, index building, save/load, and the print function
"""

import unittest
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from indexer import tokenise, build_index, save_index, load_index, print_word_index


class TestTokenise(unittest.TestCase):
    """tests for the tokenise function"""

    def test_basic_tokenisation(self):
        """simple sentence should split into individual words"""
        tokens = tokenise("Hello world")
        self.assertEqual(tokens, ["hello", "world"])

    def test_converts_to_lowercase(self):
        """all tokens should be lowercase"""
        tokens = tokenise("HELLO World")
        self.assertIn("hello", tokens)
        self.assertIn("world", tokens)

    def test_punctuation_removed(self):
        """punctuation should be stripped out"""
        tokens = tokenise("hello, world!")
        # commas and exclamation marks should not appear in tokens
        for token in tokens:
            self.assertRegex(token, r"^[a-z0-9]+$")

    def test_empty_string(self):
        """empty string should return empty list"""
        self.assertEqual(tokenise(""), [])

    def test_numbers_kept(self):
        """numbers should be treated as valid tokens"""
        tokens = tokenise("page 42")
        self.assertIn("42", tokens)

    def test_apostrophe_handling(self):
        """words with apostrophes should split appropriately"""
        tokens = tokenise("it's a test")
        # 'it' and 's' should both be there (apostrophe stripped)
        self.assertIn("it", tokens)
        self.assertIn("s", tokens)


class TestBuildIndex(unittest.TestCase):
    """tests for the index building function"""

    def _make_page(self, url, text):
        """helper to create a fake page dict with simple html"""
        return {"url": url, "html": f"<html><body><p>{text}</p></body></html>"}

    def test_word_appears_in_index(self):
        """a word from a page should appear in the built index"""
        pages = [self._make_page("http://example.com/1", "hello world")]
        index = build_index(pages)
        self.assertIn("hello", index)

    def test_frequency_counted_correctly(self):
        """if a word appears 3 times, frequency should be 3"""
        pages = [self._make_page("http://example.com/1", "good good good")]
        index = build_index(pages)
        self.assertEqual(index["good"]["http://example.com/1"]["frequency"], 3)

    def test_positions_recorded(self):
        """positions list should have one entry per occurrence"""
        pages = [self._make_page("http://example.com/1", "good bad good")]
        index = build_index(pages)
        # 'good' appears twice so positions should have 2 entries
        self.assertEqual(len(index["good"]["http://example.com/1"]["positions"]), 2)

    def test_multiple_pages(self):
        """words from different pages should all appear in the index"""
        pages = [
            self._make_page("http://example.com/1", "hello there"),
            self._make_page("http://example.com/2", "goodbye world"),
        ]
        index = build_index(pages)
        self.assertIn("hello", index)
        self.assertIn("goodbye", index)

    def test_word_on_multiple_pages(self):
        """a word shared across pages should list both pages"""
        pages = [
            self._make_page("http://example.com/1", "python is great"),
            self._make_page("http://example.com/2", "python is fun"),
        ]
        index = build_index(pages)
        self.assertIn("http://example.com/1", index["python"])
        self.assertIn("http://example.com/2", index["python"])

    def test_empty_pages_list(self):
        """passing no pages should return an empty index"""
        index = build_index([])
        self.assertEqual(index, {})


class TestSaveAndLoadIndex(unittest.TestCase):
    """tests for saving and loading the index to/from disk"""

    def test_save_and_reload(self):
        """saved index should be identical when reloaded"""
        index = {"hello": {"http://example.com": {"frequency": 2, "positions": [0, 5]}}}

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_index.json")
            save_index(index, filepath)
            loaded = load_index(filepath)

        self.assertEqual(index, loaded)

    def test_load_missing_file_returns_none(self):
        """loading a file that doesn't exist should return None, not crash"""
        result = load_index("/nonexistent/path/index.json")
        self.assertIsNone(result)


class TestPrintWordIndex(unittest.TestCase):
    """tests for the print command"""

    def test_missing_word_doesnt_crash(self):
        """printing a word not in the index should handle gracefully"""
        index = {"hello": {"http://example.com": {"frequency": 1, "positions": [0]}}}
        # should not raise any exception
        try:
            print_word_index(index, "notaword")
        except Exception as e:
            self.fail(f"print_word_index raised unexpectedly: {e}")

    def test_none_index_doesnt_crash(self):
        """printing with a None index should handle gracefully"""
        try:
            print_word_index(None, "hello")
        except Exception as e:
            self.fail(f"print_word_index raised unexpectedly: {e}")

    def test_case_insensitive_lookup(self):
        """should find 'hello' even if the user types 'Hello'"""
        index = {"hello": {"http://example.com": {"frequency": 1, "positions": [0]}}}
        # should not raise or print "not found"
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            print_word_index(index, "Hello")
        self.assertNotIn("not found", output.getvalue())


if __name__ == "__main__":
    unittest.main()