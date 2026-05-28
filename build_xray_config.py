#!/usr/bin/env python3
import json
import base64
import urllib.parse
import os

print("🔧 ساخت config.json شروع شد...")

def parse_vless(link):
    try:
        rest = link.replace('vless://', '')
        if '@' not in rest:
            return None
        uuid, rest = rest.split('@', 1)
        address_port, param_part = rest.split('?', 1) if '?' in rest else (rest, '')
        address, port = address_port.split(':', 1)
        port = port.split('#')[0].split('?')[0]
        
        params = {}
        if param_part:
            for p in param_part.split('&'):
                if '=' in p:
                    k, v = p.split('=', 1)
                    params[k] = urllib.parse.unquote(v)
        
        encryption = params.get('encryption', 'none')
        if encryption == '' or encryption == '""':
            encryption = 'none'
        
        print(f"✅ vless found: {address}:{port}")
        
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
        print(f"❌ vless error: {e}")
        return None

def build_config():
    if not os.path.exists('texts.txt'):
        print("❌ texts.txt not found!")
        return False
    
    with open('texts.txt', 'r', encoding='utf-8') as f:
        links = [l.strip() for l in f if l.strip()]
    
    print(f"📖 Total links: {len(links)}")
    
    if len(links) == 0:
        print("⚠️ No links found, using direct config")
        config = {
            "log": {"loglevel": "warning"},
            "inbounds": [{
                "port": 1080,
                "protocol": "socks",
                "listen": "127.0.0.1",
                "settings": {"auth": "noauth", "udp": True}
            }],
            "outbounds": [{
                "protocol": "freedom",
                "settings": {},
                "tag": "direct"
            }]
        }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ config.json created (direct mode)")
        return True
    
    outbound = None
    for link in links[:10]:
        if link.startswith('vless://'):
            outbound = parse_vless(link)
            if outbound:
                break
    
    if not outbound:
        print("⚠️ No valid vless link, using direct")
        outbound = {"protocol": "freedom", "settings": {}, "tag": "direct"}
    
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": 1080,
            "protocol": "socks",
            "listen": "127.0.0.1",
            "settings": {"auth": "noauth", "udp": True}
        }],
        "outbounds": [outbound, {"protocol": "freedom", "settings": {}, "tag": "direct"}],
        "routing": {
            "rules": [{
                "type": "field",
                "network": "tcp,udp",
                "outboundTag": "proxy"
            }]
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ config.json created successfully!")
    return True

if __name__ == "__main__":
    build_config()
