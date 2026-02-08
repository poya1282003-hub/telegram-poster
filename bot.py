#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

# ==================== تنظیمات ====================
# این مقادیر را در Secrets گیت‌هاب قرار می‌دهیم
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
# =================================================

def read_last_line():
    """خواندن شماره آخرین خط ارسال شده"""
    try:
        with open('last_line.txt', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_last_line(line_num):
    """ذخیره شماره خط جدید"""
    with open('last_line.txt', 'w') as f:
        f.write(str(line_num))

def read_texts():
    """خواندن همه خطوط از فایل"""
    with open('texts.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def send_to_telegram(message):
    """ارسال پیام به کانال تلگرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def main():
    print("🤖 شروع ربات تلگرام...")
    
    # بررسی تنظیمات
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده!")
        print("لطفاً در GitHub Secrets تنظیم کنید:")
        print("1. TELEGRAM_BOT_TOKEN")
        print("2. TELEGRAM_CHANNEL_ID")
        return
    
    # خواندن وضعیت
    last_line = read_last_line()
    print(f"📖 آخرین خط ارسال شده: {last_line}")
    
    # خواندن متن‌ها
    texts = read_texts()
    print(f"📄 تعداد کل خطوط: {len(texts)}")
    
    # بررسی پایان متن
    if last_line >= len(texts):
        print("✅ همه خطوط ارسال شده‌اند!")
        return
    
    # انتخاب ۵ خط بعدی
    lines_to_send = texts[last_line:last_line + 5]
    print(f"📤 ارسال {len(lines_to_send)} خط...")
    
    # ساخت پیام
    separator = "\n" + "─" * 25 + "\n"
    message = separator.join(lines_to_send)
    
    # اضافه کردن هدر
    from datetime import datetime
    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    final_message = f"🕒 {now}\n\n{message}"
    
    # ارسال
    result = send_to_telegram(final_message)
    
    if result.get('ok'):
        # بروزرسانی وضعیت
        new_last_line = last_line + len(lines_to_send)
        save_last_line(new_last_line)
        print(f"✅ ارسال موفق! خط جدید: {new_last_line}")
        
        # commit تغییرات
        os.system('git config --global user.email "actions@github.com"')
        os.system('git config --global user.name "GitHub Actions"')
        os.system('git add last_line.txt')
        os.system('git commit -m "Auto: Update last_line to ' + str(new_last_line) + '"')
        os.system('git push')
    else:
        print(f"❌ خطا: {result.get('description')}")

if __name__ == "__main__":
    main()
