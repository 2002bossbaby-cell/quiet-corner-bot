import json
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_USERS = [6438940085, 1102261684]

DATA_FILE = "journal.json"
REMINDER_FILE = "reminders.json"

MOOD_FILE = "moods.json"

mood_options = [
    "😊 Happy",
    "😔 Sad",
    "😌 Calm",
    "😤 Stressed",
    "🥺 Missing you",
    "😴 Tired",
    "❤️ Loved"
]
love_messages = [
    "even across miles, you are close to my heart 🤍",
    "one day closer to us",
    "you are my calm place",
    "soft love, steady love",
    "you are deeply cherished",
    "i’m always on your side"
]
water_quotes = [
    "Drink water like you're watering a life you love 💧",
    "Hydration is self-respect.",
    "Your body is listening — give it water 🤍",
    "Small sips, strong soul.",
    "Care for yourself the way you care for others.",
    "Water first, everything else later.",
    "A hydrated heart feels lighter.",
    "Drink water. Stay soft. Stay strong."
]

# ---------------- Utilities ----------------
def load_json(file, default):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_allowed(update: Update):
    return update.effective_user.id in ALLOWED_USERS

async def blocked(update: Update):
    await update.message.reply_text("This space is private 🤍")

# ---------------- Journal ----------------
def load_entries():
    return load_json(DATA_FILE, [])

def save_entries(data):
    save_json(DATA_FILE, data)

# ---------------- Commands ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    await update.message.reply_text(
        "🤍 Welcome to Our Quiet Corner\n\n"
        "/write – write a journal entry\n"
        "/read – read recent entries\n"
        "/random – gentle love message\n"
        "/remindon – daily reminder on\n"
        "/remindoff – daily reminder off\n"
    )

async def write(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    context.user_data["writing"] = True
    await update.message.reply_text("Write your heart out 🤍")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    text = update.message.text

    # -------- MOOD HANDLING --------
    if context.user_data.get("choosing_mood"):
        mood_text = text

        if mood_text not in mood_options:
            await update.message.reply_text("Please choose a mood using the buttons 🤍")
            return

        entry = {
            "name": update.effective_user.first_name,
            "mood": mood_text,
            "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }

        moods = load_json(MOOD_FILE, [])
        moods.insert(0, entry)
        save_json(MOOD_FILE, moods)

        context.user_data["choosing_mood"] = False
        await update.message.reply_text("Noted gently 🤍")
        return

    # -------- JOURNAL HANDLING --------
    if context.user_data.get("writing"):
        entry = {
            "name": update.effective_user.first_name,
            "text": text,
            "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }

        data = load_entries()
        data.insert(0, entry)
        save_entries(data)

        context.user_data["writing"] = False
        await update.message.reply_text("Saved gently 🤍")
        return

    # -------- PRIVATE COUPLE CHAT --------
    sender_id = update.effective_user.id
    sender_name = update.effective_user.first_name

    for uid in ALLOWED_USERS:
        if uid != sender_id:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🤍 {sender_name}: {text}"
                )
            except:
                pass

    await update.message.reply_text("Delivered 🤍")

async def read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    data = load_entries()

    if not data:
        await update.message.reply_text("No entries yet 🤍")
        return

    msg = "📖 Your shared journal:\n\n"
    for entry in data[:5]:
        msg += f"🤍 {entry['name']} ({entry['time']}):\n{entry['text']}\n\n"

    await update.message.reply_text(msg)

async def random_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    await update.message.reply_text(random.choice(love_messages))

async def send_water_reminder(context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(water_quotes)

    for uid in ALLOWED_USERS:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"💧 Time to drink water!\n\n“{quote}”"
            )
        except:
            pass

# ---------------- Reminder Commands ----------------
async def remind_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    uid = update.effective_user.id
    users = load_json(REMINDER_FILE, [])

    if uid not in users:
        users.append(uid)
        save_json(REMINDER_FILE, users)

    await update.message.reply_text("Daily reminders turned on 🤍")

async def remind_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    uid = update.effective_user.id
    users = load_json(REMINDER_FILE, [])

    if uid in users:
        users.remove(uid)
        save_json(REMINDER_FILE, users)

    await update.message.reply_text("Reminders turned off 🤍")

# ---------------- Scheduled Reminder ----------------
async def send_daily_reminders(context: ContextTypes.DEFAULT_TYPE):
    users = load_json(REMINDER_FILE, [])

    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text="🌙 Gentle reminder: want to write something today?"
            )
        except:
            pass

from telegram import ReplyKeyboardMarkup

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    keyboard = [[m] for m in mood_options]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    context.user_data["choosing_mood"] = True
    await update.message.reply_text(
        "How are you feeling right now? 🤍",
        reply_markup=reply_markup
    )

async def moodlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await blocked(update)
        return

    moods = load_json(MOOD_FILE, [])

    if not moods:
        await update.message.reply_text("No moods shared yet 🤍")
        return

    msg = "🌿 Recent moods:\n\n"
    for entry in moods[:10]:
        msg += f"🤍 {entry['name']} – {entry['mood']} ({entry['time']})\n"

    await update.message.reply_text(msg)

# ---------------- Main ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("write", write))
    app.add_handler(CommandHandler("read", read))
    app.add_handler(CommandHandler("random", random_msg))
    app.add_handler(CommandHandler("remindon", remind_on))
    app.add_handler(CommandHandler("remindoff", remind_off))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("moodlog", moodlog))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Daily reminder at 9 PM
    app.job_queue.run_daily(send_daily_reminders, time(hour=21, minute=0))

    # Water reminder every 2 hours
    app.job_queue.run_repeating(send_water_reminder, interval=7200, first=10)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
