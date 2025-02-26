from scraper.WebScraper import WebScraper  

scraper = WebScraper("https://aziz-portfolio.com/")
scraper.process_website()
scraper.save_urls_to_csv("scraped_urls.csv")
print(scraper.scraped_urls)