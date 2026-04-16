"""
search.py - handles query processing and result ranking
takes a user query, looks it up in the index, and returns ranked results
supports both single word and multi-word phrase queries
"""

from indexer import tokenise


def find_pages(index, query):
    """
    finds all pages that contain every word in the query
    for multi-word queries this uses set intersection -
    only pages that have ALL the words are returned

    ranking is by combined frequency across all query words
    so pages that mention the words more often rank higher

    returns a sorted list of (url, score) tuples
    """

    if index is None:
        print("No index loaded. Use 'load' or 'build' first.")
        return []

    if not query or not query.strip():
        print("Please provide a search term.")
        return []

    # tokenise the query the same way we tokenised the pages
    # this keeps things consistent - case insensitive, same cleaning rules
    query_words = tokenise(query)

    if not query_words:
        print("Query contained no valid search terms after processing.")
        return []

    # find pages that contain the first word - this is our starting set
    first_word = query_words[0]

    if first_word not in index:
        print(f"No pages found containing '{query}'.")
        return []

    # start with the set of pages for the first word
    matching_urls = set(index[first_word].keys())

    # for each additional word, narrow the results down
    # this is the AND logic - all words must be present
    for word in query_words[1:]:
        if word not in index:
            # if any word in the query isn't in the index, there can't be any results
            print(f"No pages found containing '{query}'.")
            return []

        word_urls = set(index[word].keys())
        matching_urls = matching_urls.intersection(word_urls)

    if not matching_urls:
        print(f"No pages found containing all words in '{query}'.")
        return []

    # now score each matching page
    # score = sum of frequencies of all query words on that page
    # simple but effective for this use case
    results = []
    for url in matching_urls:
        score = 0
        for word in query_words:
            score += index[word][url]["frequency"]
        results.append((url, score))

    # sort highest score first
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def display_results(results, query):
    """
    pretty prints the search results
    shows rank, url, and score for each result
    """

    if not results:
        return  # messages already printed in find_pages

    print(f"\nSearch results for: '{query}'")
    print(f"Found {len(results)} page(s):\n")

    for rank, (url, score) in enumerate(results, start=1):
        print(f"  {rank}. {url}")
        print(f"     Relevance score: {score}")
        print()