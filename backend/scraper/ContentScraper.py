import asyncio
import random
from scraper.utils.get_website_name import get_website_name
from scraper.MongoDBHandler import MongoDBHandler
from scraper.MetadataScraper import MetadataScraper
from scraper.InternalLinkGraphBuilder import InternalLinkGraphBuilder
from scraper.NavigationLinkFilter import NavigationLinkFilter
from playwright.async_api import async_playwright

class ScrapeRunner:
    def __init__(self, domain, concurrency=5):
        self.domain = domain
        self.website_name = get_website_name(domain)
        self.database = MongoDBHandler(self.website_name)
        self.scraped_urls = list(self.database.fetch_scraped_urls().keys())
        self.nav_filter = NavigationLinkFilter(domain)
        self.concurrency = concurrency

    async def _analyze_nav_links(self, browser):
        print("🔍 Sampling pages to detect navigational link patterns...")
        sample_urls = random.sample(self.scraped_urls, min(20, len(self.scraped_urls)))

        for i, url in enumerate(sample_urls, 1):
            try:
                print(f"📄 Analyzing sample page {i}: {url}")
                page = await browser.new_page()
                await page.route("**/*", lambda route, request: 
                    route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
                )
                await page.goto(url, wait_until="domcontentloaded", timeout=0)
                html = await page.content()
                self.nav_filter.analyze_page(html)
                await page.close()
            except Exception as e:
                print(f"⚠️ Failed to analyze sample page {url}: {e}")

        self.nav_filter.finalize()

    async def run(self):
        scraped_metadata = []
        sem = asyncio.Semaphore(self.concurrency)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            # Step 1: Analyze header/footer nav patterns
            await self._analyze_nav_links(browser)

            # Step 2: Init scraper with nav_filter
            self.scraper = MetadataScraper(self.domain, self.nav_filter)

            async def scrape_url(url):
                async with sem:
                    try:
                        print(f"🔍 Scraping {url}")
                        data = await self.scraper.scrape(browser, url)
                        scraped_metadata.append(data)
                    except Exception as e:
                        print(f"❌ Failed to scrape {url}: {e}")

            await asyncio.gather(*(scrape_url(url) for url in self.scraped_urls))
            await browser.close()

        # Step 3: Count internal links
        graph_builder = InternalLinkGraphBuilder(scraped_metadata)
        link_counts = graph_builder.build_internal_link_counts()

        for data in scraped_metadata:
            data["internal_link_count"] = link_counts.get(data["url"], 0)

        # Step 4: Save to DB
        if scraped_metadata:
            self.database.update_metadata(scraped_metadata)
        else:
            print("⚠️ No metadata to update in MongoDB!")
