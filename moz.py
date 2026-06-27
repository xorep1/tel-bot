import logging
import random
import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
# 🛠️ اضافه شدن MessageHandler و filters به ایمپورت‌ها
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import jdatetime
from datetime import datetime, timezone, timedelta

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_BOT_TOKEN"

def extract_price_from_text(text):
    """استخراج هوشمند قیمت و تفکیک دقیق آن از درصد نوسان یا متون چسبیده"""
    comma_matches = re.findall(r'[0-9۰-۹]{1,3}(?:[,٬][0-9۰-۹]{3})+', text)
    if comma_matches:
        return comma_matches[0]
        
    decimal_matches = re.findall(r'[0-9۰-۹]+\.[0-9۰-۹]+|[0-9۰-۹]+٫[0-9۰-۹]+', text)
    if decimal_matches:
        return decimal_matches[0]
        
    fallback_matches = re.findall(r'[0-9۰-۹]{4,}', text)
    if fallback_matches:
        return fallback_matches[0]
        
    return "نامشخص"

def get_prices():
    url = "https://www.tgju.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    targets = {
        "سکه امامی": "نامشخص", "نیم سکه": "نامشخص", "ربع سکه": "نامشخص", "سکه گرمی": "نامشخص",
        "مثقال طلا": "نامشخص", "دلار": "نامشخص", "نفت برنت": "نامشخص", "نفت WTI": "نامشخص",
        "نفت اوپک": "نامشخص", "بیت کوین": "نامشخص", "اتریوم": "نامشخص", "دوج کوین": "نامشخص",
        "بایننس کوین": "نامشخص"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return targets

        soup = BeautifulSoup(response.text, 'html.parser')
        lines = [line.strip() for line in soup.get_text(separator='\n').split('\n') if line.strip()]
        
        for i, line in enumerate(lines):
            line_norm = line.replace('\u200c', ' ')
            for key in targets.keys():
                if targets[key] == "نامشخص" and key in line_norm:
                    line_without_key = line_norm.replace(key, "")
                    price = extract_price_from_text(line_without_key)
                    if price != "نامشخص":
                        targets[key] = price
                    else:
                        for j in range(i + 1, min(i + 4, len(lines))):
                            price = extract_price_from_text(lines[j])
                            if price != "نامشخص":
                                targets[key] = price
                                break
        return targets
    except Exception as e:
        logging.error(f"خطا در دریافت اطلاعات: {e}")
        return targets

async def gold_dollar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_prices()
    tehran_tz = timezone(timedelta(hours=3, minutes=30))
    now_gregorian = datetime.now(tehran_tz)
    current_date = jdatetime.datetime.fromgregorian(datetime=now_gregorian).strftime("%Y/%m/%d — %H:%M")
    
    text = (
        "📊 **گزارش لحظه‌ای بازار ارز، طلا و دیجیتال**\n"
        "🔹━━━━━━━━━━━━━━━━🔹\n\n"
        "💰 **مسکوکات و طلا:**\n"
        f"👑 سکه امامی: `{prices.get('سکه امامی', 'نامشخص')}` ریال\n"
        f"🔸 نیم سکه: `{prices.get('نیم سکه', 'نامشخص')}` ریال\n"
        f"🔸 ربع سکه: `{prices.get('ربع سکه', 'نامشخص')}` ریال\n\n"
        "💵 **ارزهای سنتی:**\n"
        f"🇺🇸 دلار بازار آزاد: `{prices.get('دلار', 'نامشخص')}` ریال\n\n"
        
        "🪙 **ارزهای دیجیتال (دلار):**\n"
        f"₿ بیت‌کوین: `{prices.get('بیت کوین', 'نامشخص')}` $\n\n"
        
        "🛢️ **انرژی (بشکه‌ای / دلار):**\n"
        f"🇪🇺 نفت برنت: `{prices.get('نفت برنت', 'نامشخص')}`\n"
        f"🇺🇸 نفت تگزاس (WTI): `{prices.get('نفت WTI', 'نامشخص')}`\n"
        f"🌐 نفت اوپک: `{prices.get('نفت اوپک', 'نامشخص')}`\n\n"
        "🔹━━━━━━━━━━━━━━━━🔹\n"
        f"📅 **زمان به‌روزرسانی:** {current_date}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# 📥 تابع برای پاسخ به پیام متنی
async def s_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # متنی که می‌خواهید ربات در پاسخ به s بفرستد
    replies_list = [
        "text 1",
        "text 2",
        "text 3",
        "text 4",
        "text 5",
    ]
    
    chosen_reply = random.choice(replies_list)
    
    await update.message.reply_text(chosen_reply, parse_mode="Markdown",reply_to_message_id=update.message.message_id)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("g", gold_dollar_command))
    
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'😂|🤣|😅|😆|😁'), s_text_message))
    
    print("🤖 ربات فعال شد و آماده پاسخگویی به پیام‌های متنی است...")
    app.run_polling()

if __name__ == "__main__":
    main()