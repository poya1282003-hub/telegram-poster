#!/usr/bin/env python3
import os
import requests

print("🤖 شروع ربات")

# ۱. خواندن تنظیمات
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

# ۲. خواندن موقعیت قبلی
try:
    with open('last_line.txt', 'r') as f:
        last = int(f.read().strip())
except:
    last = 0

print(f"📍 شروع از خط: {last}")

# ۳. خواندن متن‌ها
with open('texts.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

# ۴. انتخاب ۳ خط جدید
new_lines = []
for i in range(3):
    if last + i < len(lines):
        new_lines.append(lines[last + i])

if not new_lines:
    print("✅ همه چیز ارسال شده!")
    exit(0)

# ۵. ساخت پیام
message = "\n".join(new_lines)

# ۶. ارسال به تلگرام
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {
    'chat_id': CHANNEL,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, json=data)

if response.json().get('ok'):
    # ۷. ذخیره موقعیت جدید
    new_last = last + len(new_lines)
    with open('last_line.txt', 'w') as f:
        f.write(str(new_last))
    
    print(f"✅ {len(new_lines)} خط ارسال شد")
    print(f"📌 موقعیت جدید: {new_last}")
else:
    print("❌ خطا در ارسال")
