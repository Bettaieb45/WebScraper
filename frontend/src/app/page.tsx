"use client";

import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

export default function Home() {
  const [domain, setDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [urls, setUrls] = useState<string[]>([]);
  const [error, setError] = useState("");

  const BASE_URL = "http://127.0.0.1:8000"; // Change this if your API is deployed

  const handleScrape = async () => {
    if (!domain.trim()) return;
    
    setLoading(true);
    setError("");
    setUrls([]);

    try {
      // Start scraping
      await axios.post(`${BASE_URL}/scrape/`, null, { params: { domain } });

      // Wait for a short delay to allow scraping to process
      setTimeout(async () => {
        // Fetch scraped URLs
        const res = await axios.get(`${BASE_URL}/scraped-urls/`, { params: { domain } });
        setUrls(res.data.scraped_urls || []);
      }, 5000);
    } catch (err) {
      setError("Failed to scrape the website. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white px-4">
      <motion.h1 
        className="text-4xl font-bold mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        🌐 Web Scraper
      </motion.h1>

      <div className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-lg">
        <input
          type="text"
          placeholder="Enter website URL..."
          className="w-full p-3 rounded-lg text-black"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <button
          onClick={handleScrape}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg"
          disabled={loading}
        >
          {loading ? "Scraping..." : "Start Scraping"}
        </button>
      </div>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {loading && (
        <motion.div 
          className="mt-6 text-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: "mirror" }}
        >
          ⏳ Scraping in progress...
        </motion.div>
      )}

      {!loading && urls.length > 0 && (
        <motion.div 
          className="mt-6 w-full max-w-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-xl font-semibold mb-3">🔗 Scraped URLs:</h2>
          <ul className="bg-gray-800 p-4 rounded-lg overflow-hidden">
            {urls.map((url, index) => (
              <motion.li
                key={index}
                className="py-2 border-b border-gray-600 last:border-none"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <a href={url} className="text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">
                  {url}
                </a>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </main>
  );
}
