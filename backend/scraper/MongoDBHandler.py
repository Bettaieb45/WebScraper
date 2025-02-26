from pymongo import MongoClient, UpdateOne
import os
from dotenv import load_dotenv
load_dotenv()
###  MongoDB Handler ###
class MongoDBHandler:
    """Handles MongoDB connection and URL storage."""
    
    def __init__(self, website_name):
        """Initialize MongoDB connection."""
        MONGO_URI = os.getenv("MONGO_URI")
        if not MONGO_URI:
            raise ValueError("MongoDB URI is missing!")
        
        client = MongoClient(MONGO_URI)
        db_name = website_name + '_db'
        db = client[db_name]
        self.collection = db["scraped_urls"]

    def save_urls(self, urls):
        """Saves URLs to MongoDB efficiently using bulk insert with upsert."""
        if not urls:
            print("⚠️ No URLs to store in MongoDB!")
            return

        unique_urls = list(set(urls))  # Remove duplicates
        operations = [
            UpdateOne({"url": url}, {"$setOnInsert": {"url": url}}, upsert=True)
            for url in unique_urls if "#" not in url
        ]

        if operations:
            result = self.collection.bulk_write(operations)
            print(f"✅ {result.upserted_count} new URLs stored in MongoDB!")
   

    