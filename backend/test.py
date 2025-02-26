from scraper.WebScraper import WebScraper  

scraper = WebScraper("https://aloa.co/")
scraper.process_website()
print(scraper.scraped_urls)