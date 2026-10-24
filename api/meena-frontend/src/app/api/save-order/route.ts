import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  // 🛡️ BLUE TEAM FIX: CSRF Protection (Check Origin)
  const origin = req.headers.get('origin');
  const allowedOrigin = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'; // Will be your Vercel URL
  
  if (origin && !origin.includes(allowedOrigin.replace('https://', '').replace('http://', ''))) {
    return NextResponse.json({ error: "CSRF Blocked" }, { status: 403 });
  }

  const { telegram_id, cart_items } = await req.json();
  let secureTotal = 0;
  for (const item of cart_items) {
    secureTotal += Math.max(item.price, 150) * item.qty;
  }

  const orderId = `ORD-${Math.floor(1000 + Math.random() * 9000)}`;
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  
  if (botToken) {
    await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: "8205802064", text: `🔔 *NEW ORDER*\nID: ${orderId}\nAmount: ₹${secureTotal}`, parse_mode: 'Markdown' })
    });
  }
  
  return NextResponse.json({ status: "success", order_id: orderId, total: secureTotal });
}
