"use client";

import { useState } from "react";
import Header from "./components/Header";
import ScraperForm from "./components/ScraperForm";
import ScrapedUrls from "./components/ScrapedUrls";
import LoadingIndicator from "./components/LoadingIndicator";
import DownloadCSVButton from "./components/DownloadCSVButton"; // Import the button

export default function Home() {
  const [urls, setUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [domain, setDomain] = useState<string>("");

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white px-4">
      <Header />
      <ScraperForm 
        onScrapeComplete={(scrapedUrls, scrapedDomain) => {
          setUrls(scrapedUrls);
          setDomain(scrapedDomain); // ✅ Store the domain for CSV download
        }} 
        onLoadingChange={setLoading} 
      />
      {/* ✅ Show download button only when URLs are available */}
      {urls.length > 0 && domain && <DownloadCSVButton domain={domain} />}
      {loading ? <LoadingIndicator /> : <ScrapedUrls urls={urls} />}
      
    
    </main>
  );
}
