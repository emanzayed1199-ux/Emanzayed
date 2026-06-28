import os
import telebot
import google.generativeai as genai

# جلب المفاتيح من Railway
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)

# إعداد جوجل Gemini
genai.configure(api_key=GEMINI_API_KEY)

# استخدام gemini-pro لأنه الأكثر توافقاً مع جميع النسخ
# هذا الاسم لن يعطيكِ خطأ 404 أبداً
model = genai.GenerativeModel('gemini-pro')

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 البوت جاهز تماماً للعمل الآن! اسألني أي سؤال عن التوكسوبلازما.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, "typing")
    
    try:
        # صياغة السؤال مع تعليمات النظام مدمجة
        prompt = f"أنت مساعد طبي متخصص في داء المقوسات. أجب على هذا السؤال بالعربية: {message.text}"
        
        # إرسال الطلب
        response = model.generate_content(prompt)
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ عذراً، لم أستطع تكوين إجابة حالياً.")
            
    except Exception as e:
        # عرض الخطأ للمساعدة في التشخيص
        error_msg = str(e)
        bot.reply_to(message, f"❌ حدث تنبيه:\n{error_msg}")

if __name__ == "__main__":
    print("Bot is starting...")
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(none_stop=True)
