import logging
from telegram.ext import Application
from app.bot.handlers import build_conversation
logging.basicConfig(level=logging.INFO)

def main():
    from app.config import TELEGRAM_TOKEN
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    build_conversation(app)
    app.run_polling()

if __name__=='__main__':
    main()
