#!/usr/bin/env python3
import os
import requests
from datetime import datetime, timedelta
import jdatetime  # 👈 کتابخانه تاریخ شمسی

print("🤖 شروع ربات")

# خواندن تنظیمات
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

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

# زمان ایران (UTC + 3:30)
utc_now = datetime.utcnow()
iran_time = utc_now + timedelta(hours=3, minutes=30)

# 🔴 تبدیل به تاریخ شمسی
shamsi_date = jdatetime.datetime.fromgregorian(
    year=iran_time.year,
    month=iran_time.month,
    day=iran_time.day,
    hour=iran_time.hour,
    minute=iran_time.minute
)

# ایموجی‌های متحرک
animated_emojis = ["🎯", "🚀", "⚡", "🔑", "🌊", "✨", "🎉", "🔥", "💫", "🌟"]
static_emojis = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙"]

# انتخاب ایموجی
main_emoji = animated_emojis[post_number % len(animated_emojis)]
hour_index = shamsi_date.hour % 12
time_emoji = static_emojis[hour_index]

# تاریخ و زمان شمسی
date_str = shamsi_date.strftime("%Y/%m/%d")  # مثلاً 1404/11/20
time_str = shamsi_date.strftime("%H:%M")

# 🔴 تغییر: استفاده از تاریخ شمسی
header_line = f"{main_emoji}<b> post #{post_number}</b>  {time_emoji}<b>{time_str}</b>  📅<b>{date_str}</b>"

# ساخت پیام
message = f"{header_line}\n\n"

# متن اصلی برای کپی
all_lines_text = "\n".join(lines_to_send)
message += f"<pre>{all_lines_text}</pre>\n\n"

# خط پایین
message += "🔄 هر ۳۰ دقیقه پست جدید\n\n"
message += "@V2REYONLINE"

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
        
        # نمایش زمان‌ها برای دیباگ
        print(f"🕒 زمان میلادی: {iran_time.strftime('%Y/%m/%d %H:%M')}")
        print(f"🕒 زمان شمسی: {date_str} {time_str}")
        
        # نمایش خلاصه
        print("\n📬 محتوای ارسال شده:")
        for i, line in enumerate(lines_to_send, 1):
            print(f"  {i}. {line[:40]}...")
        
    else:
        print(f"❌ خطا: {result.get('description')}")
        
except Exception as e:
    print(f"❌ مشکل اتصال: {e}")
