 import os
import time
import telebot
import google.generativeai as genai
from collections import defaultdict

TOKEN = os.environ.get(8967201684:AAGCcixp9J-CklHFLxLUyaZufVRZm0Hw6Bc)
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

# ---------------- CACHE ----------------
response_cache = {}

def get_cache_key(text):
    return text.strip().lower()

# ---------------- GEMINI ----------------
def get_ai_reply(chat_id, user_id, text):

    # rate limit
    if is_rate_limited(user_id):
        return "⏳ استنى ثواني قبل ما تبعت سؤال جديد."

    # cache check
    key = get_cache_key(text)
    if key in response_cache:
        return response_cache[key]

    try:
        chat = model.start_chat(history=chat_histories[chat_id])
        response = chat.send_message(text)
        reply = response.text

        # save cache
        response_cache[key] = reply

        return reply

    except Exception as e:
        print("Gemini error:", e)
        return "⚠️ حصل خطأ مؤقت في النظام، حاول تاني بعد قليل."

 
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

 
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "مرحباً 👋\nأنا بوت متخصص في داء المقوسات فقط."
    )

# ---------------- RUN ----------------
bot.delete_webhook(drop_pending_updates=True)
bot.polling(none_stop=True)
