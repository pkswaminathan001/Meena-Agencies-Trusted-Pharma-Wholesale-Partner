'use client';
import { useEffect, useState } from 'react';

export default function Navbar() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("meena_user");
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("meena_user");
    window.location.href = "/";
  };

  return (
    <nav className="bg-[#0B3C5D] text-white shadow-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-2 flex justify-between items-center">
        
        <div className="flex items-center gap-4">
          <img src="/logo.png" alt="Logo" className="w-[70px] h-[70px] rounded-full object-cover shadow-lg border-4 border-white bg-white" />
          <h1 className="text-2xl font-bold hidden md:block">Meena Agencies</h1>
        </div>
        
        <div className="flex items-center gap-4 text-sm font-semibold">
          <a href="#" className="hover:text-green-400 transition hidden md:block">Catalog</a>
          <a href="#" className="hover:text-green-400 transition hidden md:block">Track Order</a>
          {/* CREDIT LINK REMOVED AS PER DAD'S D9 RULE */}
          
          <button className="bg-[#1D8348] px-4 py-2 rounded-lg hover:bg-green-700 transition">
            My Account
          </button>

          {user && (
            <button onClick={handleLogout} className="bg-red-600 px-4 py-2 rounded-lg hover:bg-red-700 transition text-white">
              Logout
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
