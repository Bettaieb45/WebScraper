"use client";

import { useState } from "react";

const DownloadCSVButton = ({ domain }: { domain: string }) => {
  const [loading, setLoading] = useState(false);
  const [csvReady, setCsvReady] = useState(false);
  const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const checkCsvAvailability = async () => {

    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/scraped-urls/?domain=${domain}`);
      const data = await response.json();
      setCsvReady(data.scraped_urls && data.scraped_urls.length > 0);
    } catch (error) {
      console.error("Error checking CSV availability:", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = async () => {
    if (!csvReady) return;

    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/download-csv/?domain=${domain}`);
      if (!response.ok) throw new Error("Failed to download CSV");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${domain}_scraped_urls.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading CSV:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={checkCsvAvailability}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        disabled={loading}
      >
        {loading ? "Checking CSV..." : "Check CSV Availability"}
      </button>

      <button
        onClick={downloadCSV}
        className={`px-4 py-2 rounded-lg ${
          csvReady ? "bg-green-500 hover:bg-green-600" : "bg-gray-400 cursor-not-allowed"
        } text-white`}
        disabled={!csvReady || loading}
      >
        {loading ? "Downloading..." : "Download CSV"}
      </button>
    </div>
  );
};

export default DownloadCSVButton;
