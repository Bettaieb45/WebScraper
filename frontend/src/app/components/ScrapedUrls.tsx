"use client";

import { motion } from "framer-motion";

interface ScrapedUrlsProps {
  urls: string[];
}

export default function ScrapedUrls({ urls }: ScrapedUrlsProps) {
  if (urls.length === 0) return null;

  return (
    <motion.div
      className="mt-6 w-full max-w-lg bg-gray-800 p-4 rounded-lg shadow-md"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold mb-3 text-white">🔗 Scraped URLs:</h2>
      <ul className="overflow-hidden">
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
  );
}
