"use client";

import { useState } from "react";
import Header from "./components/Header";
import ScraperForm from "./components/ScraperForm";
import ScrapedUrls from "./components/ScrapedUrls";
import LoadingIndicator from "./components/LoadingIndicator";
import DownloadCSVButton from "./components/DownloadCSVButton";

// Define the type for the scraped URLs dictionary
interface ScrapedUrlData {
  status: string;
  meta_title?: string;
  meta_description?: string;
  heading_count?: number;
}

export default function Home() {
  // ✅ Ensure `urls` is stored as a dictionary (Record<string, ScrapedUrlData>)
  const [urls, setUrls] = useState<Record<string, ScrapedUrlData>>({});
  const [loading, setLoading] = useState(false);
  const [domain, setDomain] = useState<string>("");

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white px-4">
      <Header />
      <ScraperForm 
        onScrapeComplete={(scrapedUrls, scrapedDomain) => {
          setUrls(scrapedUrls); // ✅ Store dictionary, not array
          setDomain(scrapedDomain); // ✅ Store the domain for CSV download
        }} 
        onLoadingChange={setLoading} 
      />
      
      {/* ✅ Show download button only when URLs are available */}
      {Object.keys(urls).length > 0 && domain && <DownloadCSVButton domain={domain} />}
      
      {loading ? <LoadingIndicator /> : <ScrapedUrls urls={urls} />}
    </main>
  );
}
