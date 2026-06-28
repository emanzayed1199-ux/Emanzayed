import os
import telebot
import google.generativeai as genai

# جلب المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# قائمة بالموديلات المتاحة للتجربة التلقائية
MODELS_TO_TRY = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

def get_working_model():
    for model_name in MODELS_TO_TRY:
        try:
            m = genai.GenerativeModel(model_name)
            # تجربة بسيطة للتأكد أن الموديل شغال
            m.generate_content("test")
            return m
        except:
            continue
    return None

# محاولة تشغيل الموديل
model = get_working_model()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 البوت اشتغل تمام! اسألني أي سؤال الآن.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    global model
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, "typing")
    
    # إذا لم يعمل الموديل عند التشغيل، نحاول مرة أخرى
    if model is None:
        model = get_working_model()
        if model is None:
            bot.reply_to(message, "❌ جوجل لسه مش قادرة تتعرف على الموديل، اتأكدي من تحديث ملف requirements.txt")
            return

    try:
        # تعليمات النظام مدمجة في الرسالة
        prompt = f"أنت مساعد طبي متخصص في داء المقوسات. أجب باختصار وبالعربية: {message.text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(none_stop=True)
