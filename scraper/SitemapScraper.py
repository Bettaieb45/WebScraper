import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

###  Sitemap Scraper ###
class SitemapScraper:
    """Fetches all URLs from a sitemap, including nested sitemaps (parallel processing)."""

    def __init__(self, domain):
        self.domain = domain

    def get_sitemap_urls(self, sitemap_url):
        """Fetches all URLs from a sitemap, including nested sitemaps."""
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch sitemap: {sitemap_url}")
                return []

            root = ET.fromstring(response.content)
            namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            urls = []
            nested_sitemaps = []

            for elem in root.findall(f".//{namespace}loc"):
                url = elem.text
                if url.endswith(".xml"):
                    nested_sitemaps.append(url)  # Collect nested sitemaps
                else:
                    urls.append(url)

            # Fetch nested sitemaps in parallel
            with ThreadPoolExecutor(max_workers=8) as executor:
                results = executor.map(self.get_sitemap_urls, nested_sitemaps)
                for result in results:
                    urls.extend(result)

            return urls

        except Exception as e:
            print(f"⚠️ Error fetching sitemap: {e}")
            return []

