#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ربات تلگرام - ارسال خودکار پروکسی‌ها
ورژن: 3.0.0 | طراحی حرفه‌ای
"""

import os
import sys
import json
import base64
import requests
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import jdatetime

# ==================== تنظیمات ====================
class Config:
    """کلاس مدیریت تنظیمات"""
    
    # اطلاعات نسخه
    VERSION = "3.0.0"
    AUTHOR = "@v2reyonline"
    
    # فایل‌ها
    TEXTS_FILE = "texts.txt"
    STATE_FILE = "last_line.txt"
    LOG_FILE = "bot_debug.log"
    
    # تلگرام
    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
    REQUEST_TIMEOUT = 15
    
    # پرچم‌های کشورها (۴۰ پرچم مختلف)
    FLAGS = [
        "🇨🇭", "🇺🇸", "🇬🇧", "🇩🇪", "🇨🇦", "🇫🇷", "🇮🇹", "🇯🇵",
        "🇰🇷", "🇸🇪", "🇳🇱", "🇦🇺", "🇳🇿", "🇸🇬", "🇹🇷", "🇷🇺",
        "🇧🇷", "🇮🇳", "🇨🇳", "🇪🇸", "🇵🇹", "🇬🇷", "🇫🇮", "🇳🇴",
        "🇩🇰", "🇦🇹", "🇧🇪", "🇮🇪", "🇵🇱", "🇨🇿", "🇭🇺", "🇷🇴",
        "🇺🇦", "🇮🇱", "🇦🇪", "🇸🇦", "🇿🇦", "🇲🇽", "🇦🇷", "🇨🇱"
    ]
    
    # ایموجی‌های متحرک برای پست‌ها
    ANIMATED_EMOJIS = ["🎯", "🚀", "⚡", "🔑", "🌊", "✨", "🎉", "🔥", "💫", "🌟"]
    
    # ایموجی‌های ساعت
    CLOCK_EMOJIS = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
    
    @classmethod
    def get_bot_info(cls) -> str:
        """اطلاعات نسخه ربات"""
        return f"🤖 ربات تلگرام v{cls.VERSION} | {cls.AUTHOR}"


class Logger:
    """سیستم لاگ حرفه‌ای"""
    
    COLORS = {
        'INFO': '\033[94m',      # آبی
        'SUCCESS': '\033[92m',   # سبز
        'WARNING': '\033[93m',   # زرد
        'ERROR': '\033[91m',     # قرمز
        'DEBUG': '\033[90m',     # خاکستری
        'RESET': '\033[0m'       # ریست
    }
    
    @staticmethod
    def log(level: str, message: str, emoji: str = ""):
        """ثبت لاگ با رنگ‌بندی"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = Logger.COLORS.get(level, Logger.COLORS['INFO'])
        
        if emoji:
            message = f"{emoji} {message}"
        
        print(f"{color}[{timestamp}] [{level}] {message}{Logger.COLORS['RESET']}")
    
    @staticmethod
    def info(message: str, emoji: str = "ℹ️"):
        """لاگ اطلاعات"""
        Logger.log('INFO', message, emoji)
    
    @staticmethod
    def success(message: str, emoji: str = "✅"):
        """لاگ موفقیت"""
        Logger.log('SUCCESS', message, emoji)
    
    @staticmethod
    def warning(message: str, emoji: str = "⚠️"):
        """لاگ هشدار"""
        Logger.log('WARNING', message, emoji)
    
    @staticmethod
    def error(message: str, emoji: str = "❌"):
        """لاگ خطا"""
        Logger.log('ERROR', message, emoji)
    
    @staticmethod
    def debug(message: str, emoji: str = "🔍"):
        """لاگ دیباگ"""
        Logger.log('DEBUG', message, emoji)


class TimeManager:
    """مدیریت زمان و تاریخ"""
    
    @staticmethod
    def get_iran_time() -> datetime:
        """دریافت زمان ایران (UTC + 3:30)"""
        utc_now = datetime.utcnow()
        iran_time = utc_now + timedelta(hours=3, minutes=30)
        return iran_time
    
    @staticmethod
    def get_shamsi_date(iran_time: datetime) -> Tuple[str, str]:
        """تبدیل به تاریخ شمسی"""
        shamsi = jdatetime.datetime.fromgregorian(
            year=iran_time.year,
            month=iran_time.month,
            day=iran_time.day,
            hour=iran_time.hour,
            minute=iran_time.minute
        )
        
        date_str = shamsi.strftime("%Y/%m/%d")
        time_str = shamsi.strftime("%H:%M")
        
        return date_str, time_str
    
    @staticmethod
    def get_time_emoji(hour: int) -> str:
        """دریافت ایموجی ساعت متناسب با زمان"""
        hour_index = hour % 12
        return Config.CLOCK_EMOJIS[hour_index]


class LinkProcessor:
    """پردازش و اصلاح لینک‌ها"""
    
    @staticmethod
    def modify_link(original_link: str, link_number: int) -> str:
        """
        اصلاح لینک برای نمایش نام @v2reyonline
        پشتیبانی از: vless, trojan, vmess, ss
        """
        try:
            # انتخاب پرچم
            flag = Config.FLAGS[link_number % len(Config.FLAGS)]
            
            # نام جدید برای نمایش
            new_name = f"{flag}  @v2reyonline ✓هر ۳۰ دقیقه آپدیت"
            
            Logger.debug(f"در حال پردازش لینک #{link_number + 1}", "🔗")
            
            # پردازش بر اساس نوع لینک
            if original_link.startswith(('vless://', 'trojan://', 'ss://')):
                return LinkProcessor._process_standard_link(original_link, new_name)
            
            elif original_link.startswith('vmess://'):
                return LinkProcessor._process_vmess_link(original_link, new_name)
            
            else:
                Logger.warning(f"نوع لینک ناشناخته: {original_link[:50]}...", "❓")
                return original_link
                
        except Exception as e:
            Logger.error(f"خطا در پردازش لینک: {e}", "🛠️")
            return original_link
    
    @staticmethod
    def _process_standard_link(link: str, new_name: str) -> str:
        """پردازش لینک‌های vless, trojan, ss"""
        if '#' in link:
            parts = link.split('#', 1)
            base_link = parts[0]
            new_link = f"{base_link}#{urllib.parse.quote(new_name)}"
            Logger.debug("نام لینک vless/trojan تغییر یافت", "🔄")
        else:
            new_link = f"{link}#{urllib.parse.quote(new_name)}"
            Logger.debug("نام به لینک vless/trojan اضافه شد", "➕")
        
        return new_link
    
    @staticmethod
    def _process_vmess_link(link: str, new_name: str) -> str:
        """پردازش لینک‌های vmess"""
        try:
            base64_str = link.replace('vmess://', '')
            decoded = base64.b64decode(base64_str).decode('utf-8')
            config = json.loads(decoded)
            
            old_name = config.get('ps', 'بدون نام')
            config['ps'] = new_name
            
            new_json = json.dumps(config, separators=(',', ':'))
            new_base64 = base64.b64encode(new_json.encode()).decode()
            new_link = f"vmess://{new_base64}"
            
            Logger.debug(f"vmess: '{old_name[:20]}...' → '{new_name}'", "🔄")
            return new_link
            
        except Exception as e:
            Logger.error(f"خطا در پردازش vmess: {e}", "⚠️")
            return link


class TelegramBot:
    """مدیریت ارتباط با تلگرام"""
    
    def __init__(self, token: str, channel_id: str):
        self.token = token
        self.channel_id = channel_id
        self.api_url = Config.TELEGRAM_API_URL.format(token=token)
    
    def send_message(self, text: str) -> Tuple[bool, Optional[str]]:
        """ارسال پیام به کانال تلگرام"""
        try:
            payload = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
                'disable_notification': False
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            result = response.json()
            
            if result.get('ok'):
                message_id = result['result']['message_id']
                Logger.success(f"پیام با موفقیت ارسال شد (ID: {message_id})", "📤")
                return True, None
            else:
                error_msg = result.get('description', 'خطای ناشناخته')
                Logger.error(f"خطای تلگرام: {error_msg}", "📛")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            Logger.error("اتصال به تلگرام timeout خورد", "⏰")
            return False, "Timeout"
        except Exception as e:
            Logger.error(f"خطای اتصال: {e}", "🔌")
            return False, str(e)


class StateManager:
    """مدیریت وضعیت و فایل‌ها"""
    
    @staticmethod
    def load_state() -> int:
        """بارگذاری وضعیت فعلی از فایل"""
        try:
            with open(Config.STATE_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.isdigit():
                    last_line = int(content)
                    Logger.info(f"وضعیت بارگذاری شد: خط {last_line}", "📖")
                    return last_line
                else:
                    Logger.warning(f"مقدار نامعتبر در {Config.STATE_FILE}: {content}", "⚠️")
                    return 0
        except FileNotFoundError:
            Logger.warning(f"فایل {Config.STATE_FILE} یافت نشد. شروع از خط 0", "📝")
            return 0
        except Exception as e:
            Logger.error(f"خطا در خواندن وضعیت: {e}", "❌")
            return 0
    
    @staticmethod
    def save_state(last_line: int) -> bool:
        """ذخیره وضعیت جدید"""
        try:
            with open(Config.STATE_FILE, 'w', encoding='utf-8') as f:
                f.write(str(last_line))
            Logger.success(f"وضعیت ذخیره شد: خط {last_line}", "💾")
            return True
        except Exception as e:
            Logger.error(f"خطا در ذخیره وضعیت: {e}", "❌")
            return False
    
    @staticmethod
    def load_texts() -> list:
        """بارگذاری متن‌ها از فایل"""
        try:
            with open(Config.TEXTS_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            Logger.info(f"تعداد خطوط بارگذاری شده: {len(lines)}", "📄")
            return lines
            
        except FileNotFoundError:
            Logger.error(f"فایل {Config.TEXTS_FILE} یافت نشد!", "🚫")
            sys.exit(1)
        except Exception as e:
            Logger.error(f"خطا در خواندن فایل متن‌ها: {e}", "❌")
            sys.exit(1)


class PostBuilder:
    """سازنده پیام تلگرام"""
    
    @staticmethod
    def build_header(post_number: int, time_str: str, date_str: str, 
                    main_emoji: str, time_emoji: str) -> str:
        """ساخت هدر پیام"""
        header = f"{main_emoji}<b> post #{post_number}</b>  "
        header += f"{time_emoji}<b>{time_str}</b>  "
        header += f"📅<b>{date_str}</b>\n\n"
        return header
    
    @staticmethod
    def build_content(links: list) -> str:
        """ساخت محتوای پیام"""
        content = "<pre>" + "\n".join(links) + "</pre>\n\n"
        return content
    
    @staticmethod
    def build_footer() -> str:
        """ساخت فوتر پیام"""
        footer = "🔄 هر ۳۰ دقیقه پست جدید\n\n"
        footer += "@V2REYONLINE"
        return footer
    
    @staticmethod
    def build_complete_message(header: str, content: str, footer: str) -> str:
        """ساخت پیام کامل"""
        return header + content + footer


# ==================== اجرای اصلی ====================
def main():
    """تابع اصلی اجرای ربات"""
    
    Logger.info(Config.get_bot_info(), "🚀")
    Logger.info("شروع ربات تلگرام", "🤖")
    
    # ==================== بررسی تنظیمات ====================
    Logger.info("بررسی تنظیمات...", "🔧")
    
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID")
    
    if not TOKEN or not CHANNEL:
        Logger.error("توکن یا آیدی کانال تنظیم نشده است!", "🚫")
        Logger.info("لطفاً در GitHub Secrets تنظیم کنید:", "💡")
        Logger.info("1. TELEGRAM_BOT_TOKEN", "🔑")
        Logger.info("2. TELEGRAM_CHANNEL_ID", "📢")
        sys.exit(1)
    
    Logger.success("تنظیمات تأیید شد", "✅")
    
    # ==================== بارگذاری وضعیت ====================
    Logger.info("بارگذاری وضعیت فعلی...", "📊")
    
    last_line = StateManager.load_state()
    all_lines = StateManager.load_texts()
    
    Logger.info(f"وضعیت: خط {last_line} از {len(all_lines)}", "📍")
    
    # ==================== بررسی پایان کار ====================
    if last_line >= len(all_lines):
        Logger.success("🎉 تمام خطوط ارسال شده‌اند!", "🏁")
        Logger.info("برای شروع مجدد، فایل last_line.txt را به 0 تغییر دهید", "🔄")
        sys.exit(0)
    
    # ==================== انتخاب خطوط جدید ====================
    LINES_PER_POST = 3
    lines_to_process = []
    
    for i in range(LINES_PER_POST):
        line_num = last_line + i
        if line_num < len(all_lines):
            lines_to_process.append(all_lines[line_num])
    
    if not lines_to_process:
        Logger.error("هیچ خطی برای ارسال یافت نشد!", "📭")
        sys.exit(1)
    
    Logger.info(f"آماده ارسال {len(lines_to_process)} خط...", "📤")
    
    # ==================== پردازش لینک‌ها ====================
    Logger.info("در حال پردازش و اصلاح لینک‌ها...", "🔗")
    
    processed_links = []
    for i, original_link in enumerate(lines_to_process):
        modified_link = LinkProcessor.modify_link(original_link, last_line + i)
        processed_links.append(modified_link)
    
    # ==================== مدیریت زمان ====================
    Logger.info("مدیریت زمان و تاریخ...", "🕒")
    
    time_manager = TimeManager()
    iran_time = time_manager.get_iran_time()
    date_str, time_str = time_manager.get_shamsi_date(iran_time)
    
    Logger.info(f"زمان ایران: {time_str} | تاریخ: {date_str}", "📅")
    
    # ==================== ساخت پیام ====================
    Logger.info("ساخت پیام تلگرام...", "✍️")
    
    post_number = (last_line // LINES_PER_POST) + 1
    
    # انتخاب ایموجی
    main_emoji = Config.ANIMATED_EMOJIS[post_number % len(Config.ANIMATED_EMOJIS)]
    time_emoji = time_manager.get_time_emoji(iran_time.hour)
    
    # ساخت بخش‌های پیام
    post_builder = PostBuilder()
    
    header = post_builder.build_header(
        post_number, time_str, date_str, main_emoji, time_emoji
    )
    
    content = post_builder.build_content(processed_links)
    footer = post_builder.build_footer()
    
    message = post_builder.build_complete_message(header, content, footer)
    
    Logger.success("پیام ساخته شد", "📝")
    
    # ==================== ارسال به تلگرام ====================
    Logger.info("ارسال به کانال تلگرام...", "📨")
    
    bot = TelegramBot(TOKEN, CHANNEL)
    success, error = bot.send_message(message)
    
    if not success:
        Logger.error(f"ارسال ناموفق: {error}", "📛")
        sys.exit(1)
    
    # ==================== بروزرسانی وضعیت ====================
    Logger.info("بروزرسانی وضعیت...", "🔄")
    
    new_last_line = last_line + len(lines_to_process)
    StateManager.save_state(new_last_line)
    
    # ==================== گزارش نهایی ====================
    Logger.success("=" * 50, "🎯")
    Logger.success("✅ ربات با موفقیت اجرا شد", "🏁")
    Logger.success("=" * 50, "🎯")
    
    Logger.info(f"📊 گزارش اجرا:", "📈")
    Logger.info(f"   • پست شماره: #{post_number}", "#️⃣")
    Logger.info(f"   • خطوط ارسال شده: {len(lines_to_process)}", "📤")
    Logger.info(f"   • از خط: {last_line + 1} تا {new_last_line}", "📍")
    Logger.info(f"   • زمان: {time_str} | تاریخ: {date_str}", "🕒")
    Logger.info(f"   • ایموجی: {main_emoji} {time_emoji}", "🎨")
    
    # نمایش لینک‌های اصلاح شده برای تأیید
    Logger.info("📱 نمایش در V2Ray/Trojan:", "📲")
    for i, link in enumerate(processed_links, 1):
        if '#' in link:
            try:
                name_part = link.split('#', 1)[1]
                decoded_name = urllib.parse.unquote(name_part)
                Logger.info(f"   {i}. {decoded_name}", "🔗")
            except:
                Logger.info(f"   {i}. {link[:50]}...", "🔗")
    
    Logger.info("🤖 ربات آماده اجرای بعدی (۳۰ دقیقه دیگر)", "⏳")


# ==================== نقطه ورود ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Logger.warning("ربات توسط کاربر متوقف شد", "🛑")
        sys.exit(0)
    except Exception as e:
        Logger.error(f"خطای غیرمنتظره: {e}", "💥")
        sys.exit(1)
