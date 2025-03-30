import requests
from bs4 import BeautifulSoup
from scraper.MongoDBHandler import MongoDBHandler
from scraper.SitemapScraper import SitemapScraper
from scraper.InternalLinkCrawler import InternalLinkCrawler
from scraper.RobotsTxt import RobotsTxt
from urllib.parse import urlparse
import csv
from scraper.utils.get_website_name import get_website_name
class WebScraper:
    """Coordinates the entire scraping process."""

    def __init__(self, domain, db_handler=None, sitemap_scraper=None, link_crawler=None,robots_txt=None):
        self.domain = self.remove_trailing_slash(domain)
        self.website_name = get_website_name(domain)

        # Use dependency injection for flexibility and testing
        self.db_handler = db_handler or MongoDBHandler(self.website_name)
        self.sitemap_scraper = sitemap_scraper or SitemapScraper(self.domain)
        self.link_crawler = link_crawler or InternalLinkCrawler(self.domain)
        self.robots_txt = robots_txt or RobotsTxt(self.domain)
        

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
        all_urls = self.get_all_urls_dict(sitemap_urls,crawled_urls)
        print(f"✅ Total URLs Found: {len(all_urls)}")
        self.scraped_urls = all_urls
        self.db_handler.save_urls(self.scraped_urls)

        print("🎯 URL Extraction Completed!")
    def save_urls_to_csv(self, filename="scraped_urls.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Indexed Status"])  # Header
            for url, status in self.scraped_urls.items():
                writer.writerow([url, status])  # Write both URL and status
        return filename  # Return filename for download handling

    def get_robot_paths(self):
        """Fetches all URLs from a robot.txt"""
        return self.robots_txt.get_robot_paths()
    def is_disallowed(self, url, disallowed_paths):
        """Check if a URL is disallowed based on robots.txt rules."""
        parsed_url_path = urlparse(url).path  # Extract only the path part of the URL
        
        for path in disallowed_paths:
            if parsed_url_path.startswith(path.rstrip('/')):  # Check if URL starts with disallowed path
                return True  # URL should be excluded

        return False  # URL is allowed  
    def remove_backslash(self,url):
        """Removes the trailing slash from a URL."""
        return url[:-1] if url.endswith("/") else url
    
    def get_all_urls_dict(self, sitemap_urls, internal_urls):
        """Combines sitemap and internal URLs into a single dictionary, ensuring proper indexing status."""
        all_urls = {}

        # Fetch disallowed paths from robots.txt
        exclude_paths = self.get_robot_paths()

        # Mark sitemap URLs as indexed, but verify with robots.txt
        for url in sitemap_urls:
            url=self.remove_backslash(url)
            if self.is_disallowed(url, exclude_paths):
                all_urls[url] = "non-indexed"
            else:
                all_urls[url] = "indexed"

        # Mark internal URLs as non-indexed only if they are not already indexed
        for url in internal_urls:
            url=self.remove_backslash(url)
            if url not in all_urls:
                all_urls[url] = "non-indexed"

        return all_urls
