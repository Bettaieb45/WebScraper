from scraper.WebScraper import WebScraper
# Run the script
if __name__ == "__main__":
    domain = input("Enter the website domain (e.g., https://example.com): ").strip()
    scraper = WebScraper(domain)
    scraper.process_website()
