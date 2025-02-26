"use client";

import { motion } from "framer-motion";

export default function LoadingIndicator() {
  return (
    <motion.div
      className="mt-6 text-lg text-blue-300"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, repeat: Infinity, repeatType: "mirror" }}
    >
      ⏳ Scraping in progress...
    </motion.div>
  );
}
