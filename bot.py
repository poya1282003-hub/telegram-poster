#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ربات تلگرام - ارسال خودکار پروکسی‌ها
ورژن: 3.2.0 | نسخه پایدار و بهینه‌شده
"""

import os
import sys
import json
import base64
import requests
import urllib.parse
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List
import jdatetime

# ==================== تنظیمات ====================
class Config:
    """کلاس مدیریت تنظیمات"""
    
    # اطلاعات نسخه
    VERSION = "3.2.0"
    AUTHOR = "@v2reyonline"
    
    # فایل‌ها
    TEXTS_FILE = "texts.txt"
    STATE_FILE = "last_line.txt"
    LOG_FILE = "bot_debug.log"
    
    # تلگرام
    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
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
    
    # تنظیمات ایمنی
    MAX_MESSAGE_LENGTH = 4000
    LINES_PER_POST = 3
    
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
    
    # فعال/غیرفعال کردن لاگ دیباگ
    DEBUG_MODE = os.environ.get('TELEGRAM_DEBUG', 'false').lower() == 'true'
    
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
        """لاگ دیباگ (فقط در حالت دیباگ)"""
        if Logger.DEBUG_MODE:
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
            
            Logger.debug(f"پردازش لینک #{link_number + 1}", "🔗")
            
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
        else:
            new_link = f"{link}#{urllib.parse.quote(new_name)}"
        
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
    """مدیریت ارتباط با تلگرام - نسخه بهینه‌شده"""
    
    def __init__(self, token: str, channel_id: str):
        self.token = token
        self.channel_id = channel_id
        self.api_url = Config.TELEGRAM_API_URL.format(token=token)
    
    def send_message(self, text: str) -> Tuple[bool, Optional[str]]:
        """ارسال پیام به کانال تلگرام با قابلیت تکرار"""
        # بررسی طول پیام
        if len(text) > Config.MAX_MESSAGE_LENGTH:
            Logger.warning(f"پیام طولانی است ({len(text)} کاراکتر). کوتاه می‌کنم...", "📏")
            text = text[:Config.MAX_MESSAGE_LENGTH - 100] + "\n\n... (متن کوتاه شده)"
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                if attempt > 0:
                    Logger.info(f"تلاش مجدد {attempt + 1} از {Config.MAX_RETRIES}...", "🔄")
                    time.sleep(Config.RETRY_DELAY * attempt)
                
                payload = {
                    'chat_id': self.channel_id,
                    'text': text,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True,
                    'disable_notification': True,  # بدون اعلان
                }
                
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=Config.REQUEST_TIMEOUT
                )
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('ok'):
                    message_id = result['result']['message_id']
                    Logger.success(f"پیام با موفقیت ارسال شد (ID: {message_id})", "📤")
                    return True, None
                else:
                    error_msg = result.get('description', 'خطای ناشناخته تلگرام')
                    
                    # تشخیص خطای rate limit
                    if any(keyword in error_msg.lower() for keyword in ['too many', 'retry after', 'flood']):
                        wait_time = 10  # صبر بیشتر برای rate limit
                        Logger.warning(f"Rate limit تشخیص داده شد. صبر {wait_time} ثانیه...", "⏳")
                        time.sleep(wait_time)
                        continue
                    
                    Logger.error(f"خطای تلگرام: {error_msg}", "📛")
                    return False, error_msg
                    
            except requests.exceptions.Timeout:
                Logger.error(f"Timeout در ارتباط با تلگرام (تلاش {attempt + 1})", "⏰")
                if attempt < Config.MAX_RETRIES - 1:
                    continue
                return False, "Timeout"
                
            except requests.exceptions.ConnectionError as e:
                Logger.error(f"خطای اتصال به تلگرام: {e} (تلاش {attempt + 1})", "🔌")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY * 2)
                    continue
                return False, f"Connection Error: {e}"
                
            except requests.exceptions.RequestException as e:
                Logger.error(f"خطای درخواست: {e} (تلاش {attempt + 1})", "🚫")
                return False, str(e)
        
        return False, "تمام تلاش‌ها ناموفق بودند"


class StateManager:
    """مدیریت وضعیت و فایل‌ها"""
    
    @staticmethod
    def load_state() -> int:
        """بارگذاری وضعیت فعلی از فایل"""
        try:
            if not os.path.exists(Config.STATE_FILE):
                Logger.warning(f"فایل {Config.STATE_FILE} وجود ندارد. ایجاد می‌کنم...", "📝")
                StateManager.save_state(0)
                return 0
            
            with open(Config.STATE_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                if not content:
                    Logger.warning(f"فایل {Config.STATE_FILE} خالی است", "⚠️")
                    return 0
                
                if content.isdigit():
                    last_line = int(content)
                    Logger.info(f"وضعیت بارگذاری شد: خط {last_line}", "📖")
                    return last_line
                else:
                    Logger.warning(f"مقدار نامعتبر در {Config.STATE_FILE}: '{content}'. شروع از خط 0", "⚠️")
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
    def load_texts() -> List[str]:
        """بارگذاری متن‌ها از فایل"""
        try:
            if not os.path.exists(Config.TEXTS_FILE):
                Logger.error(f"فایل {Config.TEXTS_FILE} یافت نشد!", "🚫")
                sys.exit(1)
            
            with open(Config.TEXTS_FILE, 'r', encoding='utf-8') as f:
                lines = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:  # فقط خطوط غیرخالی
                        lines.append(line)
                        Logger.debug(f"خط {line_num}: {line[:50]}...", "📄")
            
            if not lines:
                Logger.error(f"فایل {Config.TEXTS_FILE} خالی است!", "📭")
                sys.exit(1)
            
            Logger.info(f"تعداد خطوط بارگذاری شده: {len(lines)}", "📊")
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
    def build_content(links: List[str]) -> str:
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
    
    Logger.info("=" * 50, "🚀")
    Logger.info(Config.get_bot_info(), "🤖")
    Logger.info("شروع ربات تلگرام", "⚡")
    Logger.info("=" * 50, "🚀")
    
    # ==================== بررسی تنظیمات ====================
    Logger.info("بررسی تنظیمات محیطی...", "🔧")
    
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    CHANNEL = os.environ.get("TELEGRAM_CHANNEL_ID")
    
    if not TOKEN:
        Logger.error("متغیر TELEGRAM_BOT_TOKEN تنظیم نشده است!", "🚫")
        Logger.info("لطفاً در GitHub Secrets تنظیم کنید:", "💡")
        Logger.info("1. به ریپوزیتوری بروید", "📁")
        Logger.info("2. Settings → Secrets and variables → Actions", "⚙️")
        Logger.info("3. New repository secret", "➕")
        Logger.info("4. نام: TELEGRAM_BOT_TOKEN", "🔑")
        Logger.info("5. مقدار: توکن ربات تلگرام", "🤖")
        sys.exit(1)
    
    if not CHANNEL:
        Logger.error("متغیر TELEGRAM_CHANNEL_ID تنظیم نشده است!", "🚫")
        Logger.info("لطفاً در GitHub Secrets تنظیم کنید:", "💡")
        Logger.info("1. Settings → Secrets and variables → Actions", "⚙️")
        Logger.info("2. New repository secret", "➕")
        Logger.info("3. نام: TELEGRAM_CHANNEL_ID", "📢")
        Logger.info("4. مقدار: آیدی کانال/گروه (مثال: -1001234567890)", "#️⃣")
        sys.exit(1)
    
    Logger.success("تنظیمات تأیید شد", "✅")
    Logger.debug(f"توکن: {TOKEN[:10]}...", "🔐")
    Logger.debug(f"کانال: {CHANNEL}", "📢")
    
    # ==================== بارگذاری وضعیت ====================
    Logger.info("بارگذاری وضعیت فعلی...", "📊")
    
    last_line = StateManager.load_state()
    all_lines = StateManager.load_texts()
    total_lines = len(all_lines)
    
    Logger.info(f"وضعیت فعلی: خط {last_line} از {total_lines}", "📍")
    
    # ==================== بررسی پایان کار ====================
    if last_line >= total_lines:
        Logger.success("🎉 تمام خطوط ارسال شده‌اند!", "🏁")
        Logger.info("برای شروع مجدد، مقدار فایل last_line.txt را به 0 تغییر دهید", "🔄")
        
        # ریست کردن به 0 اگر تمام شده
        StateManager.save_state(0)
        Logger.info("وضعیت به 0 ریست شد", "🔁")
        sys.exit(0)
    
    # ==================== انتخاب خطوط جدید ====================
    lines_to_process = []
    lines_count = min(Config.LINES_PER_POST, total_lines - last_line)
    
    for i in range(lines_count):
        line_num = last_line + i
        if line_num < total_lines:
            lines_to_process.append(all_lines[line_num])
    
    Logger.info(f"آماده ارسال {len(lines_to_process)} خط از خط {last_line + 1}", "📤")
    
    # ==================== پردازش لینک‌ها ====================
    Logger.info("در حال پردازش و اصلاح لینک‌ها...", "🔗")
    
    processed_links = []
    for i, original_link in enumerate(lines_to_process):
        modified_link = LinkProcessor.modify_link(original_link, last_line + i)
        processed_links.append(modified_link)
        Logger.debug(f"لینک {i + 1} پردازش شد: {modified_link[:80]}...", "✓")
    
    # ==================== مدیریت زمان ====================
    Logger.info("مدیریت زمان و تاریخ...", "🕒")
    
    time_manager = TimeManager()
    iran_time = time_manager.get_iran_time()
    date_str, time_str = time_manager.get_shamsi_date(iran_time)
    
    Logger.info(f"زمان ایران: {time_str} | تاریخ: {date_str}", "📅")
    
    # ==================== ساخت پیام ====================
    Logger.info("ساخت پیام تلگرام...", "✍️")
    
    post_number = (last_line // Config.LINES_PER_POST) + 1
    
    # انتخاب ایموجی
    main_emoji = Config.ANIMATED_EMOJIS[post_number % len(Config.ANIMATED_EMOJIS)]
    time_emoji = time_manager.get_time_emoji(iran_time.hour)
    
    # ساخت پیام
    header = PostBuilder.build_header(
        post_number, time_str, date_str, main_emoji, time_emoji
    )
    
    content = PostBuilder.build_content(processed_links)
    footer = PostBuilder.build_footer()
    
    message = PostBuilder.build_complete_message(header, content, footer)
    
    Logger.success("پیام با موفقیت ساخته شد", "📝")
    Logger.debug(f"طول پیام: {len(message)} کاراکتر", "📏")
    
    # ==================== ارسال به تلگرام ====================
    Logger.info("ارسال به کانال تلگرام...", "📨")
    
    bot = TelegramBot(TOKEN, CHANNEL)
    success, error = bot.send_message(message)
    
    if not success:
        Logger.error(f"ارسال ناموفق: {error}", "📛")
        Logger.info("ذخیره وضعیت فعلی برای تلاش بعدی...", "💾")
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
    Logger.info(f"   • وضعیت جدید: خط {new_last_line} از {total_lines}", "📊")
    Logger.info(f"   • زمان ارسال: {time_str} | تاریخ: {date_str}", "🕒")
    Logger.info(f"   • ایموجی‌های استفاده شده: {main_emoji} {time_emoji}", "🎨")
    
    # نمایش لینک‌های اصلاح شده برای تأیید
    Logger.info("📱 نام‌های نمایشی در V2Ray/Trojan:", "📲")
    for i, link in enumerate(processed_links, 1):
        if '#' in link:
            try:
                name_part = link.split('#', 1)[1]
                decoded_name = urllib.parse.unquote(name_part)
                Logger.info(f"   {i}. {decoded_name}", "🔗")
            except:
                Logger.info(f"   {i}. {link[:50]}...", "🔗")
    
    # محاسبه درصد پیشرفت
    progress = (new_last_line / total_lines) * 100
    Logger.info(f"📊 پیشرفت کلی: {progress:.1f}%", "📈")
    
    # زمان‌بندی بعدی
    next_run_minutes = 30
    Logger.info(f"⏳ ربات آماده اجرای بعدی ({next_run_minutes} دقیقه دیگر)", "🤖")


# ==================== نقطه ورود ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Logger.warning("ربات توسط کاربر متوقف شد", "🛑")
        sys.exit(0)
    except SystemExit as e:
        # خروجی کنترل شده
        exit(e.code)
    except Exception as e:
        Logger.error(f"خطای غیرمنتظره: {str(e)}", "💥")
        import traceback
        Logger.debug(traceback.format_exc(), "🐛")
        sys.exit(1)
