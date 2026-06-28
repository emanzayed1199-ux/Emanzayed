 import os
import time
import telebot
import google.generativeai as genai
from collections import defaultdict
from google.api_core import exceptions

# 1. جلب المفاتيح من إعدادات Railway
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. إعداد مكتبة تليجرام وجوجل
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# التعليمات البرمجية للبوت (System Prompt)
SYSTEM_PROMPT = """
You are a Toxoplasmosis Reference Center.
Only answer questions about toxoplasmosis.
If the question is outside this topic: reply in Arabic that you only specialize in Toxoplasmosis.
Be concise, medical, and use bullet points.
Answer in the language of the user (Arabic/English).
"""

# إعداد الموديل - استخدمنا اسم "models/gemini-1.5-flash" لضمان الوصول إليه
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# ---------------- ذاكرة المحادثة ----------------
chat_histories = defaultdict(list)
MAX_HISTORY = 6 # الاحتفاظ بآخر 6 رسائل لتقليل حجم البيانات

def add_to_history(chat_id, role, text):
    chat_histories[chat_id].append({"role": role, "parts": [text]})
    if len(chat_histories[chat_id]) > MAX_HISTORY:
        chat_histories[chat_id] = chat_histories[chat_id][-MAX_HISTORY:]

# ---------------- منع الرسائل المزعجة (Rate Limit) ----------------
user_last_request = {}
COOLDOWN_SECONDS = 4 

def is_rate_limited(user_id):
    now = time.time()
    last = user_last_request.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        return True
    user_last_request[user_id] = now
    return False

# ---------------- وظيفة الحصول على رد من Gemini ----------------
def get_ai_reply(chat_id, user_id, text):
    if is_rate_limited(user_id):
        return "⏳ فضلاً، انتظر قليلاً قبل إرسال سؤال آخر."
    
    try:
        # بدء الدردشة مع الذاكرة
        chat = model.start_chat(history=chat_histories[chat_id])
        response = chat.send_message(text)
        return response.text
    
    except exceptions.ResourceExhausted:
        return "⚠️ وصلت للحد الأقصى من الرسائل المجانية حالياً. جرب مرة أخرى بعد دقيقة."
    except exceptions.DeadlineExceeded:
        return "⚠️ استغرق الرد وقتاً طويلاً، حاول مرة أخرى."
    except Exception as e:
        print(f"Error Details: {e}") # سيظهر في سجلات Railway
        return "❌ عذراً، الموديل غير متاح حالياً. حاول بعد لحظات."

# ---------------- معالجة الرسائل ----------------
@bot.message_handler(commands=["start"])
def start(message):
    welcome_text = (
        "👋 أهلاً بك في مركز معلومات داء المقوسات (Toxoplasmosis).\n\n"
        "🦠 يمكنني مساعدتك في الإجابة على استفساراتك حول:\n"
        "• الأعراض، التشخيص، العلاج، وطرق الوقاية.\n\n"
        "اسأل سؤالك الآن."
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    # إظهار حالة "يكتب الآن"
    bot.send_chat_action(chat_id, "typing")
    
    # الحصول على الرد
    reply = get_ai_reply(chat_id, user_id, text)
    
    # حفظ المحادثة
    add_to_history(chat_id, "user", text)
    add_to_history(chat_id, "model", reply)
    
    # إرسال الرد للمستخدم
    bot.reply_to(message, reply)

# ---------------- تشغيل البوت ----------------
if __name__ == "__main__":
    print("Bot is running...")
    # حذف الـ Webhook القديم لضمان عمل Polling بشكل صحيح
    bot.delete_webhook(drop_pending_updates=True)
    bot.polling(none_stop=True)
