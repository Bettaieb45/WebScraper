from scraper.ContentScraper import ContentScraper  

scraper = ContentScraper("https://caffia.com")
scraper.process_indexed_pages()
print(scraper.generate_extracted_data_csv())
