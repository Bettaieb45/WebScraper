"use client";

import { motion } from "framer-motion";

interface ScrapedUrlsProps {
  urls: Record<string, { status: string; meta_title?: string; meta_description?: string; heading_count?: number }>;
}

export default function ScrapedUrls({ urls }: ScrapedUrlsProps) {
  const urlEntries = Object.entries(urls); // Convert dictionary to an array

  if (urlEntries.length === 0) return null;

  return (
    <motion.div
      className="mt-6 w-full max-w-lg bg-gray-800 p-4 rounded-lg shadow-md"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold mb-3 text-white">🔗 Scraped URLs:</h2>
      <ul className="overflow-hidden">
        {urlEntries.map(([url, data], index) => (
          <motion.li
            key={index}
            className="py-3 border-b border-gray-600 last:border-none flex flex-col"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <a href={url} className="text-blue-400 hover:underline font-semibold" target="_blank" rel="noopener noreferrer">
              {url}
            </a>
            <p className="text-sm text-gray-400 mt-1">
              <span className="font-bold text-green-300">Status:</span> {data.status}
            </p>
            {data.meta_title && (
              <p className="text-sm text-gray-300">
                <span className="font-bold text-yellow-400">Title:</span> {data.meta_title}
              </p>
            )}
            {data.meta_description && (
              <p className="text-sm text-gray-500">
                <span className="font-bold text-purple-400">Description:</span> {data.meta_description}
              </p>
            )}
            {data.heading_count && (
              <p className="text-sm text-gray-500">
                <span className="font-bold text-indigo-400">Heading Count:</span> {data.heading_count}
              </p>
            )}
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
}
