import requests
from bs4 import BeautifulSoup
from scraper.MongoDBHandler import MongoDBHandler
from scraper.SitemapScraper import SitemapScraper
from scraper.InternalLinkCrawler import InternalLinkCrawler
### 4️⃣ WebScraper Coordinator ###
class WebScraper:
    """Coordinates the entire scraping process."""

    def __init__(self, domain):
        self.domain = self.remove_trailing_slash(domain)
        self.website_name = self.get_website_name()
        self.db_handler = MongoDBHandler(self.website_name)
        self.sitemap_scraper = SitemapScraper(self.domain)
        self.link_crawler = InternalLinkCrawler(self.domain)
        self.scraped_urls = []

    def get_website_name(self):
        """Extracts the name of the website from the domain and formats it."""
        #exclude https and .com or anything after . for getting the name 
        return self.domain.replace("https://", "").replace("http://", "").split(".")[0]

    def remove_trailing_slash(self, url):
        """Removes the trailing slash from a URL."""
        return url[:-1] if url.endswith("/") else url

    def process_website(self):
        """Extracts URLs from the sitemap and crawls internal links."""
        sitemap_url = f"{self.domain}/sitemap.xml"

        print("📌 Fetching sitemap URLs...")
        sitemap_urls = self.sitemap_scraper.get_sitemap_urls(sitemap_url)
        print(f"✅ Sitemap URLs Found: {len(sitemap_urls)}")

        print("🚀 Crawling internal links to find more pages...")
        crawled_urls = self.link_crawler.crawl_internal_links(max_pages=200)
        print(f"✅ Crawled URLs Found: {len(crawled_urls)}")

        # Combine & store unique URLs
        all_urls = list(set(sitemap_urls + crawled_urls))
        self.scraped_urls = all_urls
        self.db_handler.save_urls(all_urls)
        print("🎯 URL Extraction Completed!")
