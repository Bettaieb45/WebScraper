"use client";

import { useState } from "react";
import Header from "./components/Header";
import ScraperForm from "./components/ScraperForm";
import ScrapedUrls from "./components/ScrapedUrls";
import LoadingIndicator from "./components/LoadingIndicator";

export default function Home() {
  const [urls, setUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white px-4">
      <Header />
      <ScraperForm onScrapeComplete={setUrls} onLoadingChange={setLoading} />
      {loading ? <LoadingIndicator /> : <ScrapedUrls urls={urls} />}
    </main>
  );
}
