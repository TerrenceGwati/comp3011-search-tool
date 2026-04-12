"""
indexer.py - builds and manages the inverted index
an inverted index maps each word -> list of pages it appears in,
along with stats like frequency and positions within the page
this is the core data structure that makes search fast
"""

import re
import json


def tokenise(text):
    """
    splits a block of text into individual lowercase tokens (words)
    removes punctuation and converts everything to lowercase
    so 'Good' and 'good' are treated as the same word
    returns a list of word strings
    """

    # lowercase first so the index is case-insensitive
    text = text.lower()

    # strip anything that isn't a letter, digit, or space
    # this handles punctuation like commas, apostrophes etc
    tokens = re.findall(r"[a-z0-9]+", text)

    return tokens


def build_index(pages):
    """
    takes a list of crawled pages and builds the inverted index
    
    the index structure looks like this:
    {
        "word": {
            "url1": {
                "frequency": 3,
                "positions": [4, 17, 42]   <- word positions in the token list
            },
            "url2": { ... }
        },
        ...
    }

    frequency = how many times the word appears on that page
    positions = which token positions the word is at (useful for phrase search)

    returns the index dict
    """

    index = {}

    for page in pages:
        url = page["url"]
        html = page["html"]

        # get clean text from this page
        # we import here to keep the module focused - crawler handles html parsing
        from crawler import extract_text_from_html
        text = extract_text_from_html(html)

        tokens = tokenise(text)

        # go through every token and record where it appears
        for position, word in enumerate(tokens):

            # if this is the first time we've seen this word, set up its entry
            if word not in index:
                index[word] = {}

            # if this is the first time this word has appeared on this url
            if url not in index[word]:
                index[word][url] = {
                    "frequency": 0,
                    "positions": []
                }

            # update the stats for this word on this page
            index[word][url]["frequency"] += 1
            index[word][url]["positions"].append(position)

    print(f"Index built. Total unique words: {len(index)}")
    return index


def save_index(index, filepath="data/index.json"):
    """
    saves the index to disk as a json file
    json is human readable and easy to reload later
    """

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"Index saved to {filepath}")


def load_index(filepath="data/index.json"):
    """
    loads a previously saved index from disk
    returns the index dict, or None if the file doesn't exist
    """

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            index = json.load(f)

        print(f"Index loaded from {filepath}. Words in index: {len(index)}")
        return index

    except FileNotFoundError:
        print(f"No index file found at {filepath}. Run 'build' first.")
        return None

    except json.JSONDecodeError as e:
        print(f"Error reading index file: {e}")
        return None


def print_word_index(index, word):
    """
    prints the index entry for a given word
    shows every page the word appears in, its frequency, and positions
    """

    word = word.lower()  # normalise the input

    if index is None:
        print("No index loaded. Use 'load' or 'build' first.")
        return

    if word not in index:
        print(f"Word '{word}' not found in the index.")
        return

    entries = index[word]
    print(f"\nIndex entry for '{word}':")
    print(f"  Appears in {len(entries)} page(s):\n")

    # sort by frequency descending so the most relevant pages come first
    sorted_entries = sorted(entries.items(), key=lambda x: x[1]["frequency"], reverse=True)

    for url, stats in sorted_entries:
        print(f"  URL: {url}")
        print(f"    Frequency : {stats['frequency']}")
        print(f"    Positions : {stats['positions'][:10]}{'...' if len(stats['positions']) > 10 else ''}")
        print()