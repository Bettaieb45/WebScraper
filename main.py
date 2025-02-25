from fastapi import FastAPI
from scraper.WebScraper import WebScraper  # Import your WebScraper class
from fastapi.middleware.cors import CORSMiddleware

class WebScraperAPI:
    """A class-based FastAPI app that manages the web scraping process."""

    def __init__(self):
        self.app = FastAPI(title="Web Scraper API", version="1.0")
        self.scrapers = {}  # Dictionary to store WebScraper instances
        self.app.add_middleware(  # Add CORS middleware
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Register routes
        self.setup_routes()

    def setup_routes(self):
        """Define API endpoints."""

        @self.app.get("/")
        def home():
            return {"message": "Welcome to the Web Scraper API!"}

        @self.app.post("/scrape/")
        def scrape_website(domain: str):
            """Creates a WebScraper instance and stores it."""
            if domain not in self.scrapers:
                self.scrapers[domain] = WebScraper(domain)  # Store scraper instance

            scraper = self.scrapers[domain]
            scraper.process_website()
            return {"message": f"Scraping started for {domain}"}

        @self.app.get("/website-name/")
        def get_website_name(domain: str):
            """Fetches the website name using WebScraper."""
            return {"website_name": self.scrapers[domain].website_name}

        @self.app.get("/scraped-urls/")
        def get_scraped_urls(domain: str):
            """Retrieves scraped URLs from MongoDB."""
            if domain not in self.scrapers:
                return {"error": "Domain not found. Run /scrape/ first."}
            
            scraper = self.scrapers[domain]
            urls = scraper.scraped_urls
            return {"scraped_urls": urls}

    def get_app(self):
        """Returns the FastAPI instance."""
        return self.app

# Create API instance
web_scraper_api = WebScraperAPI()
app = web_scraper_api.get_app()
