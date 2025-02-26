"use client";

import { useState } from "react";
import axios from "axios";

interface ScraperFormProps {
  onScrapeComplete: (urls: string[]) => void;
  onLoadingChange: (loading: boolean) => void;
}

export default function ScraperForm({ onScrapeComplete, onLoadingChange }: ScraperFormProps) {
  const [domain, setDomain] = useState("");
  const [error, setError] = useState("");

  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleScrape = async () => {
    if (!domain.trim()) return;

    setError("");
    onScrapeComplete([]); // Reset previous results
    onLoadingChange(true); // Start loading state

    try {
      await axios.post(`${BASE_URL}/scrape/`, null, { params: { domain } });

      setTimeout(async () => {
        const res = await axios.get(`${BASE_URL}/scraped-urls/`, { params: { domain } });
        onScrapeComplete(res.data.scraped_urls || []);
      }, 5000);
    } catch (error) {
      console.error("❌ Scraper Error:", axios.isAxiosError(error) ? error.response?.data || error.message : error);
      setError("Failed to scrape the website. Please try again.");
    } finally {
      onLoadingChange(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 w-full max-w-lg">
      <input
        type="text"
        placeholder="Enter website URL..."
        className="w-full p-3 rounded-lg text-black border border-gray-400 focus:outline-none focus:border-blue-500"
        value={domain}
        onChange={(e) => setDomain(e.target.value)}
      />
      <button
        onClick={handleScrape}
        className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 shadow-lg"
      >
        Start Scraping
      </button>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>
  );
}
