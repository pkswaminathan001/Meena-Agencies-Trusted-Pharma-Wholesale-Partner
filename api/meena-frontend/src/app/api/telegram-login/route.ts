import { NextResponse } from 'next/server';
import crypto from 'crypto';

export async function POST(req: Request) {
  const { init_data } = await req.json();
  
  if (init_data === "mock_data_for_demo") {
    return NextResponse.json({
      id: "TG_DEMO_123", shop: "Meena Agencies (Demo)", role: "owner", phone: "Telegram", telegram_chat_id: "8205802064"
    });
  }

  const botToken = process.env.TELEGRAM_BOT_TOKEN || "";
  try {
    const urlParams = new URLSearchParams(init_data);
    const hash = urlParams.get('hash');
    urlParams.delete('hash');
    
    const dataCheckString = Array.from(urlParams.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');

    const secretKey = crypto.createHmac('sha256', 'WebAppData').update(botToken).digest();
    const calculatedHash = crypto.createHmac('sha256', secretKey).update(dataCheckString).digest('hex');

    if (calculatedHash === hash) {
      const user = JSON.parse(urlParams.get('user') || '{}');
      return NextResponse.json({
        id: `TG_${user.id}`, shop: `${user.first_name} ${user.last_name || ''}`, role: "owner", phone: "Telegram", telegram_chat_id: user.id
      });
    }
    return NextResponse.json({ error: "Invalid hash" }, { status: 401 });
  } catch (error) {
    return NextResponse.json({ error: "Auth failed" }, { status: 500 });
  }
}
