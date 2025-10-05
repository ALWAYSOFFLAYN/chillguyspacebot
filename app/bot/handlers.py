from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from .state import S
from .keyboards import two_buttons

# story engine
from ..story.engine import StoryState, render_node, advance

ABOUT_TEXT = (
    "Chillguy Space Bot — история с развилками и RAG.\n"
    "/start — спросить имя и начать историю\n"
    "/about — краткая справка"
)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Как тебя зовут?")
    return S.ASK_NAME

async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ABOUT_TEXT)

async def _send_node(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Рендер текущего узла, показать две кнопки
    state: StoryState = ctx.user_data["state"]
    text, labels, ending = render_node(state)
    ctx.user_data["labels"] = labels
    kb = two_buttons(labels["button_1"], labels["button_2"])
    await update.message.reply_text(text, reply_markup=kb)
    return ending is not None

async def capture_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = (update.message.text or "Гость").strip()
    ctx.user_data["state"] = StoryState(name=name, node_id="flare_alert")
    finished = await _send_node(update, ctx)
    if finished:
        return ConversationHandler.END
    return S.STORY

def _map_press_to_key(pressed: str, labels: dict) -> str | None:
    p = (pressed or "").strip().lower()
    if p == (labels["button_1"] or "").lower() or "1" in p:
        return "button_1"
    if p == (labels["button_2"] or "").lower() or "2" in p:
        return "button_2"
    return None

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # Восстановим состояние пользователя
    if "state" not in ctx.user_data:
        return await start(update, ctx)

    labels = ctx.user_data.get("labels", {"button_1":"button-1","button_2":"button-2"})
    key = _map_press_to_key(update.message.text, labels)
    if key is None:
        kb = two_buttons(labels["button_1"], labels["button_2"])
        await update.message.reply_text("Нажми одну из двух кнопок.", reply_markup=kb)
        return S.STORY

    # Переходим по ветке
    advance(ctx.user_data["state"], key)
    finished = await _send_node(update, ctx)
    if finished:
        # финальный узел — завершаем диалог
        return ConversationHandler.END
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
