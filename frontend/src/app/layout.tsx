import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "WebScrapeX - AI-Powered Web Scraping Made Easy",
  description:
    "Extract data effortlessly with WebScrapeX—your AI-driven, FastAPI-powered web scraping solution. Built with Python, BeautifulSoup, and Next.js for efficiency and speed.",
  icons: {
    icon: "/favicon.ico",
  },
  openGraph: {
    title: "WebScrapeX - AI-Powered Web Scraping Made Easy",
    description:
      "Extract data effortlessly with WebScrapeX—your AI-driven, FastAPI-powered web scraping solution. Built with Python, BeautifulSoup, and Next.js for efficiency and speed.",
    url: "https://webscrapex.com",
    siteName: "WebScrapeX",
    images: [
      {
        url: "/og-image.png", // Replace with your actual OpenGraph image
        width: 1200,
        height: 630,
        alt: "WebScrapeX - The Future of Data Extraction",
      },
    ],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "WebScrapeX - AI-Powered Web Scraping Made Easy",
    description:
      "Extract data effortlessly with WebScrapeX—your AI-driven, FastAPI-powered web scraping solution. Built with Python, BeautifulSoup, and Next.js for efficiency and speed.",
    images: ["/og-image.png"], // Replace with your actual image
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-theme="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex flex-col min-h-screen h-full bg-gray-950 text-gray-100 relative animate-fadeIn`}
      >
        {children}
      </body>
    </html>
  );
}
