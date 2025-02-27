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
        # Check if the collection is empty and prompt to scrape first
        if self.collection.count_documents({}) == 0:
            print(f"⚠️ No data found in MongoDB for {website_name}. Please scrape first!")

    def save_urls(self, url_data):
        if not url_data:
            print("⚠️ No URLs to store in MongoDB!")
            return

        operations = [
            UpdateOne({"url": url}, {"$set": {"status": status}}, upsert=True)
            for url, status in url_data.items()
        ]

        if operations:
            result = self.collection.bulk_write(operations)
            print(f"✅ {result.upserted_count} new URLs stored in MongoDB!")

    def fetch_scraped_urls(self):
        """Fetch all scraped URLs and their metadata from MongoDB dynamically."""
        projection = {"_id": 0}  # Dynamically include all fields except _id
        return {
            entry.pop("url"): entry  # Remove "url" from values and use it as key
            for entry in self.collection.find({}, projection)
        }

    
    def update_metadata(self, metadata_list):
        """Updates MongoDB with metadata including title, description, and heading count."""
        if not metadata_list:
            print("⚠️ No metadata to update in MongoDB!")
            return

        operations = [
            UpdateOne({"url": data["url"]}, {"$set": data}, upsert=True)
            for data in metadata_list
        ]

        if operations:
            result = self.collection.bulk_write(operations)
            print(f"✅ {result.upserted_count} pages updated with metadata in MongoDB!")
    