from fastapi import FastAPI
from scraper.WebScraper import WebScraper 
from fastapi.middleware.cors import CORSMiddleware
from scraper.ContentScraper import ContentScraper
import io
import csv
from fastapi.responses import Response
class WebScraperAPI:
    """A class-based FastAPI app that manages the web scraping process."""

    def __init__(self):
        self.app = FastAPI(title="Web Scraper API", version="1.0")
        self.scrapers = {}  # Dictionary to store WebScraper instances
        self.content_scrapers = {}  # Dictionary to store ContentScraper instances
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
        
        @self.app.post("/scrape-content/")
        def scrape_content(domain: str):
            """Creates a ContentScraper instance and stores it."""
            if domain not in self.content_scrapers:
                self.content_scrapers[domain] = ContentScraper(domain)
            content_scraper = self.content_scrapers[domain]
            content_scraper.process_indexed_pages()
            
        @self.app.get("/website-name/")
        def get_website_name(domain: str):
            """Fetches the website name using WebScraper."""
            return {"website_name": self.scrapers[domain].website_name}

        @self.app.get("/scraped-urls/")
        def get_scraped_urls(domain: str):
            """Retrieves scraped URLs from MongoDB."""
            if domain not in self.content_scrapers:
                return {"error": "Domain not found. Run /scrape/ first."}
            
            content_scraper = self.content_scrapers[domain]
            urls = content_scraper.db_handler.fetch_scraped_urls()
            return {"scraped_urls": urls}
        @self.app.get("/download-csv/")
        def download_csv(domain: str):
            """Dynamically generates and returns extracted data CSV."""
            if domain not in self.content_scrapers:
                return {"error": "Domain not found. Run /scrape/ first."}
            content_scraper = self.content_scrapers[domain]
            csv_content = content_scraper.generate_extracted_data_csv()
            response = Response(content=csv_content,media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename={domain}_extracted_data.csv"
            return response
            
        
    def get_app(self):
        """Returns the FastAPI instance."""
        return self.app

# Create API instance
web_scraper_api = WebScraperAPI()
app = web_scraper_api.get_app()
