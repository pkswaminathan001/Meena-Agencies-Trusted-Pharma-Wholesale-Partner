import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Meena Agencies | Trusted Pharma Wholesale",
  description: "B2B Pharma Ordering Portal",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-[#0B3C5D] text-white shadow-xl sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <span>🦚</span> Meena Agencies
            </h1>
            <div className="flex gap-6 text-sm font-semibold">
              <a href="#" className="hover:text-green-400 transition">Catalog</a>
              <a href="#" className="hover:text-green-400 transition">Track Order</a>
              <a href="#" className="hover:text-green-400 transition">Credit Line</a>
              <button className="bg-[#1D8348] px-4 py-2 rounded-lg hover:bg-green-700 transition">
                My Account
              </button>
            </div>
          </div>
        </nav>
        <main className="min-h-screen bg-gray-50">{children}</main>
        <footer className="bg-[#0B3C5D] text-white py-8 mt-12 text-center">
          <p>© 2026 Meena Agencies. Trusted Pharma Wholesale Partner, Thanjavur.</p>
        </footer>
      </body>
    </html>
  );
}
