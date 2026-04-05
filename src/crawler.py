"""
crawler.py - handles all the web crawling for the search tool
basically responsible for visiting every page on quotes.toscrape.com
and pulling back the raw HTML so the indexer can process it
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# the base url we're working with - set once here so it's easy to change
BASE_URL = "https://quotes.toscrape.com"

# politeness window in seconds - coursework requires at least 6
POLITENESS_DELAY = 6


def get_all_pages(base_url=BASE_URL, delay=POLITENESS_DELAY):
    """
    crawls the entire site starting from the base url
    follows pagination links until there are no more pages
    returns a list of dicts, each with 'url' and 'html' keys
    """

    visited = set()       # track urls we've already seen so we don't loop
    to_visit = [base_url] # queue of urls still to crawl
    pages = []            # store the results here

    print(f"Starting crawl from: {base_url}")

    while to_visit:
        url = to_visit.pop(0)  # grab the next url from the front of the queue

        # skip if we've already been here
        if url in visited:
            continue

        # mark it as visited before we do anything
        visited.add(url)

        try:
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=10)

            # if the request failed (404, 500 etc) just skip this page
            if response.status_code != 200:
                print(f"  -> Got status {response.status_code}, skipping")
                continue

            html = response.text

            # store this page's data
            pages.append({
                "url": url,
                "html": html
            })

            # parse the html and look for any new links to follow
            soup = BeautifulSoup(html, "html.parser")
            new_links = extract_internal_links(soup, url, base_url)

            for link in new_links:
                if link not in visited:
                    to_visit.append(link)

        except requests.exceptions.RequestException as e:
            # network errors happen - just log and move on
            print(f"  -> Error fetching {url}: {e}")

        # wait before the next request - respect the politeness window
        if to_visit:
            print(f"  -> Waiting {delay}s before next request...")
            time.sleep(delay)

    print(f"\nCrawl complete. Visited {len(pages)} pages.")
    return pages


def extract_internal_links(soup, current_url, base_url):
    """
    finds all internal links on a page
    filters out external links and anything that isn't part of our target site
    returns a list of absolute urls
    """

    links = []
    base_domain = urlparse(base_url).netloc

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]

        # turn relative urls into absolute ones e.g. /page/2 -> https://quotes.toscrape.com/page/2
        absolute = urljoin(current_url, href)

        parsed = urlparse(absolute)

        # only keep links that are on the same domain
        if parsed.netloc == base_domain or parsed.netloc == "":
            # strip fragments (#section) since they're the same page
            clean = absolute.split("#")[0]
            if clean and clean not in links:
                links.append(clean)

    return links


def extract_text_from_html(html):
    """
    pulls out all the visible text from a page's html
    strips out script/style tags since we don't want to index those
    returns a plain string of text
    """

    soup = BeautifulSoup(html, "html.parser")

    # remove script and style tags - their content isn't useful for indexing
    for tag in soup(["script", "style"]):
        tag.decompose()

    # get_text joins all remaining text with spaces
    text = soup.get_text(separator=" ")

    # clean up excessive whitespace
    text = " ".join(text.split())

    return text
