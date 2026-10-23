import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Meena Agencies | Trusted Pharma Wholesale",
  description: "B2B Pharma Ordering Portal",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Navbar />
        <main className="min-h-screen bg-gray-50">{children}</main>
        <footer className="bg-[#0B3C5D] text-white py-8 mt-12 text-center">
          <p>© 2026 Meena Agencies. Trusted Pharma Wholesale Partner, Thanjavur.</p>
        </footer>
      </body>
    </html>
  );
}
