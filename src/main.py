"""
main.py - the command line interface for the search tool
this is the entry point - run this file to start the shell
provides four commands: build, load, print, find
"""

import os
import sys

from crawler import get_all_pages
from indexer import build_index, save_index, load_index, print_word_index
from search import find_pages, display_results


# default path for the saved index file
INDEX_FILE = "data/index.json"


def ensure_data_dir():
    """makes sure the data/ directory exists before we try to write to it"""
    os.makedirs("data", exist_ok=True)


def run_build():
    """
    crawls the website, builds the index, and saves it to disk
    this can take a while because of the politeness delay between requests
    """

    print("Starting build... this will take a few minutes due to the politeness delay.")
    print("Please don't interrupt the process.\n")

    ensure_data_dir()

    # crawl all the pages
    pages = get_all_pages()

    if not pages:
        print("No pages were crawled. Check your internet connection and try again.")
        return None

    # build the index from the crawled pages
    index = build_index(pages)

    # save it so we don't have to crawl again next time
    save_index(index, INDEX_FILE)

    print("\nBuild complete. You can now use 'load', 'print', and 'find'.")
    return index


def run_load():
    """loads the index from the saved file"""
    index = load_index(INDEX_FILE)
    return index


def handle_command(command_line, index):
    """
    parses a command line input and calls the appropriate function
    returns the (possibly updated) index
    """

    # split the command line into parts
    parts = command_line.strip().split()

    if not parts:
        return index  # empty input, just loop again

    command = parts[0].lower()
    args = parts[1:]  # everything after the command

    if command == "build":
        index = run_build()

    elif command == "load":
        index = run_load()

    elif command == "print":
        if not args:
            print("Usage: print <word>")
            print("Example: print nonsense")
        else:
            # only use the first word for print - the spec asks for one word
            print_word_index(index, args[0])

    elif command == "find":
        if not args:
            print("Usage: find <word> [word2] ...")
            print("Example: find good friends")
        else:
            # rejoin the args so we can pass the full query string
            query = " ".join(args)
            results = find_pages(index, query)
            display_results(results, query)

    elif command in ("exit", "quit", "q"):
        print("Goodbye!")
        sys.exit(0)

    elif command == "help":
        print_help()

    else:
        print(f"Unknown command: '{command}'. Type 'help' for available commands.")

    return index


def print_help():
    """prints usage instructions"""
    print("""
Available commands:
  build               Crawl the website and build the search index
  load                Load a previously saved index from disk
  print <word>        Print the index entry for a specific word
  find <query>        Find pages containing the given word(s)
  help                Show this help message
  exit / quit / q     Exit the program

Examples:
  > build
  > load
  > print nonsense
  > find indifference
  > find good friends
""")


def main():
    """
    main loop - keeps running and reading commands until the user exits
    the index starts as None and gets set by build or load
    """

    print("=" * 50)
    print("  Search Engine Tool - COMP3011 Coursework 2")
    print("=" * 50)
    print("Type 'help' for available commands.\n")

    index = None  # no index loaded yet

    while True:
        try:
            # read a command from the user
            command_line = input("> ").strip()
            index = handle_command(command_line, index)

        except (KeyboardInterrupt, EOFError):
            # handle Ctrl+C or Ctrl+D gracefully
            print("\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()