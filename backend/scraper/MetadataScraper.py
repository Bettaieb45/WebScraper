from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.async_api import Browser, Page
from typing import Optional
from scraper.NavigationLinkFilter import NavigationLinkFilter  # Import your filter class

class MetadataScraper:
    def __init__(self, base_domain: str, nav_filter: Optional[NavigationLinkFilter] = None):
        self.base_domain = urlparse(base_domain).netloc
        self.nav_filter = nav_filter

    async def scrape(self, browser: Browser, url: str) -> dict:
        page: Page = await browser.new_page()

        # 🚫 Block unnecessary resources
        await page.route("**/*", lambda route, request: 
            route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
        )

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=0)
        except Exception as e:
            print(f"❌ Failed to load {url}: {e}")
            await page.close()
            return {
                "url": url,
                "title": None,
                "meta_description": None,
                "headings": {},
                "links_to": []
            }

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        # ✅ Title and meta description
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc['content'].strip() if meta_desc and meta_desc.has_attr('content') else None

        # ✅ Headings count
        headings = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}

        # ✅ Internal links (with nav path filtering)
        all_links = soup.find_all("a", href=True)
        links_to = []
        skipped_nav = 0

        for a in all_links:
            href = a['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.netloc != self.base_domain:
                continue  # external link

            if self.nav_filter:
                dom_path = self.nav_filter.get_dom_path(a)
                if self.nav_filter.is_navigational(dom_path):
                    skipped_nav += 1
                    continue

            cleaned_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            links_to.append(cleaned_url)

        await page.close()

        print(f"✅ Scraped {url} — {len(links_to)} internal links kept, {skipped_nav} skipped as navigation.\n")

        return {
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "headings": headings,
            "links_to": list(set(links_to))
        }
