#!/usr/bin/env python3
import os

print("=== تست کانال جدید ===")
print()

# خواندن از Secrets
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "NOT_SET")
CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID", "NOT_SET")

print("📊 اطلاعات خوانده شده از GitHub Secrets:")
print(f"1. توکن ربات: {TOKEN[:15]}..." if len(TOKEN) > 10 else f"1. توکن ربات: {TOKEN}")
print(f"2. آیدی کانال: {CHANNEL}")
print()

# بررسی
if TOKEN == "NOT_SET":
    print("❌ توکن در Secrets تنظیم نشده!")
    print("   به Settings → Secrets → TELEGRAM_BOT_TOKEN برو")
elif CHANNEL == "NOT_SET":
    print("❌ آیدی کانال در Secrets تنظیم نشده!")
    print("   به Settings → Secrets → TELEGRAM_CHANNEL_ID برو")
else:
    print("✅ هر دو Secret تنظیم شده‌اند!")
    print()
    print("🔍 بررسی فرمت آیدی کانال:")
    if CHANNEL.startswith("@"):
        print(f"   ✅ کانال عمومی: {CHANNEL}")
    elif CHANNEL.startswith("-100"):
        print(f"   ✅ کانال خصوصی: {CHANNEL}")
    else:
        print(f"   ⚠️ فرمت غیرمعمول: {CHANNEL}")
        print("   برای کانال عمومی باید با @ شروع شود")
        print("   برای کانال خصوصی باید با -100 شروع شود")
