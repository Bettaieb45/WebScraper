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
            # Create WebScraper only if not already existing
            if domain not in self.scrapers:
                self.scrapers[domain] = WebScraper(domain)

            # Now run the scrape
            scraper = self.scrapers[domain]
            scraper.process_website()
            return {"message": f"Scraping started for {domain}"}

        
        @self.app.post("/scrape-content/")
        def scrape_content(domain: str):
            """
            1) Make sure there's a WebScraper for the domain.
            2) Pass its db_handler into ContentScraper.
            3) Let ContentScraper process.
            """
            if domain not in self.scrapers:
                return {"error": f"No WebScraper found for {domain}; run /scrape/ first."}

            # If we haven't created a ContentScraper yet, do it now
            if domain not in self.content_scrapers:
                db_handler = self.scrapers[domain].db_handler
                self.content_scrapers[domain] = ContentScraper(domain, db_handler=db_handler)

            content_scraper = self.content_scrapers[domain]
            content_scraper.process_indexed_pages()
            return {"message": f"Content scraping started for {domain}"}
            
        @self.app.get("/website-name/")
        def get_website_name(domain: str):
            """Fetches the website name using WebScraper."""
            return {"website_name": self.scrapers[domain].website_name}

        @self.app.get("/scraped-urls/")
        def get_scraped_urls(domain: str):
            """
            Return scraped URLs for a domain using the ContentScraper's db_handler.
            """
            if domain not in self.content_scrapers:
                return {"error": "Domain not found in content scrapers. Run /scrape-content/ first."}

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
