
import 
import telebot
import google.generativeai as genai

# جلب المفاتيح
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# وظيفة للبحث عن أول موديل شغال في الحساب
def find_any_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # نختار الموديل ونرجعه
                return genai.GenerativeModel(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
    return None

# محاولة أولية لتجهيز الموديل
model = find_any_model()

@bot.message_handler(commands=["start"])
def start(message):
    welcome_text = (
        "👋 *أهلاً بك في بوت Toxoplasmosis Facts!*\n\n"
        "أنا مساعدك الذكي المتخصص في تقديم معلومات طبية شاملة حول *داء المقوسات (التوكسوبلازما)*. 🦠\n\n"
        "يمكنك سؤالي عن:\n"
        "• 🧬 طرق انتقال العدوى.\n"
        "• 🌡️ الأعراض والتشخيص.\n"
        "• 💊 طرق الوقاية والعلاج.\n\n"
        "📩 *اكتب سؤالك الآن وسأقوم بالرد عليك فوراً!*"
    )
    # أضفنا parse_mode="Markdown" لجعل الخط عريض ومنسق
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    global model
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, "typing")
    
    # إذا لم يجد موديل عند التشغيل، يحاول مرة أخرى الآن
    if model is None:
        model = find_any_model()
    
    if model is None:
        bot.reply_to(message, "❌ للأسف مش لاقي أي موديل شغال في الحساب. اتأكدي إن مفتاح الـ API صح.")
        return

    try:
        # التعليمات مدمجة في السؤال
        prompt = f"أنت مساعد طبي خبير في داء المقوسات. أجب باختصار وبالعربية: {message.text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        # لو حصل خطأ، نعرضه عشان نعرف سببه
        bot.reply_to(message, f"❌ حصلت مشكلة:\n{str(e)}")

if __name__ == "__main__":
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(none_stop=True)
