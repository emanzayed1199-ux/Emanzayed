import os
import time
import telebot
import google.generativeai as genai
from collections import defaultdict

# المتغيرات تُقرأ من إعدادات Railway (أكثر أماناً)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a Toxoplasmosis Reference Center.
Only answer questions about toxoplasmosis.
If outside topic: reply in Arabic refusal.
Be concise, medical, bullet points.
"""

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# ---------------- MEMORY ----------------
chat_histories = defaultdict(list)
MAX_HISTORY = 10

def add_to_history(chat_id, role, text):
    chat_histories[chat_id].append({"role": role, "parts": [text]})
    chat_histories[chat_id] = chat_histories[chat_id][-MAX_HISTORY:]

# ---------------- RATE LIMIT ----------------
user_last_request = {}
COOLDOWN_SECONDS = 5

def is_rate_limited(user_id):
    now = time.time()
    last = user_last_request.get(user_id, 0)
    if now - last < COOLDOWN_SECONDS:
        return True
    user_last_request[user_id] = now
    return False

# ---------------- GEMINI ----------------
def get_ai_reply(chat_id, user_id, text):
    if is_rate_limited(user_id):
        return "⏳ استنى ثواني قبل ما تبعت سؤال جديد."
    try:
        chat = model.start_chat(history=chat_histories[chat_id])
        response = chat.send_message(text)
        return response.text
    except Exception as e:
       print("🔥 FULL ERROR:", e)
       return "حدث خطأ"
# ---------------- HANDLERS ----------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "مرحباً 👋\nأنا بوت متخصص في داء المقوسات فقط.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    bot.send_chat_action(chat_id, "typing")
    add_to_history(chat_id, "user", text)
    reply = get_ai_reply(chat_id, user_id, text)
    add_to_history(chat_id, "model", reply)
    bot.reply_to(message, reply)

# ---------------- RUN ----------------
bot.delete_webhook(drop_pending_updates=True)
bot.polling(none_stop=True)
