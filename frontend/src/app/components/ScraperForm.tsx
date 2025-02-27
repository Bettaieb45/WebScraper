"use client";

import { useState } from "react";
import axios from "axios";

// Define the expected structure for scraped URLs
interface ScrapedUrlData {
  status: string;
  meta_title?: string;
  meta_description?: string;
  heading_count?: number;
}

interface ScraperFormProps {
  onScrapeComplete: (urls: Record<string, ScrapedUrlData>, domain: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export default function ScraperForm({ onScrapeComplete, onLoadingChange }: ScraperFormProps) {
  const [domain, setDomain] = useState("");
  const [error, setError] = useState("");

  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleScrape = async () => {
    if (!domain.trim()) return;

    setError("");
    onScrapeComplete({}, ""); // ✅ Reset previous results (empty dictionary)
    onLoadingChange(true); // ✅ Start loading state

    try {
      // Step 1: Start website scraping
      await axios.post(`${BASE_URL}/scrape/`, null, { params: { domain } });

      // Step 2: Wait for scraping to complete
      await new Promise((resolve) => setTimeout(resolve, 5000));

      // Step 3: Start content scraping
      await axios.post(`${BASE_URL}/scrape-content/`, null, { params: { domain } });

      // Step 4: Wait for content scraping to complete
      await new Promise((resolve) => setTimeout(resolve, 5000));

      // Step 5: Fetch the final scraped URLs
      const res = await axios.get(`${BASE_URL}/scraped-urls/`, { params: { domain } });

      // ✅ Ensure response is correctly structured as a dictionary
      const urlsDict: Record<string, ScrapedUrlData> = res.data.scraped_urls || {};

      onScrapeComplete(urlsDict, domain); // ✅ Pass dictionary instead of an array
    } catch (error) {
      console.error("❌ Scraper Error:", axios.isAxiosError(error) ? error.response?.data || error.message : error);
      setError("Failed to scrape the website. Please try again.");
    } finally {
      onLoadingChange(false);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-center sm:items-stretch gap-3 w-full max-w-lg">
      <input
        type="text"
        placeholder="Enter website URL..."
        className="flex-1 p-3 rounded-lg text-black border border-gray-400 focus:outline-none focus:border-blue-500"
        value={domain}
        onChange={(e) => setDomain(e.target.value)}
      />
      <button
        onClick={handleScrape}
        className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 shadow-lg whitespace-nowrap"
      >
        Start Scraping
      </button>
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>

  );
}
