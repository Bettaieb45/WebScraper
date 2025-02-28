from scraper.utils.get_website_name import get_website_name
from scraper.MongoDBHandler import MongoDBHandler
from pymongo import UpdateOne
from bs4 import BeautifulSoup
import requests
import csv
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading

class ContentScraper:
    def __init__(self, domain, db_handler=None):
        self.domain = domain
        self.website_name = get_website_name(domain)
        self.db_handler = db_handler or MongoDBHandler(self.website_name)
        self.scraped_urls = self.db_handler.fetch_scraped_urls()
        self.extracted_data = {}
        self.session = requests.Session()  # ✅ Reuse HTTP connections for faster requests
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

        # ✅ Lazy initialize Selenium (only when needed)
        self.driver_lock = threading.Lock()
        self._selenium_driver = None  

    def _get_selenium_driver(self):
        """Lazy initialization of Selenium WebDriver."""
        if self._selenium_driver is None:
            with self.driver_lock:  # Ensures only one instance is created
                if self._selenium_driver is None:
                    options = Options()
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--blink-settings=imagesEnabled=false")  # ✅ Disable images for faster rendering
                    
                    # ✅ Set Browserless authentication token
                    browserless_url = os.environ.get("BROWSER_WEBDRIVER_ENDPOINT")
                    browserless_token = os.environ.get("BROWSER_TOKEN")
                    remote_url = f"{browserless_url}/?token={browserless_token}"

                    self._selenium_driver = webdriver.Remote(
                        command_executor=remote_url,
                        options=options
                    )
        return self._selenium_driver

    def fetch_page_data(self, url):
        """Fetches metadata and heading count from a given URL, using Selenium as a fallback."""
        try:
            print(f"ℹ️ Fetching data for {url}...")
            response = self.session.get(url, timeout=10)

            if response.status_code == 404:
                print(f"⚠️ 404 detected for {url}, switching to Selenium...")
                return self._fetch_data_selenium(url)

            if response.status_code != 200:
                print(f"⚠️ Skipping {url} - Status Code: {response.status_code}")
                return None

            return self._extract_metadata(response.text, url)
        except Exception as e:
            print(f"⚠️ Failed to fetch data for {url}: {e}")
            return None

    def _fetch_data_selenium(self, url):
        """Fetches metadata using Selenium for JavaScript-heavy pages."""
        try:
            driver = self._get_selenium_driver()
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return self._extract_metadata(str(soup), url)
        except Exception as e:
            print(f"⚠️ Selenium failed for {url}: {e}")
            return None

    def _extract_metadata(self, html, url):
        """Extracts metadata and heading count from HTML content."""
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
        max_workers = min(32, os.cpu_count() + 4)  # ✅ Dynamically adjust worker count based on CPU

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
        """Closes the Selenium WebDriver."""
        if self._selenium_driver:
            self._selenium_driver.quit()
