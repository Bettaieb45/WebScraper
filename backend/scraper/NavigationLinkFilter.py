from collections import defaultdict
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class NavigationLinkFilter:
    def __init__(self, base_domain: str):
        self.base_domain = urlparse(base_domain).netloc
        self.dom_path_counts = defaultdict(int)
        self.nav_paths = set()
        self.page_count = 0

    def get_dom_path(self, element) -> str:
        path = []
        while element and element.name:
            path.insert(0, element.name)
            element = element.parent
        return " > ".join(path)

    def analyze_page(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all("a", href=True)
        seen_paths = set()

        for a in links:
            href = a['href']
            parsed_href = urlparse(href)
            if parsed_href.netloc and parsed_href.netloc != self.base_domain:
                continue

            dom_path = self.get_dom_path(a)
            seen_paths.add(dom_path)

        for path in seen_paths:
            self.dom_path_counts[path] += 1

        self.page_count += 1
        print(f"📄 Analyzed page {self.page_count}, found {len(seen_paths)} unique DOM paths")

    def finalize(self, threshold=0.8):
        print("\n🔍 Finalizing navigation pattern detection...")
        print(f"Total pages analyzed: {self.page_count}")
        for path, count in sorted(self.dom_path_counts.items(), key=lambda x: -x[1]):
            frequency = count / self.page_count
            print(f"    Path: {path}  —  Appears in {frequency:.2%} of pages")
            if frequency >= threshold:
                self.nav_paths.add(path)

        print(f"\n✅ {len(self.nav_paths)} DOM paths classified as navigational.\n")

    def is_navigational(self, dom_path: str) -> bool:
        return dom_path in self.nav_paths
