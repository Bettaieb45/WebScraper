from scraper.utils.get_website_name import get_website_name
from scraper.MongoDBHandler import MongoDBHandler
from playwright.sync_api import sync_playwright
import csv
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class ContentScraper:
    def __init__(self, domain, db_handler=None):
        self.domain = domain
        self.website_name = get_website_name(domain)
        self.db_handler = db_handler or MongoDBHandler(self.website_name)
        self.scraped_urls = self.db_handler.fetch_scraped_urls()
        self.extracted_data = {}
        self._playwright = None  # Lazy initialization
        self.driver_lock = threading.Lock()
    
    def _get_playwright_browser(self):
        """Lazy initialization of Playwright Browser."""
        if self._playwright is None:
            with self.driver_lock:
                if self._playwright is None:
                    self._playwright = sync_playwright().start()
                    self.browser = self._playwright.chromium.launch(headless=True)
        return self.browser
    
    def fetch_page_data(self, url):
        """Fetches metadata and heading count using Playwright per thread instance."""
        print(f"ℹ️ Fetching data for {url}...")
        with sync_playwright() as p:  # Ensuring a new instance per thread
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            try:
                page.goto(url, timeout=10000)
                page.wait_for_load_state("networkidle")  # Wait for full page load
                html = page.content()
                return self._extract_metadata(html, url)
            except Exception as e:
                print(f"⚠️ Failed to fetch data for {url}: {e}")
                return None
            finally:
                page.close()
                browser.close()

    def _extract_metadata(self, html, url):
        """Extracts metadata and heading count from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        meta_title = soup.find("title").text if soup.find("title") else "N/A"
        meta_description = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_description["content"] if meta_description else "N/A"
        
        headings = [h for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]) if not h.find_parent(["header", "footer"])]
        heading_count = len(headings)
        
        print(f"✅ Fetched data for {url}!")
        return {"url": url, "meta_title": meta_title, "meta_description": meta_description, "heading_count": heading_count}
    
    def process_indexed_pages(self):
        """Processes only indexed URLs using optimized multithreading and updates MongoDB with metadata."""
        indexed_pages = [url for url, status in self.scraped_urls.items() if status.get("status") == "indexed"]
        print(f"ℹ️ Processing {len(indexed_pages)} indexed pages...")
        
        extracted_data = []
        max_workers = min(32, os.cpu_count() + 4)  # Dynamically adjust worker count
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_page_data, url): url for url in indexed_pages}
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    extracted_data.append(result)
        
        print(f"✅ Metadata fetched for {len(extracted_data)} indexed pages!")
        
        if extracted_data:
            self.db_handler.update_metadata(extracted_data)
            print(f"✅ Metadata updated for {len(extracted_data)} indexed pages!")
        else:
            print("⚠️ No metadata to update in MongoDB!")
    
    def generate_extracted_data_csv(self):
        """Generates CSV data dynamically without storing it."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        data = self.db_handler.fetch_scraped_urls()
        all_keys = {key for entry in data.values() for key in entry.keys()}
        all_keys.update(["status"])
        all_keys = sorted(all_keys)
        
        writer.writerow(["URL"] + all_keys)
        
        for url, entry in data.items():
            row = [url] + [entry.get(key, "N/A") for key in all_keys]
            writer.writerow(row)
        
        return output.getvalue()
    
    def close(self):
        """Closes the Playwright Browser."""
        if self._playwright:
            self.browser.close()
            self._playwright.stop()
