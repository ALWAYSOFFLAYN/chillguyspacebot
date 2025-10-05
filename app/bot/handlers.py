from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from .state import S
from .keyboards import two_buttons

ABOUT_TEXT = (
    "Chillguy Space Bot — минимальный прототип с кнопками.\\n"
    "/start — спросить имя, показать две кнопки\\n"
    "/about — краткая справка"
)

BUTTON_1 = "button-1"
BUTTON_2 = "button-2"

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Как тебя зовут?")
    return S.ASK_NAME

async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ABOUT_TEXT)

async def capture_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = (update.message.text or "Гость").strip()
    ctx.user_data["name"] = name
    kb = two_buttons(BUTTON_1, BUTTON_2)
    await update.message.reply_text(
        f"Приятно познакомиться, {name}! Нажми одну из кнопок ниже:",
        reply_markup=kb
    )
    return S.STORY

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    choice = (update.message.text or "").strip().lower()
    if BUTTON_1 in choice:
        msg = "Ты нажал(а) button-1. (Пока просто проверка UI)"
    elif BUTTON_2 in choice:
        msg = "Ты нажал(а) button-2. (Пока просто проверка UI)"
    else:
        msg = "Пожалуйста, нажми одну из кнопок: button-1 или button-2."

    kb = two_buttons(BUTTON_1, BUTTON_2)
    await update.message.reply_text(msg, reply_markup=kb)
    return S.STORY

def build_conversation(application):
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            S.ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_name)],
            S.STORY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, on_button)],
        },
        fallbacks=[CommandHandler("about", about)],
        allow_reentry=True,
    )
    application.add_handler(conv)
    application.add_handler(CommandHandler("about", about))
