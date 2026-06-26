import os
import random
import telebot
import google.generativeai as genai
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8967201684:AAGCcixp9J-CklHFLxLUyaZufVRZm0Hw6Bc"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)

genai.configure(api_key= GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = (
    "You are the 'Toxoplasmosis Reference Center' (المركز المرجعي لداء المقوسات) — "
    "a professional clinical research consultancy system. "
    "Your interaction is strictly text-based. Do not suggest, generate, or reference any buttons, menus, or UI elements. "
    "STRICT SCOPE: You are only permitted to answer questions about Toxoplasmosis (داء المقوسات). "
    "This includes its causes, transmission, symptoms, diagnosis, prevention, and treatment. "
    "If the user asks about ANYTHING outside Toxoplasmosis, you MUST reply with exactly this text and nothing else: "
    "'عذراً، أنا متخصص فقط في الأبحاث والمراجع العلمية المتعلقة بداء المقوسات، ولا يمكنني الإجابة على أسئلة خارج هذا النطاق.' "
    "Your tone is formal, professional, and informative. "
    "You are a research consultancy system — not a doctor — and you never provide personal medical advice or prescriptions. "
    "You are fully fluent in Egyptian colloquial Arabic (العامية المصرية) and Modern Standard Arabic. "
    "Egyptian dialect you must understand: "
    "'علاج إيه' or 'فيه علاج' or 'بيتعالج إزاي' = what does research document about treatment. "
    "'عايز أعرف' = I want to know, 'بيعمل إيه' = what does it do, 'إزاي بتحصل العدوى' = how does infection occur. "
    "Ignore minor spelling mistakes and always infer the intended meaning. "
    "When asked about treatment (علاج) or medications (أدوية), begin your response with: "
    "'بصفتي نظاماً بحثياً استشارياً، فيما يلي ما توثقه الأبحاث العلمية المعتمدة حول هذا الموضوع:' "
    "then provide a thorough formal summary including Pyrimethamine, Sulfadiazine, Folinic acid, and Spiramycin for pregnant women. "
    "For all other Toxoplasmosis topics, begin with: 'وفقاً للمراجع العلمية المعتمدة:' "
    "RESPONSE FORMAT — always follow these rules: "
    "1. Be concise and straight to the point. Never write long wordy paragraphs. "
    "2. Use bullet points (•) to present key information clearly. "
    "3. Structure your answer: one short opening sentence, then bullet points, then a brief closing note if needed. "
    "4. Keep every bullet point short — one clear fact per bullet. "
    "5. Tone must always be professional and clinical. "
    "Always respond in Arabic."
)

QUIZ_QUESTIONS = [
    {
        "question": "داء المقوسات تسببه بكتيريا وليس طفيلياً.",
        "answer": False,
        "explanation": "❌ خطأ! داء المقوسات يسببه طفيلي يُسمى المقوسة الغوندية (Toxoplasma gondii)، وليس بكتيريا."
    },
    {
        "question": "القطط هي المضيف الرئيسي والنهائي لطفيلي داء المقوسات.",
        "answer": True,
        "explanation": "✅ صح! القطط هي المضيف النهائي الوحيد الذي يتكاثر فيه الطفيلي جنسياً ويُطرح في برازها."
    },
    {
        "question": "معظم الأشخاص الأصحاء المصابين بداء المقوسات تظهر عليهم أعراض شديدة.",
        "answer": False,
        "explanation": "❌ خطأ! معظم الأشخاص ذوي المناعة الجيدة لا تظهر عليهم أي أعراض أو تكون خفيفة جداً."
    },
    {
        "question": "يمكن أن تنتقل العدوى بداء المقوسات عن طريق تناول اللحوم غير المطهية جيداً.",
        "answer": True,
        "explanation": "✅ صح! اللحوم النيئة أو غير المطهية جيداً (خاصة لحم الخنزير والضأن) من أهم مصادر العدوى."
    },
    {
        "question": "داء المقوسات الخلقي يحدث عندما تنتقل العدوى من الأم إلى الجنين أثناء الحمل.",
        "answer": True,
        "explanation": "✅ صح! إذا أُصيبت الأم بالعدوى لأول مرة أثناء الحمل، قد تنتقل العدوى للجنين وتسبب مضاعفات خطيرة."
    },
    {
        "question": "لا يوجد علاج متاح لداء المقوسات.",
        "answer": False,
        "explanation": "❌ خطأ! يُعالج داء المقوسات بمضادات الطفيليات مثل البيريميثامين والسلفاديازين."
    },
    {
        "question": "غسل الخضروات والفواكه جيداً يساعد في الوقاية من داء المقوسات.",
        "answer": True,
        "explanation": "✅ صح! قد تكون التربة الملوثة على الخضروات مصدراً للعدوى، لذا الغسيل الجيد مهم جداً."
    },
    {
        "question": "يُعدّ داء المقوسات خطيراً بشكل خاص للأشخاص الذين يعانون من ضعف في المناعة.",
        "answer": True,
        "explanation": "✅ صح! لدى المرضى ذوي المناعة الضعيفة (كمرضى الإيدز) قد يؤدي المرض إلى التهاب دماغي مميت."
    },
    {
        "question": "يمكن تشخيص داء المقوسات عن طريق اختبار الدم للكشف عن الأجسام المضادة.",
        "answer": True,
        "explanation": "✅ صح! يُكشف عن العدوى بقياس الأجسام المضادة IgG وIgM في الدم."
    },
    {
        "question": "تنتقل العدوى بداء المقوسات عن طريق الهواء من شخص لآخر.",
        "answer": False,
        "explanation": "❌ خطأ! داء المقوسات لا ينتقل بالهواء. يكون الانتقال عبر الغذاء أو التربة الملوثة أو من الأم للجنين."
    },
]

MAX_HISTORY = 20

chat_histories = {}
quiz_scores = {}
quiz_seen = {}

def get_history(chat_id):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    return chat_histories[chat_id]

def clear_history(chat_id):
    chat_histories[chat_id] = []

def add_to_history(chat_id, role, text):
    history = get_history(chat_id)
    history.append({"role": role, "parts": [{"text": text}]})
    if len(history) > MAX_HISTORY:
        chat_histories[chat_id] = history[-MAX_HISTORY:]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    clear_history(message.chat.id)
    bot.send_message(
        message.chat.id,
        "مرحباً بك في المركز المرجعي لداء المقوسات 🔬\n"
        "*(Toxoplasmosis Reference Center)*\n\n"
        "بصفتي نظاماً بحثياً استشارياً، أنا هنا لأقدم لك ملخصات دقيقة وموثقة "
        "من الأبحاث والمراجع العلمية المعتمدة حول داء المقوسات.\n\n"
        "📂 *نطاق الاستشارة البحثية:*\n"
        "• أسباب المرض وآليات انتقال العدوى.\n"
        "• الأعراض السريرية وطرق التشخيص الموثقة.\n"
        "• بروتوكولات العلاج المذكورة في الدراسات العلمية.\n"
        "• إجراءات الوقاية الموصى بها في المراجع الطبية.\n\n"
        "💬 تفضل بطرح استفسارك وسيتم الرد بناءً على المراجع العلمية المعتمدة.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['sources'])
def send_sources(message):
    bot.send_message(
        message.chat.id,
        "📚 *المراجع الطبية الموثوقة لداء المقوسات:*\n\n"
        "🌍 *منظمة الصحة العالمية (WHO)*\n"
        "https://www.who.int/news-room/fact-sheets/detail/food-safety\n\n"
        "🇺🇸 *مراكز السيطرة على الأمراض والوقاية منها (CDC)*\n"
        "https://www.cdc.gov/parasites/toxoplasmosis\n\n"
        "🏥 *Mayo Clinic*\n"
        "https://www.mayoclinic.org/diseases-conditions/toxoplasmosis\n\n"
        "📖 *MedlinePlus — المكتبة الوطنية للطب (NIH)*\n"
        "https://medlineplus.gov/toxoplasmosis.html\n\n"
        "🔬 *Merck Manual — دليل مرك الطبي*\n"
        "https://www.merckmanuals.com/professional/infectious-diseases/sporozoan-infections/toxoplasmosis\n\n"
        "⚠️ تنبيه: هذه المراجع للأغراض التوعوية فقط ولا تُغني عن استشارة الطبيب المختص.",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.send_message(
        message.chat.id,
        "📚 *مكتبة داء المقوسات البحثية*\n"
        "_(Toxoplasmosis Research Library)_\n\n"
        "هذه المكتبة هي أرشيف رقمي متخصص يسترجع ويلخص نتائج الأبحاث العلمية والبيانات الموثقة "
        "من مراجع طبية موثوقة حول مرض داء المقوسات (Toxoplasmosis).\n\n"
        "🔍 *مصادر الأرشيف:*\n"
        "WHO · CDC · Mayo Clinic · NIH · Merck Manual · الأبحاث المحكّمة\n\n"
        "📌 *ما تفعله هذه المكتبة:*\n"
        "تسترجع ملخصات الأبحاث وتعرضها بصيغة مفهومة. هي ليست طبيباً ولا تقدم نصائح طبية شخصية.\n\n"
        "🧠 *التقنية المستخدمة:*\n"
        "مدعومة بنموذج Gemini من Google للذكاء الاصطناعي.\n\n"
        "💬 اكتب استفساراك وسأسترجع المعلومات من الأرشيف فوراً.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "💡 يمكنك سؤالي عن:\n"
        "• أسباب الإصابة وكيفية انتقال العدوى.\n"
        "• الأعراض الشائعة وطرق التشخيص.\n"
        "• إجراءات الوقاية الهامة.\n"
        "• خيارات العلاج المتاحة.\n\n"
        "⚙️ الأوامر المتاحة:\n"
        "• /start — بدء محادثة جديدة\n"
        "• /about — معلومات عن البوت\n"
        "• /toxo_info — معلومات عامة مع صورة\n"
        "• /quiz — اختبر معلوماتك 🧠\n"
        "• /sources — المراجع الطبية الموثوقة\n"
        "• /reset — مسح سجل المحادثة\n"
        "• /help — عرض هذه القائمة\n\n"
        "💬 تفضل بكتابة سؤالك وسأرد عليك فوراً."
    )

@bot.message_handler(commands=['reset'])
def reset_chat(message):
    clear_history(message.chat.id)
    bot.send_message(
        message.chat.id,
        "✅ تم مسح سجل المحادثة. يمكنك البدء من جديد!"
    )

@bot.message_handler(commands=['quiz'])
def send_quiz(message):
    user_id = message.from_user.id
    total = len(QUIZ_QUESTIONS)

    if user_id not in quiz_seen:
        quiz_seen[user_id] = set()

    if len(quiz_seen[user_id]) >= total:
        quiz_seen[user_id] = set()
        bot.send_message(
            message.chat.id,
            "🎊 أحسنت! لقد أجبت على جميع الأسئلة.\nيبدأ الاختبار من جديد بنفس الأسئلة. أرسل /score لترى نتيجتك الكاملة."
        )

    remaining = [i for i in range(total) if i not in quiz_seen[user_id]]
    q_index = random.choice(remaining)
    q = QUIZ_QUESTIONS[q_index]

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ صح", callback_data=f"quiz_true|{q_index}"),
        InlineKeyboardButton("❌ خطأ", callback_data=f"quiz_false|{q_index}")
    )
    answered = len(quiz_seen[user_id])
    bot.send_message(
        message.chat.id,
        f"🧠 *سؤال اختباري* ({answered + 1}/{total}):\n\n{q['question']}",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz_"))
def handle_quiz_answer(call):
    parts = call.data.split("|")
    user_answer = parts[0] == "quiz_true"
    q_index = int(parts[1])
    q = QUIZ_QUESTIONS[q_index]
    is_correct = user_answer == q["answer"]

    user_id = call.from_user.id
    if user_id not in quiz_scores:
        quiz_scores[user_id] = {"correct": 0, "total": 0}
    if user_id not in quiz_seen:
        quiz_seen[user_id] = set()

    if q_index not in quiz_seen[user_id]:
        quiz_seen[user_id].add(q_index)
        quiz_scores[user_id]["total"] += 1
        if is_correct:
            quiz_scores[user_id]["correct"] += 1

    result = "🎉 إجابة صحيحة!" if is_correct else "💡 إجابة خاطئة!"
    s = quiz_scores[user_id]
    bot.edit_message_text(
        f"🧠 *سؤال اختباري:*\n\n{q['question']}\n\n{result}\n{q['explanation']}\n\n"
        f"📊 نتيجتك: {s['correct']}/{s['total']}\n\nأرسل /quiz لسؤال جديد!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['score'])
def send_score(message):
    user_id = message.from_user.id
    s = quiz_scores.get(user_id)
    if not s or s["total"] == 0:
        bot.send_message(
            message.chat.id,
            "📊 لم تجب على أي سؤال بعد!\nأرسل /quiz لتبدأ الاختبار."
        )
        return
    percentage = round((s["correct"] / s["total"]) * 100)
    if percentage == 100:
        grade = "🏆 ممتاز! أنت خبير حقيقي في داء المقوسات!"
    elif percentage >= 70:
        grade = "👍 جيد جداً! معلوماتك قوية."
    elif percentage >= 50:
        grade = "📚 جيد! يمكنك التحسن بالمزيد من الأسئلة."
    else:
        grade = "💪 استمر في التعلم! أرسل /quiz لتتحسن أكثر."
    bot.send_message(
        message.chat.id,
        f"📊 *نتيجتك في الاختبار:*\n\n"
        f"✅ إجابات صحيحة: {s['correct']}\n"
        f"❌ إجابات خاطئة: {s['total'] - s['correct']}\n"
        f"📝 إجمالي الأسئلة: {s['total']}\n"
        f"🎯 النسبة: {percentage}%\n\n"
        f"{grade}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['toxo_info'])
def send_toxo_info(message):
    send_toxo(message.chat.id)

def send_toxo(chat_id):
    caption = 'داء المقوسات هو مرض طفيلي تسببه المقوسة الغوندية، وهي من الأبيكومبلكسا. ترتبط العدوى بداء المقوسات بمجموعة متنوعة من الحالات العصبية والنفسية والسلوكية. في بعض الأحيان، قد يعاني الأشخاص لبضعة أسابيع أو أشهر من مرض خفيف يشبه الإنفلونزا، مثل آلام العضلات وتضخم الغدد الليمفاوية. قد تظهر مشاكل في العين لدى عدد قليل من الأشخاص. أما لدى الأشخاص الذين يعانون من ضعف في جهاز المناعة، فقد تظهر أعراض حادة مثل النوبات وضعف التنسيق. إذا أصيبت المرأة بالعدوى أثناء الحمل، فقد تؤثر حالة تُعرف باسم داء المقوسات الخلقي على الطفل'
    with open('hq720.jpg', 'rb') as photo:
        bot.send_photo(chat_id, photo, caption=caption)

STATIC_FALLBACK = (
    "أنا مكتبة بحثية ولا أقدم نصائح طبية. يُرجى استشارة الطبيب المختص للحصول على مشورة طبية.\n\n"
    "فيما يلي ملخص من الأبحاث العلمية حول هذا الموضوع:\n\n"
    "وفقاً للأبحاث المنشورة في قواعد بيانات WHO وCDC وMayo Clinic:\n"
    "• يُوثّق الباحثون استخدام Pyrimethamine وSulfadiazine مع Folinic acid "
    "كبروتوكول علاجي رئيسي لداء المقوسات لدى البالغين.\n"
    "• تُشير الأبحاث إلى استخدام Spiramycin للحوامل في الثلث الأول من الحمل للحد من انتقال العدوى للجنين.\n"
    "• تُحدد الدراسات مدة العلاج عادةً بين 4 و6 أسابيع تبعاً لشدة الحالة وحالة المناعة.\n"
    "• تُفيد الأبحاث بأن الأشخاص ذوي المناعة الجيدة دون أعراض لا يحتاجون في الغالب إلى علاج."
)

def get_ai_reply(chat_id, user_text):
    educational_prefix = (
        "[General knowledge question about Toxoplasmosis for educational purposes]: "
    )
    history = get_history(chat_id)
    if history and history[-1]["role"] == "user":
       history[-1]["parts"][0]["text"] = educational_prefix + user_text
 
    response = model.generate_content(history)
    if not response.candidates:
        return None

    candidate = response.candidates[0]
    finish_reason = str(getattr(candidate, "finish_reason", "")).upper()
    if finish_reason in ("SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT"):
        return None

    text = getattr(response, "text", None)
    if not text:
        parts = candidate.content.parts if candidate.content else []
        text = "".join(p.text for p in parts if hasattr(p, "text")) or None

    return text

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    try:
        add_to_history(chat_id, "user", message.text)
        reply = get_ai_reply(chat_id, message.text)

        if reply is None:
            add_to_history(chat_id, "model", STATIC_FALLBACK)
            bot.reply_to(message, STATIC_FALLBACK)
        else:
            add_to_history(chat_id, "model", reply)
            bot.reply_to(message, reply)

    except Exception as e:
        chat_histories.pop(chat_id, None)
        bot.reply_to(message, "عذراً، حدث خطأ في الاتصال. حاول مرة أخرى.")

bot.delete_webhook(drop_pending_updates=True)

bot.set_my_commands([
    telebot.types.BotCommand("start", "بدء محادثة جديدة"),
    telebot.types.BotCommand("about", "معلومات عن البوت وهدفه"),
    telebot.types.BotCommand("help", "عرض قائمة المساعدة والأوامر"),
    telebot.types.BotCommand("toxo_info", "معلومات عامة عن داء المقوسات مع صورة"),
    telebot.types.BotCommand("quiz", "اختبر معلوماتك عن داء المقوسات"),
    telebot.types.BotCommand("score", "اعرض نتيجتك في الاختبار"),
    telebot.types.BotCommand("sources", "المراجع الطبية الموثوقة"),
    telebot.types.BotCommand("reset", "مسح سجل المحادثة والبدء من جديد"),
])

bot.polling()
