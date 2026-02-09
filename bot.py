#!/usr/bin/env python3
import os
import requests
from datetime import datetime

print("🤖 شروع ربات")

# خواندن تنظیمات
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "")  # تغییر: پیش‌فرض خالی

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

# ==================== ساخت پیام زیبا ====================
post_number = (last_line // 3) + 1

# تاریخ امروز
today = datetime.now()
date_str = today.strftime("%Y/%m/%d - %H:%M")

# شروع پیام - با HTML
message = f"<b>🔑 پست #{post_number}</b> | 🗓️ {date_str}\n"
message += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"

# اضافه کردن ۳ خط
for i, line in enumerate(lines_to_send, 1):
    message += f"<b>{i}.</b> <code>{line}</code>\n\n"

message += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"

# بخش کپی
message += "<b>📋 کپی آسان:</b>\n"
for i, line in enumerate(lines_to_send, 1):
    message += f"<pre>{line}</pre>\n"

message += "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"

# بخش کانال - اگر CHANNEL_USERNAME تنظیم شده
if CHANNEL_USERNAME:
    message += f"<b>📢 کانال:</b> {CHANNEL_USERNAME}\n"
else:
    message += "<b>📢 کانال:</b> (نام کانال تنظیم نشده)\n"

message += "🔄 هر ۳۰ دقیقه پست جدید\n"
message += "🔔 نوتیفیکیشن روشن باشه\n\n"
message += "#پروکسی #MTProto #کانال"

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
