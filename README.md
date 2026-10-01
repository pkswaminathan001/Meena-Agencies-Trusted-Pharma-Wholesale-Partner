# 🏥 Meena Agencies
### Trusted Pharma Wholesale Partner

**An AI-powered pharma wholesale platform built for Tamil Nadu's pharmacy retailers.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org)
[![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)]()

*Built with ❤️ for pharmacies in Thanjavur, Tamil Nadu*

</div>

---

## 🌟 Overview

**Meena Agencies** is a modern, AI-driven wholesale pharmaceutical platform designed to replace paperwork, phone calls, and manual order-taking with a fast, secure, multi-tenant digital system.

Pharmacies order in one tap. Owners approve from their phone. Employees get real-time alerts. **Every customer's data is isolated at the architecture level** — no pharmacy can ever see another's orders, prices, or history.

---

## ✨ Core Features

<table>
<tr>
<td width="50%">

### 🛒 For Retailers (Pharmacies)
- 🔐 Secure PIN-based login
- 🛍️ Amazon-style shopping cart
- 📦 One-tap **Reorder Last** with OTP modal
- 💊 Live product catalog with batch tracking
- 📊 Personal dashboard (credit, outstanding)
- 📱 **Telegram notifications** for every order
- 📄 PDF/PNG account statements
- 🚚 Live delivery tracking

</td>
<td width="50%">

### 👨‍💼 For Owner / Staff
- 📥 Real-time order alerts via Telegram
- ✅ Approve / Reject from mobile
- 💰 Credit limit & outstanding tracking
- 🌅 **7 AM Flash Offers** (auto-scheduled)
- 🎯 Tiered discount engine (Silver/Gold/Platinum)
- 📈 Analytics, forecasts, fraud detection
- 🧾 GST invoicing + accounting books
- 🤖 AI chat with **Groq LLM**

</td>
</tr>
</table>

---

## 🧠 AI & Marketing Engine

| Feature | Description |
|---|---|
| **📰 Pharma Intel** | Live RSS feed — GST updates, CDSCO alerts, AI-in-pharma news. Auto-refreshed, never repeats. |
| **🤖 Copy Engine** | Generates per-retailer headlines based on tier + purchase history. Ethical B2B copy only. |
| **🎯 Intent Router** | Classifies every retailer message: order / complaint / question / payment / chitchat |
| **📢 Smart Promotions** | Broadcast to segments with per-customer personalization |
| **📊 Forecasting** | Smart forecast + seasonal + climate-aware demand prediction |
| **🚨 Fraud Detection** | Detects anomalies in order patterns |

---

## 🔒 Security Architecture

> **Every customer's data is isolated. This is enforced at the code level, not by hope.**

| Layer | Protection |
|---|---|
| **Multi-Tenant Middleware** | Every message resolved by `chat_id` only — never by content |
| **Owner Lock** | Owner commands require exact `OWNER_CHAT_ID` match |
| **Retailer Isolation** | Each retailer sees ONLY their own orders, prices, banner |
| **Atomic Writes** | `storage.py` prevents order loss during simultaneous writes |
| **Audit Trail** | Every sensitive action logged to `security_audit.log` |
| **No Group Chats** | Group chats rejected automatically |
| **Secrets Protected** | `.env` never committed to git |

---

## 🏗️ Architecture
