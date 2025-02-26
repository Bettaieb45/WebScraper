### **🕸 WebScraper - A Smart Web Crawling & Sitemap Scraping Tool**  

#### **🚀 Overview**  
WebScraper is a powerful Python-based tool designed to **extract, crawl, and store URLs** from a website's sitemap and internal links. It automates the process of discovering web pages, making it easier to collect structured data for analysis, SEO audits, or competitive research.  

With its modular architecture, WebScraper provides:  
✔ **Sitemap Parsing** – Extract URLs directly from the `sitemap.xml`  
✔ **Internal Link Crawling** – Discover additional pages by following internal links  
✔ **MongoDB Integration** – Store extracted URLs in a **MongoDB** database  
✔ **Scalability** – Crawl up to **200+ pages** while ensuring efficient scraping  

---

### **🛠 Features**  
🔹 **Flexible & Modular** – Uses dependency injection, making it **easy to customize** or swap components  
🔹 **Optimized for Speed** – Efficiently extracts URLs without unnecessary processing  
🔹 **Designed for Scalability** – Crawl small and large sites effortlessly  
🔹 **Database Support** – Automatically saves extracted URLs in **MongoDB**  
🔹 **Human-Readable Logs** – Provides clear, structured feedback while scraping  

---



#### **🎯 What Happens?**
1️⃣ It **extracts URLs** from the sitemap  
2️⃣ It **crawls internal links** to discover additional pages  
3️⃣ It **stores all URLs** in a MongoDB database  

**Example Output:**  
```
📌 Fetching sitemap URLs...
✅ Sitemap URLs Found: 45
🚀 Crawling internal links...
✅ Crawled URLs Found: 155
🎯 URL Extraction Completed!
```

---


Modify the `WebScraper` parameters inside `WebScraper.py` to **adjust settings**:  
```python
scraper = WebScraper(
    domain="https://example.com", 
    max_pages=300  # Increase/decrease internal link crawling limit
)
```

---

### **⚡ Extending & Customizing**
Since WebScraper uses **dependency injection**, you can easily replace components:  

#### **Customizing the Database Handler**
Want to save URLs to **PostgreSQL** or **CSV** instead of MongoDB? Replace `MongoDBHandler` in `WebScraper.py` with your own class.

#### **Adjusting Crawling Logic**
Modify `InternalLinkCrawler.py` to follow specific rules (e.g., **avoid login pages** or **crawl only product pages**).  

---

### **🐞 Troubleshooting**
🔹 **Problem:** *Scraper stops after a few URLs*  
✅ Solution: Increase the `max_pages` limit in `InternalLinkCrawler.py`  

🔹 **Problem:** *MongoDB connection issues*  
✅ Solution: Ensure MongoDB is running and accessible. Check connection settings in `MongoDBHandler.py`

🔹 **Problem:** *Getting blocked by some websites*  
✅ Solution: Try using **request headers** or a **rotating proxy service** to bypass bot detection.

---

### **📜 License**
This project is licensed under the **MIT License** – free to use and modify! 🎉  

---

### **📞 Need Help?**
Feel free to open an **issue** on GitHub or reach out! 🚀  
