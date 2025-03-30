# run_scraper.py
import asyncio
from scraper.ContentScraper import ScrapeRunner
from scraper.WebScraper import WebScraper

if __name__ == "__main__":
    domain = "https://aloa.co"
    runner = ScrapeRunner(domain)
    asyncio.run(runner.run())
    ##scraper = WebScraper(domain)
    ##scraper.process_website()
