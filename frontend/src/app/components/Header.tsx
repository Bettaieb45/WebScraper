"use client";

import { motion } from "framer-motion";

export default function Header() {
  return (
    <motion.h1
      className="text-4xl font-bold mb-6 text-center"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      🌐 Web Scraper
    </motion.h1>
  );
}
