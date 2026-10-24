'use client';
import { useEffect, useState } from 'react';
import Script from 'next/script';

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [error, setError] = useState("");
  
  // UI State
  const [showMap, setShowMap] = useState(false);
  const [locations, setLocations] = useState<any>({});
  const [geoStatus, setGeoStatus] = useState("");

  const handleTelegramLogin = async (initData: string) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/telegram_login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ init_data: initData })
      });
      if (!res.ok) throw new Error("Auth Failed");
      const data = await res.json();
      setUser(data);
      localStorage.setItem("meena_user", JSON.stringify(data));
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    const savedUser = localStorage.getItem("meena_user");
    if (savedUser) setUser(JSON.parse(savedUser));
    const tg = (window as any).Telegram?.WebApp;
    if (tg && tg.initData) { tg.expand(); handleTelegramLogin(tg.initData); }
  }, []);

  const fetchProducts = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/products`).then(res => res.json()).then(data => setProducts(data));
  };

  useEffect(() => { if (user) fetchProducts(); }, [user]);

  // ─── GPS LOGIC ───
  const handleCheckIn = () => {
    setGeoStatus("Getting location...");
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          setGeoStatus(`Location found! Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`);
          
          await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/update_location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              telegram_id: user.telegram_chat_id || "demo_user",
              name: user.shop || "Sales Rep",
              lat: latitude,
              lon: longitude
            })
          });
        },
        (err) => {
          setGeoStatus(`Error: ${err.message}. Please allow location.`);
        },
        { enableHighAccuracy: true } // Forces GPS, not just Wi-Fi
      );
    } else {
      setGeoStatus("Geolocation not supported by this browser.");
    }
  };

  const fetchLocations = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/get_locations`);
    const data = await res.json();
    setLocations(data);
  };

  useEffect(() => {
    if (showMap) {
      fetchLocations();
      const interval = setInterval(fetchLocations, 5000); // Auto-refresh map every 5s
      return () => clearInterval(interval);
    }
  }, [showMap]);

  if (!user) {
    return (
      <>
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <div className="h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-xl shadow-2xl w-96 border-t-4 border-[#0B3C5D] text-center">
            <h1 className="text-2xl font-bold text-[#0B3C5D] mb-2">Meena Agencies</h1>
            <button onClick={() => handleTelegramLogin("mock_data_for_demo")} className="w-full bg-[#229ED9] text-white py-3 rounded-lg font-bold hover:bg-blue-600 transition mt-4">
              Login with Telegram
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="bg-[#0B3C5D] text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">🦚 Meena Agencies</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowMap(!showMap)} className="bg-blue-600 px-4 py-2 rounded text-sm font-bold">
            {showMap ? "View Products" : "Live Tracking"}
          </button>
          <button onClick={() => { localStorage.clear(); setUser(null); }} className="bg-red-600 px-4 py-2 rounded text-sm font-bold">
            Logout
          </button>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        {showMap ? (
          <div className="max-w-6xl mx-auto">
            <h2 className="text-2xl font-bold text-[#0B3C5D] mb-4">🗺️ Live Sales Rep Tracking</h2>
            <div className="bg-white p-4 rounded-xl shadow mb-4">
              <h3 className="font-bold mb-2">Rep Check-In</h3>
              <button onClick={handleCheckIn} className="bg-[#1D8348] text-white px-4 py-2 rounded font-bold">
                📍 Share My Live Location
              </button>
              {geoStatus && <p className="text-sm mt-2 text-gray-600">{geoStatus}</p>}
            </div>

            <div className="bg-white p-4 rounded-xl shadow">
              <h3 className="font-bold mb-2">Active Reps ({Object.keys(locations).length})</h3>
              {Object.keys(locations).length === 0 ? (
                <p className="text-gray-500">No reps have checked in yet.</p>
              ) : (
                <ul className="space-y-2">
                  {Object.entries(locations).map(([id, loc]: any) => (
                    <li key={id} className="border-b pb-2">
                      <b>{loc.name}</b> - Lat: {loc.lat.toFixed(4)}, Lon: {loc.lon.toFixed(4)} <span className="text-gray-400 text-sm">({loc.time})</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
             <h2 className="text-2xl font-bold text-[#0B3C5D] mb-4">Product Catalog</h2>
             <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {products.map((p, i) => (
                  <div key={i} className="bg-white p-4 rounded shadow border-l-4 border-[#1D8348]">
                    <h3 className="font-bold">{p.name}</h3>
                    <p className="text-green-700 font-bold">₹{p.price}</p>
                    <p className="text-sm text-gray-500">Stock: {p.stock}</p>
                  </div>
                ))}
             </div>
          </div>
        )}
      </main>
    </div>
  );
}
