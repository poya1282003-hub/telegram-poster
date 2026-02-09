#!/usr/bin/env python3
import os
import requests
from datetime import datetime

print("🤖 شروع ربات")

# خواندن تنظیمات
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "")

if not TOKEN or not CHANNEL:
    print("❌ توکن یا آیدی کانال تنظیم نشده!")
    exit(1)

print("✅ تنظیمات OK")

# خواندن موقعیت
try:
    with open('last_line.txt', 'r') as f:
        last_line = int(f.read().strip())
except:
    last_line = 0

print(f"📌 آخرین خط ارسال شده: {last_line}")

# خواندن متن‌ها
try:
    with open('texts.txt', 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("❌ فایل texts.txt پیدا نشد!")
    exit(1)

print(f"📄 تعداد کل خطوط: {len(all_lines)}")

# اگر تمام شده
if last_line >= len(all_lines):
    print("🎉 تمام خطوط ارسال شده‌اند!")
    exit(0)

# انتخاب ۳ خط جدید
lines_to_send = []
for i in range(3):
    line_num = last_line + i
    if line_num < len(all_lines):
        lines_to_send.append(all_lines[line_num])

if not lines_to_send:
    print("❌ هیچ خطی برای ارسال نیست!")
    exit(0)

print(f"📤 ارسال {len(lines_to_send)} خط...")

# ==================== ساخت پیام ====================
post_number = (last_line // 3) + 1
today = datetime.now()
date_str = today.strftime("%Y/%m/%d - %H:%M")

# شروع پیام ساده
message = f"<b>🔄 پست #{post_number}</b> | 📅 {date_str}\n\n"

# فقط یک باکس بزرگ (بدون نمایش لینک‌ها قبل از باکس)
box_width = 45  # تقریباً ۱۰ سانت

# عنوان بالای باکس
message += "<b>📋 برای کپی کردن روی دکمه زیر بزنید:</b>\n\n"

# دکمه بزرگ بالایی
message += f"<code>╔{'═' * box_width}╗</code>\n"
message += f"<code>║{' ' * box_width}║</code>\n"

# متن وسط دکمه (بزرگ)
button_text = "🖱️ اینجا کلیک کنید تا کپی شود 🖱️"
text_padding = (box_width - len(button_text) + 8) // 2  # +8 برای ایموجی
left_pad = " " * text_padding
right_pad = " " * (box_width - len(left_pad) - len(button_text) + 8)

message += f"<code>║{left_pad}{button_text}{right_pad}║</code>\n"
message += f"<code>║{' ' * box_width}║</code>\n"
message += f"<code>╚{'═' * box_width}╝</code>\n\n"

# متن اصلی برای کپی (همه ۳ لینک)
all_lines_text = "\n".join(lines_to_send)
message += f"<pre>{all_lines_text}</pre>\n\n"

# اطلاعات پایین
message += "⏰ هر ۳۰ دقیقه پست جدید\n"
message += "🔔 نوتیفیکیشن روشن باشه\n\n"

# آدرس کانال
message += "<i>@v2rayonlin</i>"

# ==================== ارسال ====================
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    'chat_id': CHANNEL,
    'text': message,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True,
}

try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get('ok'):
        # آپدیت موقعیت
        new_last = last_line + len(lines_to_send)
        with open('last_line.txt', 'w') as f:
            f.write(str(new_last))
        
        print(f"✅ پست #{post_number} ارسال شد")
        print(f"📍 موقعیت جدید: {new_last}")
        
        # نمایش خلاصه
        print("\n📬 محتوای ارسال شده:")
        for i, line in enumerate(lines_to_send, 1):
            print(f"  {i}. {line[:40]}...")
        
    else:
        print(f"❌ خطا: {result.get('description')}")
        
except Exception as e:
    print(f"❌ مشکل اتصال: {e}")
