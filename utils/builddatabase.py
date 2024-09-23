"""
Run this to scrape from j-archive and fully update the episode tables in the database.
"""

from dbbuilder import update_database
from jsoncrawler import crawl

def main():
    crawl()
    update_database()

if __name__ == "__main__":
    main()