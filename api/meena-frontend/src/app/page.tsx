'use client';
import { useEffect, useState } from 'react';
import Script from 'next/script';

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [error, setError] = useState("");
  
  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showAddStock, setShowAddStock] = useState(false);
  const [stockSku, setStockSku] = useState("");
  const [stockQty, setStockQty] = useState(1);

  // ─── SECURE CHECKOUT STATE ───
  const [cart, setCart] = useState<any[]>([]);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [checkoutStep, setCheckoutStep] = useState(1); // 1=Review, 2=OTP
  const [otp, setOtp] = useState("");
  const [orderSuccess, setOrderSuccess] = useState("");

  const handleTelegramLogin = async (initData: string) => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/telegram_login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ init_data: initData })
      });
      if (!res.ok) throw new Error("Telegram Authentication Failed");
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

  const addToCart = (product: any) => {
    setCart(prev => {
      const existing = prev.find(p => p.name === product.name);
      if (existing) return prev.map(p => p.name === product.name ? { ...p, qty: p.qty + 1 } : p);
      return [...prev, { ...product, qty: 1 }];
    });
  };

  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.qty, 0);

  // ─── CHECKOUT FLOW ───
  const handleRequestOtp = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/request_order_otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telegram_id: user.telegram_chat_id || "123456789" })
      });
      const data = await res.json();
      if (data.otp) alert(`DEMO MODE: Your Telegram OTP is ${data.otp}`);
      setCheckoutStep(2);
    } catch (err) {
      alert("Failed to send OTP");
    }
  };

  const handlePlaceOrder = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/place_order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: user.telegram_chat_id || "123456789",
          otp: otp,
          cart_items: cart
        })
      });
      if (!res.ok) throw new Error("Invalid OTP");
      const data = await res.json();
      setOrderSuccess(data.order_id);
      setCart([]);
      setShowCheckoutModal(false);
      setCheckoutStep(1);
      setOtp("");
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleLogout = () => { setUser(null); localStorage.removeItem("meena_user"); };

  if (!user) {
    return (
      <>
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <div className="h-screen flex items-center justify-center bg-gray-50">
          <div className="bg-white p-8 rounded-xl shadow-2xl w-96 border-t-4 border-[#0B3C5D] text-center">
            <h1 className="text-2xl font-bold text-[#0B3C5D] mb-2">🦚 Meena Agencies</h1>
            <p className="text-gray-500 text-sm mb-6">Fast B2B Pharma Ordering</p>
            {error && <p className="text-red-500 text-sm mb-4 font-bold">{error}</p>}
            <button onClick={() => handleTelegramLogin("mock_data_for_demo")} className="w-full bg-[#229ED9] text-white py-3 rounded-lg font-bold hover:bg-blue-600 transition">
              Login with Telegram
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50">
      <div className={`fixed inset-y-0 left-0 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 z-30 w-64 bg-[#0B3C5D] text-white flex flex-col`}>
        <div className="p-4 border-b border-blue-800">
          <h2 className="text-xl font-bold">🦚 Meena</h2>
          <p className="text-sm text-green-400 font-semibold">{user.role}</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <a href="#" className="block py-2 px-4 bg-blue-800 rounded-lg">📦 Dashboard</a>
          <a href="#" className="block py-2 px-4 hover:bg-blue-800 rounded-lg">🛒 Place Order</a>
          {user.role === 'owner' && (
            <button onClick={() => setShowAddStock(true)} className="w-full text-left py-2 px-4 text-green-400 font-bold">➕ Add Stock</button>
          )}
        </nav>
        <div className="p-4 border-t border-blue-800">
          <button onClick={handleLogout} className="w-full bg-red-600 py-2 rounded-lg font-bold">🚪 Logout</button>
        </div>
      </div>

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="bg-white shadow-sm p-4 flex justify-between items-center md:hidden">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-2xl">☰</button>
          <span className="font-bold text-[#0B3C5D]">{user.shop}</span>
          <div className="w-6"></div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-6xl mx-auto">
            {orderSuccess && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                <strong>✅ Order Placed Successfully!</strong> Order ID: {orderSuccess}
              </div>
            )}
            <h1 className="text-3xl font-bold text-[#0B3C5D] mb-2">Welcome, {user.shop}</h1>
            <p className="text-gray-500 mb-8">User: {user.id} | Role: {user.role}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {products.map((p, i) => (
                <div key={i} className="bg-white rounded-xl shadow hover:shadow-xl transition p-5 border-l-4 border-[#1D8348] flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-lg text-[#0B3C5D]">{p.name}</h3>
                    <p className="text-2xl font-extrabold text-[#1D8348] mt-2">₹{p.price}</p>
                    <p className="text-sm text-gray-500 mb-4">Stock: {p.stock}</p>
                  </div>
                  <button onClick={() => addToCart(p)} className="w-full bg-[#0B3C5D] text-white py-2 rounded font-bold hover:bg-blue-800">Add to Cart</button>
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>

      {/* FLOATING CART BUTTON */}
      {cart.length > 0 && (
        <div className="fixed bottom-6 right-6 z-50">
          <button onClick={() => setShowCheckoutModal(true)} className="bg-[#1D8348] text-white px-6 py-4 rounded-full shadow-2xl font-bold flex items-center gap-2 hover:bg-green-700">
            🛒 Checkout ({cart.length}) - ₹{cartTotal}
          </button>
        </div>
      )}

      {/* CHECKOUT MODAL WITH TELEGRAM OTP */}
      {showCheckoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-2xl w-96">
            {checkoutStep === 1 ? (
              <>
                <h2 className="text-xl font-bold mb-4">Review Order</h2>
                <div className="max-h-60 overflow-y-auto mb-4">
                  {cart.map((item, i) => (
                    <div key={i} className="flex justify-between border-b py-2">
                      <span>{item.name} (x{item.qty})</span>
                      <span className="font-bold">₹{item.price * item.qty}</span>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between font-bold text-lg mb-6">
                  <span>Total:</span>
                  <span>₹{cartTotal}</span>
                </div>
                <button onClick={handleRequestOtp} className="w-full bg-[#1D8348] text-white py-3 rounded-lg font-bold mb-2">🔒 Send Telegram OTP</button>
                <button onClick={() => setShowCheckoutModal(false)} className="w-full bg-gray-200 py-2 rounded-lg">Cancel</button>
              </>
            ) : (
              <>
                <h2 className="text-xl font-bold mb-2">Enter Security OTP</h2>
                <p className="text-sm text-gray-500 mb-4">We sent a 6-digit code to your Telegram app.</p>
                <input type="text" value={otp} onChange={e => setOtp(e.target.value)} placeholder="Enter 6-digit OTP" className="w-full mb-4 px-4 py-3 border rounded-lg text-center text-xl tracking-widest font-bold" maxLength={6} />
                <button onClick={handlePlaceOrder} className="w-full bg-[#1D8348] text-white py-3 rounded-lg font-bold mb-2">✅ Verify & Place Order</button>
                <button onClick={() => setCheckoutStep(1)} className="w-full bg-gray-200 py-2 rounded-lg">Back</button>
              </>
            )}
          </div>
        </div>
      )}

      {/* ADD STOCK MODAL */}
      {showAddStock && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <form onSubmit={(e) => { e.preventDefault(); fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/add_stock`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sku: stockSku, qty: stockQty }) }).then(() => { setShowAddStock(false); fetchProducts(); }) }} className="bg-white p-6 rounded-xl shadow-2xl w-96">
            <h2 className="text-xl font-bold mb-4">Quick Add Stock</h2>
            <input type="text" placeholder="Medicine SKU" onChange={e => setStockSku(e.target.value)} className="w-full mb-3 p-2 border rounded" required />
            <input type="number" placeholder="Quantity" onChange={e => setStockQty(parseInt(e.target.value))} className="w-full mb-4 p-2 border rounded" required />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setShowAddStock(false)} className="px-4 py-2 bg-gray-200 rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-[#1D8348] text-white rounded font-bold">Save</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
