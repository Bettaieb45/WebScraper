import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

###  Internal Link Crawler ###
class InternalLinkCrawler:
    """Crawls internal links dynamically using multithreading."""

    def __init__(self, domain):
        self.domain = domain

    def crawl_internal_links(self, max_pages=100):
        """Crawls internal links from a website."""
        visited = set()
        queue = [self.domain]

        def fetch_page(url):
            """Fetches and extracts internal links from a single page."""
            if url in visited or "#" in url:
                return []

            print(f"🔍 Crawling: {url}")
            visited.add(url)

            try:
                response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")

                new_links = []
                for link in soup.find_all("a", href=True):
                    new_url = urljoin(url, link["href"])
                    parsed_url = urlparse(new_url)

                    if parsed_url.netloc == urlparse(self.domain).netloc and new_url not in visited:
                        new_links.append(new_url)

                return new_links

            except Exception as e:
                print(f"⚠️ Failed to crawl {url}: {e}")
                return []

        # Use multithreading to speed up crawling
        with ThreadPoolExecutor(max_workers=16) as executor:
            while queue and len(visited) < max_pages:
                results = list(executor.map(fetch_page, queue[:16]))
                new_urls = [url for sublist in results for url in sublist]
                queue = new_urls

        return list(visited)

