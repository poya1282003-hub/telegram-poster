#!/usr/bin/env python3
"""
اسکریپت آپدیت خودکار پروکسی‌های جهانی هر ۳۰ دقیقه
"""

import requests
import re
from datetime import datetime

# منابع پروکسی جهانی
PROXY_SOURCES = [
    # منابع اصلی
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    
    # منابع کمکی
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
    """دریافت لینک‌ها از یک منبع"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            proxies = extract_proxy_links(response.text)
            print(f"✅ {url.split('/')[-1]}: {len(proxies)} پروکسی")
            return proxies
        else:
            print(f"⚠️ {url.split('/')[-1]}: خطا {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ {url.split('/')[-1]}: {str(e)[:50]}")
        return []

def update_proxies_file():
    """آپدیت فایل texts.txt"""
    print("=" * 50)
    print(f"🔄 آپدیت پروکسی‌ها - {datetime.now().strftime('%H:%M:%S')}")
    
    # خواندن پروکسی‌های موجود
    try:
        with open('texts.txt', 'r', encoding='utf-8') as f:
            existing = [line.strip() for line in f if line.strip()]
    except:
        existing = []
    
    print(f"📊 موجود: {len(existing)} پروکسی")
    
    # دریافت از همه منابع
    all_new = []
    for source in PROXY_SOURCES:
        new_proxies = fetch_proxies_from_source(source)
        all_new.extend(new_proxies)
    
    # ادغام و حذف تکراری
    unique_proxies = list(dict.fromkeys(existing + all_new))
    
    # ذخیره
    with open('texts.txt', 'w', encoding='utf-8') as f:
        for proxy in unique_proxies:
            f.write(proxy + '\n')
    
    print("=" * 50)
    print(f"✅ آپدیت کامل شد!")
    print(f"📈 جدید: {len(all_new)} | کل: {len(unique_proxies)}")
    
    return len(unique_proxies)

if __name__ == "__main__":
    update_proxies_file()
