#!/usr/bin/env python3
import os
import requests
import base64
import json
from datetime import datetime, timedelta
import jdatetime
import urllib.parse

print("🤖 شروع ربات - تغییر لینک‌ها در حافظه")

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

# ==================== اصلاح لینک در حافظه ====================
def modify_link_in_memory(original_link, link_number):
    """
    لینک را در حافظه تغییر می‌دهد (بدون ذخیره در فایل)
    """
    # انتخاب پرچم
    flag_index = link_number % len(flags)
    flag = flags[flag_index]
    
    # نام جدید
    new_name = f"{flag}  @v2reyonline ✓هر ۳۰ دقیقه آپدیت"
    
    # 🔴 ۱. اگر لینک vless یا trojan است (بیشتر لینک‌های شما)
    if original_link.startswith(('vless://', 'trojan://', 'ss://')):
        if '#' in original_link:
            # لینک دارای نام است → نام را تغییر بده
            parts = original_link.split('#', 1)
            base_link = parts[0]
            new_link = f"{base_link}#{urllib.parse.quote(new_name)}"
            print(f"   🔄 تغییر نام در vless/trojan")
        else:
            # لینک بدون نام است → نام اضافه کن
            new_link = f"{original_link}#{urllib.parse.quote(new_name)}"
            print(f"   ➕ اضافه کردن نام به vless/trojan")
        
        return new_link
    
    # 🔴 ۲. اگر لینک vmess است
    elif original_link.startswith('vmess://'):
        try:
            base64_str = original_link.replace('vmess://', '')
            decoded = base64.b64decode(base64_str).decode('utf-8')
            config = json.loads(decoded)
            
            # تغییر فیلد ps
            old_name = config.get('ps', 'بدون نام')
            config['ps'] = new_name
            
            new_json = json.dumps(config, separators=(',', ':'))
            new_base64 = base64.b64encode(new_json.encode()).decode()
            new_link = f"vmess://{new_base64}"
            
            print(f"   🔄 تغییر vmess: '{old_name[:20]}...' → '{new_name}'")
            return new_link
            
        except:
            print(f"   ❌ خطا در پردازش vmess")
            return original_link
    
    # 🔴 ۳. سایر لینک‌ها
    else:
        print(f"   ⚠️ نوع لینک ناشناخته")
        return original_link

# اصلاح همه لینک‌ها در حافظه
lines_to_send = []
print("\n🔧 در حال تغییر لینک‌ها:")
for i, original_link in enumerate(raw_lines):
    print(f"\nلینک {i+1}:")
    print(f"   اصلی: {original_link[:60]}...")
    
    modified_link = modify_link_in_memory(original_link, last_line + i)
    lines_to_send.append(modified_link)
    
    # نمایش نام جدید
    if '#' in modified_link:
        try:
            name_part = modified_link.split('#', 1)[1]
            decoded_name = urllib.parse.unquote(name_part)
            print(f"   📱 در V2Ray نمایش داده می‌شود: {decoded_name}")
        except:
            print(f"   📱 نام encode شده: {name_part[:30]}...")
    elif modified_link.startswith('vmess://'):
        print(f"   📱 vmess - نام در فیلد ps تغییر یافت")

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

# ساخت پیام
message = f"{main_emoji}<b> post #{post_number}</b>  {time_emoji}<b>{time_str}</b>  📅<b>{date_str}</b>\n\n"

# 🔴 ارسال لینک‌های تغییر یافته (نه لینک‌های اصلی)
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
        
        print(f"\n✅ پست #{post_number} ارسال شد")
        print(f"📍 موقعیت جدید: {new_last}")
        
        print("\n📋 خلاصه تغییرات:")
        print("=" * 50)
        for i, (original, modified) in enumerate(zip(raw_lines, lines_to_send), 1):
            print(f"\nلینک {i}:")
            print(f"قبل: {original[:50]}...")
            print(f"بعد: {modified[:50]}...")
            
            # استخراج نام برای نمایش
            if modified != original:
                if '#' in modified:
                    name_part = modified.split('#', 1)[1]
                    try:
                        name = urllib.parse.unquote(name_part)
                        print(f"✅ در V2Ray: {name}")
                    except:
                        print(f"✅ تغییر یافت (encode شده)")
                else:
                    print(f"✅ تغییر یافت")
            else:
                print(f"⚠️ بدون تغییر")
        
    else:
        print(f"❌ خطا: {result.get('description')}")
        
except Exception as e:
    print(f"❌ مشکل اتصال: {e}")
