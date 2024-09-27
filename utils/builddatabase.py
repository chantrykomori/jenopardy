"""
Server-side program to scrape from j-archive and fully update the episode tables in the database.
"""

from dbbuilder import update_database
from jsoncrawler import crawl

def main():
    """Runs both the web scraper and the database updater."""
    crawl()
    update_database()

if __name__ == "__main__":
    main()
