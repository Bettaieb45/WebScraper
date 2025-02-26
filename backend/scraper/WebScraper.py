import requests
from bs4 import BeautifulSoup
from scraper.MongoDBHandler import MongoDBHandler
from scraper.SitemapScraper import SitemapScraper
from scraper.InternalLinkCrawler import InternalLinkCrawler
import csv
class WebScraper:
    """Coordinates the entire scraping process."""

    def __init__(self, domain, db_handler=None, sitemap_scraper=None, link_crawler=None):
        self.domain = self.remove_trailing_slash(domain)
        self.website_name = self.get_website_name()

        # Use dependency injection for flexibility and testing
        self.db_handler = db_handler or MongoDBHandler(self.website_name)
        self.sitemap_scraper = sitemap_scraper or SitemapScraper(self.domain)
        self.link_crawler = link_crawler or InternalLinkCrawler(self.domain)

        self.scraped_urls = []

    def get_website_name(self):
        """Extracts the name of the website from the domain and formats it."""
        return self.domain.replace("https://", "").replace("http://", "").split(".")[0]

    def remove_trailing_slash(self, url):
        """Removes the trailing slash from a URL."""
        return url[:-1] if url.endswith("/") else url

    def fetch_sitemap_urls(self):
        """Fetches URLs from the sitemap."""
        sitemap_url = f"{self.domain}/sitemap.xml"
        print("📌 Fetching sitemap URLs...")
        return self.sitemap_scraper.get_sitemap_urls(sitemap_url)

    def crawl_internal_links(self, max_pages=200):
        """Crawls internal links to find more pages."""
        print("🚀 Crawling internal links...")
        return self.link_crawler.crawl_internal_links(max_pages=max_pages)

    def process_website(self):
        """Orchestrates the full scraping process."""
        sitemap_urls = self.fetch_sitemap_urls()
        print(f"✅ Sitemap URLs Found: {len(sitemap_urls)}")

        crawled_urls = self.crawl_internal_links()
        print(f"✅ Crawled URLs Found: {len(crawled_urls)}")

        # Combine and store unique URLs
        all_urls = list(set(sitemap_urls + crawled_urls))
        self.scraped_urls = all_urls
        self.db_handler.save_urls(all_urls)

        print("🎯 URL Extraction Completed!")
    def save_urls_to_csv( self,filename="scraped_urls.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Scraped URLs"])  # Header
            for url in self.scraped_urls:
                writer.writerow([url])
        return filename  # Return filename for download handling
