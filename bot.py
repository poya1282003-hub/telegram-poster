#!/usr/bin/env python3
import os
import requests
import base64
import json
from datetime import datetime, timedelta
import jdatetime

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
raw_lines = []
for i in range(3):
    line_num = last_line + i
    if line_num < len(all_lines):
        raw_lines.append(all_lines[line_num])

if not raw_lines:
    print("❌ هیچ خطی برای ارسال نیست!")
    exit(0)

print(f"📤 دریافت {len(raw_lines)} خط خام...")

# ==================== پرچم‌های چرخشی ====================
flags = [
    "🇨🇭", "🇺🇸", "🇬🇧", "🇩🇪", "🇨🇦", "🇫🇷", "🇮🇹", "🇯🇵",
    "🇰🇷", "🇸🇪", "🇳🇱", "🇦🇺", "🇳🇿", "🇸🇬", "🇹🇷", "🇷🇺",
    "🇧🇷", "🇮🇳", "🇨🇳", "🇪🇸", "🇵🇹", "🇬🇷", "🇫🇮", "🇳🇴",
    "🇩🇰", "🇦🇹", "🇧🇪", "🇮🇪", "🇵🇱", "🇨🇿", "🇭🇺", "🇷🇴",
    "🇺🇦", "🇮🇱", "🇦🇪", "🇸🇦", "🇿🇦", "🇲🇽", "🇦🇷", "🇨🇱"
]

# ==================== اصلاح لینک‌ها ====================
def modify_vmess_link(link, post_number):
    """
    تغییر فیلد ps در لینک vmess
    نمایش: {پرچم} @v2reyonline ✓هر ۳۰ دقیقه آپدیت
    """
    try:
        if not link.startswith("vmess://"):
            return link
        
        # انتخاب پرچم بر اساس شماره پست
        flag_index = post_number % len(flags)
        flag = flags[flag_index]
        
        base64_str = link.replace("vmess://", "")
        decoded = base64.b64decode(base64_str).decode('utf-8')
        config = json.loads(decoded)
        
        # 🔴 تغییر ps به فرمت مورد نظر
        config["ps"] = f"{flag}  @v2reyonline ✓هر ۳۰ دقیقه آپدیت"
        
        new_json = json.dumps(config)
        new_base64 = base64.b64encode(new_json.encode()).decode()
        new_link = f"vmess://{new_base64}"
        
        print(f"   ✅ {config['ps']}")
        return new_link
        
    except Exception as e:
        print(f"   ⚠️ خطا در اصلاح لینک: {e}")
        return link

# اصلاح همه لینک‌ها
lines_to_send = []
for i, line in enumerate(raw_lines):
    modified_line = modify_vmess_link(line, last_line + i)
    lines_to_send.append(modified_line)

# ==================== ساخت پیام ====================
post_number = (last_line // 3) + 1

# زمان ایران
utc_now = datetime.utcnow()
iran_time = utc_now + timedelta(hours=3, minutes=30)

# تاریخ شمسی
shamsi_date = jdatetime.datetime.fromgregorian(
    year=iran_time.year,
    month=iran_time.month,
    day=iran_time.day,
    hour=iran_time.hour,
    minute=iran_time.minute
)

# ایموجی‌ها
animated_emojis = ["🎯", "🚀", "⚡", "🔑", "🌊", "✨", "🎉", "🔥", "💫", "🌟"]
static_emojis = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙"]

# انتخاب ایموجی
main_emoji = animated_emojis[post_number % len(animated_emojis)]
hour_index = shamsi_date.hour % 12
time_emoji = static_emojis[hour_index]

# تاریخ و زمان شمسی
date_str = shamsi_date.strftime("%Y/%m/%d")
time_str = shamsi_date.strftime("%H:%M")

# 🔴 ساخت پیام - بدون خط اول
message = f"{main_emoji}<b> post #{post_number}</b>  {time_emoji}<b>{time_str}</b>  📅<b>{date_str}</b>\n\n"

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
        
        print("\n📱 نمایش در V2Ray کاربران:")
        for i, line in enumerate(lines_to_send, 1):
            try:
                if line.startswith("vmess://"):
                    base64_part = line.replace("vmess://", "")
                    decoded = base64.b64decode(base64_part).decode('utf-8')
                    config = json.loads(decoded)
                    ps = config.get("ps", "")
                    print(f"  {i}. {ps}")
            except:
                print(f"  {i}. خطا در نمایش")
        
    else:
        print(f"❌ خطا: {result.get('description')}")
        
except Exception as e:
    print(f"❌ مشکل اتصال: {e}")
