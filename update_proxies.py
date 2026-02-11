#!/usr/bin/env python3
"""
اسکریپت آپدیت خودکار پروکسی‌های جهانی
هر ۳۰ دقیقه لینک‌های جدید را از منابع دریافت می‌کند
"""

import requests
import re
from datetime import datetime

# لیست منابع پروکسی جهانی
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
]

def extract_proxy_links(text):
    """استخراج لینک‌های پروکسی از متن"""
    patterns = [
        r'vless://[^\s]+',
        r'vmess://[^\s]+',
        r'trojan://[^\s]+',
        r'ss://[^\s]+',
    ]
    
    links = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        links.extend(found)
    return links

def fetch_proxies_from_source(url):
    """دریافت لینک از یک منبع"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            proxies = extract_proxy_links(response.text)
            print(f"✅ {url.split('/')[-1]}: {len(proxies)} لینک")
            return proxies
        return []
    except:
        return []

def update_proxies_file():
    """آپدیت فایل texts.txt"""
    print("=" * 50)
    print(f"🔄 شروع آپدیت - {datetime.now().strftime('%H:%M:%S')}")
    
    # خواندن لینک‌های موجود
    try:
        with open('texts.txt', 'r', encoding='utf-8') as f:
            existing = [line.strip() for line in f if line.strip()]
    except:
        existing = []
    
    print(f"📊 لینک‌های موجود: {len(existing)}")
    
    # دریافت لینک‌های جدید
    all_new = []
    for source in PROXY_SOURCES:
        new = fetch_proxies_from_source(source)
        all_new.extend(new)
    
    # ادغام و حذف تکراری
    unique = list(dict.fromkeys(existing + all_new))
    
    # ذخیره
    with open('texts.txt', 'w', encoding='utf-8') as f:
        for link in unique:
            f.write(link + '\n')
    
    print(f"📈 لینک‌های جدید: {len(all_new)}")
    print(f"📁 کل لینک‌ها: {len(unique)}")
    print("=" * 50)

if __name__ == "__main__":
    update_proxies_file()
