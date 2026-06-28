import os
import telebot
import google.generativeai as genai
from google.api_core import exceptions

# جلب المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود المفتاح
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY is missing in Railway Variables!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# طريقة بديلة وأكثر أماناً للتعليمات (تعمل على كل الإصدارات)
SYSTEM_PROMPT = "أنت مساعد طبي متخصص في داء المقوسات. أجب باختصار وبالعربية."

model = genai.GenerativeModel("gemini-1.5-flash")

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 البوت يعمل! أرسل سؤالك الآن.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, "typing")
    
    try:
        # دمج التعليمات مع السؤال مباشرة لضمان العمل على الإصدارات القديمة
        full_query = f"{SYSTEM_PROMPT}\n\nالسؤال: {message.text}"
        response = model.generate_content(full_query)
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ جوجل استلمت الطلب لكن لم ترجع نصاً (ربما بسبب سياسات المحتوى).")
            
    except Exception as e:
        # هذا السطر سيخبرك بنوع الخطأ بدقة في التليجرام
        error_message = str(e)
        if "API_KEY_INVALID" in error_message:
            bot.reply_to(message, "❌ خطأ: مفتاح جوجل API غير صحيح. تأكدي منه في Variables.")
        elif "User location is not supported" in error_message:
            bot.reply_to(message, "❌ خطأ: منطقة سيرفر Railway هذه غير مدعومة من جوجل حالياً.")
        else:
            bot.reply_to(message, f"❌ حدث خطأ تقني:\n{error_message}")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(none_stop=True)
