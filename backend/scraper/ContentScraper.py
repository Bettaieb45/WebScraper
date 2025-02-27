from scraper.utils.get_website_name import get_website_name
from scraper.MongoDBHandler import MongoDBHandler
from pymongo import UpdateOne
from bs4 import BeautifulSoup
import requests
import csv
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

class ContentScraper:
    def __init__(self, domain, db_handler=None):
        self.domain = domain
        self.website_name = get_website_name(domain)
        self.db_handler = db_handler or MongoDBHandler(self.website_name)
        self.scraped_urls = self.db_handler.fetch_scraped_urls()
        self.extracted_data = {}

    def fetch_page_data(self, url):
        """Fetches metadata and heading count from a given URL."""
        try:
            print(f"ℹ️ Fetching data for {url}...")
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"⚠️ Skipping {url} - Status Code: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")
            meta_title = soup.find("title").text if soup.find("title") else "N/A"
            meta_description = soup.find("meta", attrs={"name": "description"})
            meta_description = meta_description["content"] if meta_description else "N/A"

            # Count heading tags excluding header/footer
            headings = [h for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]) if not h.find_parent(["header", "footer"])]
            heading_count = len(headings)

            return {"url": url, "meta_title": meta_title, "meta_description": meta_description, "heading_count": heading_count}
        except Exception as e:
            print(f"⚠️ Failed to fetch data for {url}: {e}")
            return None

    def process_indexed_pages(self, max_workers=10):
        """Processes only indexed URLs using multithreading and updates MongoDB with metadata."""
        indexed_pages = [url for url, status in self.scraped_urls.items() if status.get("status") == "indexed"]
        print(f"ℹ️ Processing {len(indexed_pages)} indexed pages...")

        extracted_data = []

        # ✅ Use ThreadPoolExecutor for parallel requests
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

        # Fetch scraped data
        data = self.db_handler.fetch_scraped_urls()

        # Determine all possible fields dynamically
        all_keys = set()
        for entry in data.values():
            all_keys.update(entry.keys())

        # Ensure URL and Status are always included
        all_keys.update(["status"])
        all_keys = sorted(all_keys)  # Sort for consistency

        # Write CSV header
        writer.writerow(["URL"] + all_keys)

        # Write CSV rows
        for url, entry in data.items():
            row = [url] + [entry.get(key, "N/A") for key in all_keys]
            writer.writerow(row)

        return output.getvalue()  # Return CSV content as string
