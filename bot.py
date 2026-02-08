#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

print("🤖 شروع ربات تلگرام")

# خواندن از Secrets گیت‌هاب
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

print(f"✅ توکن: {TOKEN[:10]}...")
print(f"✅ کانال: {CHANNEL}")

# بررسی تنظیمات
if not TOKEN or "توکن_" in TOKEN:
    print("❌ توکن ربات تنظیم نشده!")
    print("   در GitHub Secrets → TELEGRAM_BOT_TOKEN را تنظیم کن")
    exit(1)

if not CHANNEL or "آیدی_" in CHANNEL:
    print("❌ آیدی کانال تنظیم نشده!")
    print("   در GitHub Secrets → TELEGRAM_CHANNEL_ID را تنظیم کن")
    exit(1)

# خواندن شماره آخرین خط
try:
    with open('last_line.txt', 'r') as f:
        last_line = int(f.read().strip())
except:
    last_line = 0

print(f"📖 آخرین خط ارسال شده: {last_line}")

# خواندن تمام خطوط متن
try:
    with open('texts.txt', 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f]
except FileNotFoundError:
    print("❌ فایل texts.txt پیدا نشد!")
    exit(1)

print(f"📄 تعداد کل خطوط: {len(all_lines)}")

# اگر همه خطوط ارسال شده‌اند
if last_line >= len(all_lines):
    print("🎉 تمام خطوط ارسال شده‌اند!")
    exit(0)

# 🎯 گرفتن ۳ خط بعدی (تغییر از ۵ به ۳)
lines_to_send = []
for i in range(3):  # هر بار ۳ خط
    if last_line + i < len(all_lines):
        lines_to_send.append(all_lines[last_line + i])

print(f"📤 ارسال {len(lines_to_send)} خط به تلگرام...")

# ساخت پیام نهایی
separator = "\n" + "─" * 25 + "\n"
message = separator.join(lines_to_send)

# ارسال به تلگرام
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    'chat_id': CHANNEL,
    'text': message,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
}

try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get('ok'):
        # بروزرسانی شماره خط
        new_last_line = last_line + len(lines_to_send)
        with open('last_line.txt', 'w') as f:
            f.write(str(new_last_line))
        print(f"✅ ارسال موفق! خط جدید: {new_last_line}")
        print(f"📊 {len(lines_to_send)} خط ارسال شد")
    else:
        print(f"❌ خطای تلگرام: {result.get('description')}")
        
except Exception as e:
    print(f"❌ خطای اتصال: {e}")
