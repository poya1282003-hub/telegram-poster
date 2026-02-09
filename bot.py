#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

print("=" * 50)
print("🤖 ربات تلگرام - شروع کار")
print("=" * 50)

# خواندن از Secrets گیت‌هاب
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "")

# بررسی تنظیمات
if not TOKEN or "توکن_" in TOKEN:
    print("❌ توکن ربات تنظیم نشده!")
    exit(1)

if not CHANNEL or "آیدی_" in CHANNEL:
    print("❌ آیدی کانال تنظیم نشده!")
    exit(1)

# ================== مرحله ۱: خواندن last_line.txt ==================
print("\n📁 مرحله ۱: خواندن وضعیت فعلی")
try:
    with open('last_line.txt', 'r') as f:
        last_line = int(f.read().strip())
    print(f"✅ آخرین خط ارسال شده از فایل: {last_line}")
except FileNotFoundError:
    print("⚠️ فایل last_line.txt پیدا نشد. شروع از خط 0")
    last_line = 0
    with open('last_line.txt', 'w') as f:
        f.write('0')
except ValueError:
    print("⚠️ محتوای last_line.txt نامعتبر است. شروع از خط 0")
    last_line = 0
    with open('last_line.txt', 'w') as f:
        f.write('0')

# ================== مرحله ۲: خواندن texts.txt ==================
print("\n📄 مرحله ۲: خواندن محتوای texts.txt")
try:
    with open('texts.txt', 'r', encoding='utf-8') as f:
        all_lines = [line.rstrip('\n') for line in f]
    print(f"✅ تعداد کل خطوط: {len(all_lines)}")
    
except FileNotFoundError:
    print("❌ فایل texts.txt پیدا نشد!")
    exit(1)

# ================== مرحله ۳: بررسی پایان کار ==================
if last_line >= len(all_lines):
    print("\n🎉 تمام خطوط ارسال شده‌اند!")
    print(f"last_line: {last_line}, total_lines: {len(all_lines)}")
    exit(0)

# ================== مرحله ۴: انتخاب ۳ خط بعدی ==================
print(f"\n🎯 مرحله ۴: انتخاب ۳ خط بعدی (از خط {last_line + 1})")
lines_to_send = []
for i in range(3):
    line_num = last_line + i
    if line_num < len(all_lines):
        lines_to_send.append(all_lines[line_num])
        print(f"  ✓ خط {line_num + 1}: {all_lines[line_num][:30]}...")

if not lines_to_send:
    print("❌ هیچ خطی برای ارسال وجود ندارد!")
    exit(0)

# ================== مرحله ۵: ساخت پیام نهایی (بدون جداکننده) ==================
print("\n📝 مرحله ۵: ساخت پیام نهایی")
# فقط خط‌ها را با یک اینتر ساده به هم وصل کن
message = "\n".join(lines_to_send)

# ================== مرحله ۶: ارسال به تلگرام ==================
print("\n📤 مرحله ۶: ارسال به تلگرام")
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
        # ================== مرحله ۷: به‌روزرسانی last_line.txt ==================
        new_last_line = last_line + len(lines_to_send)
        with open('last_line.txt', 'w') as f:
            f.write(str(new_last_line))
        
        print(f"\n✅ ارسال موفقیت‌آمیز!")
        print(f"📊 آمار:")
        print(f"   • خطوط ارسال شده: {len(lines_to_send)}")
        print(f"   • از خط: {last_line + 1} تا {new_last_line}")
        print(f"   • last_line.txt به‌روز شد: {new_last_line}")
        
    else:
        print(f"❌ خطای تلگرام: {result.get('description')}")
        
except Exception as e:
    print(f"❌ خطای اتصال: {e}")

print("\n" + "=" * 50)
print("پایان اجرا")
print("=" * 50)
