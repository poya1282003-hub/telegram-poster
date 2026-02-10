#!/usr/bin/env python3
import os
import requests
import base64
import json
from datetime import datetime, timedelta
import jdatetime
import urllib.parse

print("🤖 شروع ربات - تغییر لینک‌ها در حافظه")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

if not TOKEN or not CHANNEL:
    print("❌ توکن یا آیدی کانال تنظیم نشده!")
    exit(1)

print("✅ تنظیمات OK")

try:
    with open('last_line.txt', 'r') as f:
        last_line = int(f.read().strip())
except:
    last_line = 0

print(f"📌 آخرین خط ارسال شده: {last_line}")

try:
    with open('texts.txt', 'r', encoding='utf-8') as f:
        all_lines = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print("❌ فایل texts.txt پیدا نشد!")
    exit(1)

print(f"📄 تعداد کل خطوط: {len(all_lines)}")

if last_line >= len(all_lines):
    print("🎉 تمام خطوط ارسال شده‌اند!")
    exit(0)

raw_lines = []
for i in range(3):
    line_num = last_line + i
    if line_num < len(all_lines):
        raw_lines.append(all_lines[line_num])

if not raw_lines:
    print("❌ هیچ خطی برای ارسال نیست!")
    exit(0)

print(f"📤 دریافت {len(raw_lines)} خط خام...")

flags = [
    "🇨🇭", "🇺🇸", "🇬🇧", "🇩🇪", "🇨🇦", "🇫🇷", "🇮🇹", "🇯🇵",
    "🇰🇷", "🇸🇪", "🇳🇱", "🇦🇺", "🇳🇿", "🇸🇬", "🇹🇷", "🇷🇺",
    "🇧🇷", "🇮🇳", "🇨🇳", "🇪🇸", "🇵🇹", "🇬🇷", "🇫🇮", "🇳🇴",
    "🇩🇰", "🇦🇹", "🇧🇪", "🇮🇪", "🇵🇱", "🇨🇿", "🇭🇺", "🇷🇴",
    "🇺🇦", "🇮🇱", "🇦🇪", "🇸🇦", "🇿🇦", "🇲🇽", "🇦🇷", "🇨🇱"
]

def modify_link_in_memory(original_link, link_number):
    flag_index = link_number % len(flags)
    flag = flags[flag_index]
    
    new_name = f"{flag}  @v2reyonline ✓هر ۳۰ دقیقه آپدیت"
    
    if original_link.startswith(('vless://', 'trojan://', 'ss://')):
        if '#' in original_link:
            parts = original_link.split('#', 1)
            base_link = parts[0]
            new_link = f"{base_link}#{urllib.parse.quote(new_name)}"
            print(f"   🔄 تغییر نام در vless/trojan")
        else:
            new_link = f"{original_link}#{urllib.parse.quote(new_name)}"
            print(f"   ➕ اضافه کردن نام به vless/trojan")
        
        return new_link
    
    elif original_link.startswith('vmess://'):
        try:
            base64_str = original_link.replace('vmess://', '')
            decoded = base64.b64decode(base64_str).decode('utf-8')
            config = json.loads(decoded)
            
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
    
    else:
        print(f"   ⚠️ نوع لینک ناشناخته")
        return original_link

lines_to_send = []
print("\n🔧 در حال تغییر لینک‌ها:")
for i, original_link in enumerate(raw_lines):
    print(f"\nلینک {i+1}:")
    print(f"   اصلی: {original_link[:60]}...")
    
    modified_link = modify_link_in_memory(original_link, last_line + i)
    lines_to_send.append(modified_link)
    
    if '#' in modified_link:
        try:
            name_part = modified_link.split('#', 1)[1]
            decoded_name = urllib.parse.unquote(name_part)
            print(f"   📱 در V2Ray نمایش داده می‌شود: {decoded_name}")
        except:
            print(f"   📱 نام encode شده: {name_part[:30]}...")
    elif modified_link.startswith('vmess://'):
        print(f"   📱 vmess - نام در فیلد ps تغییر یافت")

post_number = (last_line // 3) + 1

utc_now = datetime.utcnow()
iran_time = utc_now + timedelta(hours=3, minutes=30)

shamsi_date = jdatetime.datetime.fromgregorian(
    year=iran_time.year,
    month=iran_time.month,
    day=iran_time.day,
    hour=iran_time.hour,
    minute=iran_time.minute
)

animated_emojis = ["🎯", "🚀", "⚡", "🔑", "🌊", "✨", "🎉", "🔥", "💫", "🌟"]
static_emojis = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙"]

main_emoji = animated_emojis[post_number % len(animated_emojis)]
hour_index = shamsi_date.hour % 12
time_emoji = static_emojis[hour_index]

date_str = shamsi_date.strftime("%Y/%m/%d")
time_str = shamsi_date.strftime("%H:%M")

header_line = f"{main_emoji}<b> #‌{post_number} post</b>  {time_emoji}<b>{time_str}</b>  📅<b>{date_str}</b>"

message = f"{header_line}\n\n"

all_lines_text = "\n".join(lines_to_send)
message += f"<pre>{all_lines_text}</pre>\n\n"

message += "🔄 هر ۳۰ دقیقه پست جدید\n\n"
message += "@V2REYONLINE"

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
        new_last = last_line + len(lines_to_send)
        with open('last_line.txt', 'w') as f:
            f.write(str(new_last))
        
        print(f"✅ پست #{post_number} ارسال شد")
        print(f"📍 موقعیت جدید: {new_last}")
        
        print(f"🕒 زمان ایران: {iran_time.strftime('%H:%M')}")
        print(f"📅 تاریخ شمسی: {date_str}")
        
        print("\n📋 خلاصه تغییرات:")
        print("=" * 50)
        for i, (original, modified) in enumerate(zip(raw_lines, lines_to_send), 1):
            print(f"\nلینک {i}:")
            print(f"قبل: {original[:50]}...")
            print(f"بعد: {modified[:50]}...")
            
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
