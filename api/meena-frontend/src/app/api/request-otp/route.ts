import { NextResponse } from 'next/server';

const rateLimit = new Map<string, number>();

export async function POST(req: Request) {
  const { telegram_id } = await req.json();
  
  const now = Date.now();
  const lastRequest = rateLimit.get(telegram_id) || 0;
  
  if (now - lastRequest < 60000) {
    return NextResponse.json({ error: "Too many requests. Please wait 60 seconds." }, { status: 429 });
  }
  rateLimit.set(telegram_id, now);

  const otp = Math.floor(100000 + Math.random() * 900000).toString();
  
  // Store OTP securely in memory
  if (!(global as any).activeOtps) (global as any).activeOtps = {};
  (global as any).activeOtps[telegram_id] = otp;

  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  if (botToken) {
    await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: telegram_id, text: `🦚 Meena Agencies\nYour OTP is: *${otp}*`, parse_mode: 'Markdown' })
    });
  }
  return NextResponse.json({ status: "success", message: "OTP Sent" });
}
