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

      // ✅ Check if data.scraped_urls is a non-empty object instead of an array
      setCsvReady(data.scraped_urls && Object.keys(data.scraped_urls).length > 0);
    } catch (error) {
      console.error("Error checking CSV availability:", error);
      setCsvReady(false);
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
      {/* Check CSV Availability Button */}
      <button
        onClick={checkCsvAvailability}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-all"
        disabled={loading}
      >
        {loading ? "Checking CSV..." : "Check CSV Availability"}
      </button>

      {/* Download CSV Button */}
      {csvReady && (
        <button
          onClick={downloadCSV}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all"
          disabled={loading}
        >
          {loading ? "Downloading..." : "Download CSV"}
        </button>
      )}
    </div>
  );
};

export default DownloadCSVButton;
