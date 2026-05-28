#!/usr/bin/env python3
"""
تبدیل لینک‌های texts.txt به config.json معتبر برای Xray
"""

import json
import base64
import urllib.parse
import os

def parse_vless(link):
    """تبدیل لینک vless با encryption صحیح"""
    try:
        rest = link.replace('vless://', '')
        uuid, rest = rest.split('@', 1)
        address_port, param_part = rest.split('?', 1) if '?' in rest else (rest, '')
        address, port = address_port.split(':', 1)
        port = port.split('#')[0]
        
        # استخراج پارامترها
        params = {}
        if param_part:
            for p in param_part.split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = urllib.parse.unquote(v)
        
        # 🔴 کلید حل مشکل: encryption MUST be "none"
        encryption = params.get('encryption', 'none')
        if encryption == '' or encryption == '""':
            encryption = 'none'
        
        return {
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": address,
                    "port": int(port),
                    "users": [{
                        "id": uuid,
                        "encryption": encryption,
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
        print(f"❌ خطا در parse vless: {e}")
        return None

def parse_vmess(link):
    """تبدیل لینک vmess به دیکشنری"""
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

def build_config():
    """ساخت config.json از texts.txt"""
    
    # چک کردن وجود فایل texts.txt
    if not os.path.exists('texts.txt'):
        print("❌ فایل texts.txt پیدا نشد! اول update_proxies.py را اجرا کنید.")
        return False
    
    # خواندن لینک‌ها
    with open('texts.txt', 'r', encoding='utf-8') as f:
        links = [l.strip() for l in f if l.strip()]
    
    print(f"📖 تعداد کل لینک‌ها: {len(links)}")
    
    # پیدا کردن اولین لینک معتبر
    outbound = None
    
    for link in links:
        if link.startswith('vless://'):
            outbound = parse_vless(link)
            if outbound:
                print(f"✅ لینک vless پیدا شد")
                break
        elif link.startswith('vmess://'):
            outbound = parse_vmess(link)
            if outbound:
                print(f"✅ لینک vmess پیدا شد")
                break
    
    if not outbound:
        print("❌ هیچ لینک معتبری پیدا نشد!")
        return False
    
    # ساخت کانفیگ کامل
    config = {
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
            {
                "protocol": "freedom",
                "settings": {},
                "tag": "direct"
            }
        ],
        "routing": {
            "rules": [
                {
                    "type": "field",
                    "ip": ["geoip:private"],
                    "outboundTag": "direct"
                },
                {
                    "type": "field",
                    "network": "tcp,udp",
                    "outboundTag": "proxy"
                }
            ]
        }
    }
    
    # ذخیره فایل
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ فایل config.json با موفقیت ساخته شد!")
    
    # نمایش مقدار encryption برای اطمینان
    if outbound['protocol'] == 'vless':
        enc = outbound['settings']['vnext'][0]['users'][0]['encryption']
        print(f"🔧 مقدار encryption: '{enc}' (باید 'none' باشد)")
    
    return True

if __name__ == "__main__":
    build_config()
