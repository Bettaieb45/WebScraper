import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

###  Internal Link Crawler ###
class InternalLinkCrawler:
    """Crawls internal links dynamically using multithreading."""

    def __init__(self, domain):
        self.domain = self.remove_trailing_slash(domain)
        self.base_netloc = urlparse(self.domain).netloc

    def remove_trailing_slash(self, url):
        """Removes the trailing slash from a URL if present."""
        return url[:-1] if url.endswith("/") else url

    def normalize_url(self, base_url, link):
        """Ensures extracted URLs are absolute and prevents malformed URLs."""
        absolute_url = urljoin(base_url, link)
        parsed = urlparse(absolute_url)

        # Prevent self-referential and malformed URLs
        if not parsed.netloc or parsed.netloc != self.base_netloc:
            return None  # Ignore external links and empty URLs

        # Ensure URL does not contain repeating paths (fix infinite loop issue)
        path_parts = list(filter(None, parsed.path.split('/')))
        normalized_path = "/".join(path_parts[:5])  # Limit path depth to avoid looping

        normalized_url = f"{parsed.scheme}://{parsed.netloc}/{normalized_path}".rstrip("/")
        return normalized_url

    def fetch_page(self, url, visited):
        """Fetches and extracts internal links from a single page."""
        if url in visited or "#" in url:
            return []

        print(f"🔍 Crawling: {url}")
        visited.add(url)

        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                print(f"⚠️ Skipping {url} - Status Code: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")

            new_links = set()
            for link in soup.find_all("a", href=True):
                new_url = self.normalize_url(url, link["href"])
                if new_url and new_url not in visited:
                    new_links.add(new_url)

            return list(new_links)

        except Exception as e:
            print(f"⚠️ Failed to crawl {url}: {e}")
            return []

    def crawl_internal_links(self, max_pages=100):
        """Crawls internal links from a website."""
        visited = set()
        queue = [self.domain]

        with ThreadPoolExecutor(max_workers=16) as executor:
            while queue and len(visited) < max_pages:
                results = list(executor.map(lambda url: self.fetch_page(url, visited), queue[:16]))
                new_urls = [url for sublist in results for url in sublist if url not in visited]
                queue = new_urls

        return list(visited)
