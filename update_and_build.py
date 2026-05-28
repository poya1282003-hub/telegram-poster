#!/usr/bin/env python3
"""
یک اسکریپت واحد برای آپدیت لینک‌ها و ساخت کانفیگ Xray
"""

import requests
import re
import json
import base64
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

# ==================== تنظیمات ====================
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
]

# ==================== توابع استخراج لینک ====================
def extract_proxy_links(text: str) -> List[str]:
    patterns = [r'vless://[^\s]+', r'vmess://[^\s]+', r'trojan://[^\s]+', r'ss://[^\s]+']
    links = []
    for pattern in patterns:
        found = re.findall(pattern, text)
        links.extend(found)
    return links

def fetch_proxies_from_source(url: str) -> List[str]:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            proxies = extract_proxy_links(response.text)
            print(f"✅ {url.split('/')[-1]}: {len(proxies)} لینک")
            return proxies
        return []
    except Exception as e:
        print(f"❌ خطا در {url}: {e}")
        return []

# ==================== توابع تبدیل (با اصلاح encryption) ====================
def parse_vless(link: str) -> Optional[Dict]:
    try:
        rest = link.replace('vless://', '')
        if '@' not in rest:
            return None
        uuid, rest = rest.split('@', 1)
        address_port, param_part = rest.split('?', 1) if '?' in rest else (rest, '')
        if ':' not in address_port:
            return None
        address, port = address_port.split(':', 1)
        port = port.split('#')[0].split('?')[0]
        
        params = {}
        if param_part:
            for p in param_part.split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = urllib.parse.unquote(v)
        
        # 🔴 کلید حل مشکل: اینجا encryption را强制 می‌کنیم
        encryption = params.get('encryption', 'none')
        if encryption == '' or encryption == '""' or encryption == '%22%22':
            encryption = 'none'
        
        return {
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": address,
                    "port": int(port),
                    "users": [{
                        "id": uuid,
                        "encryption": encryption,  # ✅ حتماً "none" است
                        "flow": params.get('flow', ''),
                        "level": 0
                    }]
                }]
            },
            "streamSettings": {
                "network": params.get('type', 'tcp'),
                "security": params.get('security', 'none'),
                "tlsSettings": {} if params.get('security') != 'tls' else {
                    "allowInsecure": True,
                    "serverName": params.get('sni', address)
                }
            },
            "tag": "proxy"
        }
    except Exception as e:
        print(f"   خطا در vless: {e}")
        return None

def parse_vmess(link: str) -> Optional[Dict]:
    try:
        b64_part = link.replace('vmess://', '')
        b64_part += '=' * (4 - len(b64_part) % 4)
        decoded = base64.b64decode(b64_part).decode('utf-8')
        data = json.loads(decoded)
        return {
            "protocol": "vmess",
            "settings": {
                "vnext": [{
                    "address": data.get('add', ''),
                    "port": int(data.get('port', 0)),
                    "users": [{
                        "id": data.get('id', ''),
                        "security": data.get('scy', 'auto'),
                        "level": 0
                    }]
                }]
            },
            "streamSettings": {
                "network": data.get('net', 'tcp'),
                "security": data.get('tls', 'none'),
                "wsSettings": {
                    "path": data.get('path', '/'),
                    "headers": {"Host": data.get('host', '')}
                } if data.get('net') == 'ws' else None
            },
            "tag": "proxy"
        }
    except:
        return None

def parse_ss(link: str) -> Optional[Dict]:
    try:
        rest = link.replace('ss://', '')
        if '@' not in rest:
            return None
        b64_part, rest = rest.split('@', 1)
        b64_part += '=' * (4 - len(b64_part) % 4)
        decoded = base64.b64decode(b64_part).decode('utf-8')
        method, password = decoded.split(':', 1)
        address = rest.split(':', 1)[0]
        port = rest.split(':', 1)[1].split('#', 1)[0].split('?', 1)[0]
        return {
            "protocol": "shadowsocks",
            "settings": {
                "servers": [{
                    "address": address,
                    "port": int(port),
                    "method": method,
                    "password": password,
                    "level": 0
                }]
            },
            "tag": "proxy"
        }
    except:
        return None

def build_config_from_links(links: List[str]) -> Dict[str, Any]:
    outbound = None
    for link in links:
        if link.startswith('vless://'):
            outbound = parse_vless(link)
        elif link.startswith('vmess://'):
            outbound = parse_vmess(link)
        elif link.startswith('ss://'):
            outbound = parse_ss(link)
        
        if outbound:
            print(f"✅ استفاده از: {link[:50]}...")
            break
    
    if not outbound:
        print("⚠️ هیچ لینک معتبری یافت نشد، از حالت direct استفاده می‌شود")
        outbound = {"protocol": "freedom", "settings": {}, "tag": "direct"}
    
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [
            {
                "port": 1080,
                "protocol": "socks",
                "listen": "127.0.0.1",
                "settings": {"auth": "noauth", "udp": True},
                "tag": "socks-in"
            },
            {
                "port": 8080,
                "protocol": "http",
                "listen": "127.0.0.1",
                "settings": {},
                "tag": "http-in"
            }
        ],
        "outbounds": [
            outbound,
            {"protocol": "freedom", "settings": {}, "tag": "direct"}
        ],
        "routing": {
            "rules": [
                {"type": "field", "ip": ["geoip:private"], "outboundTag": "direct"},
                {"type": "field", "network": "tcp,udp", "outboundTag": "proxy"}
            ]
        }
    }

# ==================== اصلی ====================
def main():
    print("=" * 60)
    print(f"🔄 شروع - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. جمع‌آوری لینک‌ها
    all_links = []
    for source in PROXY_SOURCES:
        new_links = fetch_proxies_from_source(source)
        all_links.extend(new_links)
    
    # حذف تکراری
    unique_links = list(dict.fromkeys(all_links))
    print(f"📊 لینک‌های منحصربه‌فرد: {len(unique_links)}")
    
    # 2. ذخیره در texts.txt (برای ربات تلگرام)
    with open('texts.txt', 'w', encoding='utf-8') as f:
        for link in unique_links:
            f.write(link + '\n')
    print("💾 texts.txt ذخیره شد")
    
    # 3. ساخت config.json
    config = build_config_from_links(unique_links)
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("💾 config.json ذخیره شد")
    
    # 4. نمایش اطلاعات encryption برای اطمینان
    for out in config['outbounds']:
        if out.get('protocol') == 'vless':
            enc = out['settings']['vnext'][0]['users'][0]['encryption']
            print(f"🔧 مقدار encryption: '{enc}' (باید 'none' باشد)")
            break
    
    print("=" * 60)

if __name__ == "__main__":
    main()
