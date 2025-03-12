import logging
import os
import io
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from scraper.utils.get_website_name import get_website_name

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ContentScraper:
    def __init__(self, domain, db_handler=None):
        self.domain = domain
        self.website_name = get_website_name(domain)
        self.db_handler = db_handler  
        self._playwright = None
        self.driver_lock = threading.Lock()

        # Dictionary of all URL info from DB
        self.scraped_urls = self.db_handler.fetch_scraped_urls() if self.db_handler else {}
        # Will store repeated block signatures (for quick removal later)
        self.repeated_block_signatures = set()
        
        logger.info(f"Initialized ContentScraper for domain: {domain}")

    def _get_playwright_browser(self):
        """Lazy initialization of Playwright Browser."""
        if self._playwright is None:
            with self.driver_lock:
                if self._playwright is None:
                    self._playwright = sync_playwright().start()
                    self.browser = self._playwright.chromium.launch(headless=True)
        return self.browser

    def fetch_page_data(self, url):
        """
        Fetches DOM for a single page in a separate thread.
        Then removes repeated blocks from the DOM, extracts metadata.
        """
        logger.info(f"[fetch_page_data] Fetching data for {url} ...")
        # Use a separate Playwright instance per thread to avoid concurrency issues
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=0)  
                page.wait_for_load_state("domcontentloaded")
                html = page.content()
                page.close()
                browser.close()

            # Now parse the HTML and remove repeated blocks
            soup = BeautifulSoup(html, "html.parser")
            self._remove_repeated_blocks(soup)

            # Extract metadata from the pruned HTML
            result = self._extract_metadata(soup, url)
            logger.info(f"[fetch_page_data] Successfully extracted data for {url}.")
            return result

        except Exception as e:
            logger.warning(f"[fetch_page_data] Failed to fetch data for {url}: {e}")
            return None

    def _extract_metadata(self, soup, url):
        """
        Extracts meta title, meta description, heading count,
        and internal links from the pruned DOM soup.
        """
        # Meta Title
        title_tag = soup.find("title")
        meta_title = title_tag.text.strip() if title_tag else "N/A"

        # Meta Description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = (desc_tag["content"].strip() 
                            if desc_tag and desc_tag.has_attr("content") else "N/A")

        # Headings count
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        heading_count = len(headings)

        # Internal link detection
        all_links = soup.find_all("a", href=True)
        domain_netloc = urlparse(self.domain).netloc.lower()

        internal_links = []
        for link in all_links:
            href = link["href"].strip()

            # Skip anchor links, mailto:, tel:, or empty
            if (href.startswith("#") or 
                href.startswith("mailto:") or 
                href.startswith("tel:") or 
                not href):
                continue

            parsed = urlparse(href)
            link_domain = parsed.netloc.lower()
            scheme = parsed.scheme.lower()

            # If netloc is empty (relative URL), treat as internal
            # But also skip if it's something like "javascript:..."
            if not link_domain:
                # If the scheme is something odd like 'javascript', skip
                if scheme in ["", "http", "https"]:
                    internal_links.append(href)
            else:
                # If it has the same domain and scheme is http/https, keep it
                if link_domain == domain_netloc and scheme in ["http", "https"]:
                    internal_links.append(href)

        internal_link_count = len(internal_links)

        return {
            "url": url,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "heading_count": heading_count,
            "internal_link_count": internal_link_count,
            "internal_links": internal_links, 
        }



    def process_indexed_pages(self):
        """
        1) Identify repeated blocks by analyzing a sample of pages.
        2) Fetch the content for each indexed page (threaded).
        3) Update MongoDB with extracted metadata.
        """
        logger.info("[process_indexed_pages] Starting processing of indexed pages.")

        # 1. Identify repeated blocks
        indexed_pages = [u for (u, data) in self.scraped_urls.items() if data.get("status") == "indexed"]
        if not indexed_pages:
            logger.warning("[process_indexed_pages] No indexed pages found in DB.")
            return

        # We'll pick a sample to do repeated-block detection (e.g., up to 20 pages)
        sample_size = min(len(indexed_pages), 20)
        sample_pages = indexed_pages[:sample_size]
        if sample_size > 1:
            logger.info(f"[process_indexed_pages] Sampling {sample_size} pages to detect repeated blocks.")
            self._detect_repeated_subtrees(sample_pages)
        else:
            logger.info("[process_indexed_pages] Only one indexed page. Skipping repeated-block detection.")

        # 2. Fetch the content for each indexed page concurrently
        logger.info(f"[process_indexed_pages] Fetching content for {len(indexed_pages)} indexed pages (threaded).")
        extracted_data = []
        max_workers = min(32, os.cpu_count() + 4)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_page_data, url): url for url in indexed_pages}
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    extracted_data.append(result)

        # 3. Update MongoDB
        logger.info(f"[process_indexed_pages] Fetched data for {len(extracted_data)} pages. Updating DB.")
        if extracted_data and self.db_handler:
            self.db_handler.update_metadata(extracted_data)
        logger.info("[process_indexed_pages] Finished processing indexed pages.")

    def generate_extracted_data_csv(self):
        """Generates a CSV string of all stored (and updated) data from MongoDB."""
        if not self.db_handler:
            logger.error("[generate_extracted_data_csv] No DB handler provided.")
            return ""

        logger.info("[generate_extracted_data_csv] Generating CSV data.")
        data = self.db_handler.fetch_scraped_urls()
        # Collect all possible keys (besides URL) for columns
        all_keys = set()
        for entry in data.values():
            all_keys.update(entry.keys())
        all_keys.discard("url")  # We'll put URL in the first column
        all_keys = sorted(all_keys)

        # Create CSV in-memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["URL"] + all_keys)

        for url, entry in data.items():
            row = [url] + [entry.get(k, "N/A") for k in all_keys]
            writer.writerow(row)

        csv_content = output.getvalue()
        logger.info("[generate_extracted_data_csv] CSV generation complete.")
        return csv_content

    def close(self):
        """Cleans up the Playwright browser if in use."""
        logger.info("[close] Closing Playwright browser context if open.")
        if self._playwright:
            self.browser.close()
            self._playwright.stop()


    def _detect_repeated_subtrees(self, sample_pages):
        """
        Simple repeated-block detection.
        1) For each page in sample, parse the top-level DOM structure.
        2) Compute signatures for direct child blocks of <body>.
        3) Count how often each signature appears.
        4) If a block appears in = 100% of pages, consider it repeated.
    
        """
        
        logger.info("[_detect_repeated_subtrees] Detecting repeated blocks from sample pages.")
        block_counts = {}

        # Quick fetch of HTML for each sample page
        for url in sample_pages:
            try:
                with sync_playwright() as p:
                    b = p.chromium.launch(headless=True)
                    c = b.new_context()
                    pg = c.new_page()
                    pg.goto(url, timeout=0)
                    pg.wait_for_load_state("domcontentloaded")
                    html = pg.content()
                    pg.close()
                    b.close()

                soup = BeautifulSoup(html, "html.parser")
                body = soup.find("body")
                if not body:
                    continue

                # For each direct child of <body>, compute a signature
                for child in body.find_all(recursive=False):
                    sig = self._compute_block_signature(child)
                    if sig:
                        block_counts[sig] = block_counts.get(sig, 0) + 1

            except Exception as e:
                logger.warning(f"[_detect_repeated_subtrees] Error sampling {url}: {e}")

        threshold = int(len(sample_pages) * 1)  # 100% of sample pages
        for sig, count in block_counts.items():
            if count >= threshold:
                self.repeated_block_signatures.add(sig)

        logger.info(f"[_detect_repeated_subtrees] Found {len(self.repeated_block_signatures)} repeated block signatures.")

    def _compute_block_signature(self, element):
        """
        Compute a simplified signature of a DOM block:
         - tag name
         - immediate child structure
         - textual or link density cues
         - any semantic cues in class/id names
        """
        tag_name = element.name
        child_tags = [child.name for child in element.find_all(recursive=False)]
        class_names = element.get("class", [])
        id_name = element.get("id", "")

        # Some heuristics: link density
        links = element.find_all("a")
        link_count = len(links)
        text_length = len(element.get_text(strip=True))

        # A naive signature: combine tag structure, plus link density
        signature = f"{tag_name}|{child_tags}|classes:{class_names}|id:{id_name}|links:{link_count}|textlen:{text_length//50}"
        return signature

    def _remove_repeated_blocks(self, soup):
        """
        Removes blocks from the soup if they match any 'repeated_block_signatures'
        discovered by _detect_repeated_subtrees.
        """
        if not self.repeated_block_signatures:
            # If we have no info about repeated blocks, there's nothing to remove
            return

        body = soup.find("body")
        if not body:
            return

        # Check each direct child of <body> again
        children = body.find_all(recursive=False)
        for child in children:
            sig = self._compute_block_signature(child)
            if sig in self.repeated_block_signatures:
                child.decompose()  # Remove from DOM
