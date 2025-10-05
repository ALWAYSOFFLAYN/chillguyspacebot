from telegram import ReplyKeyboardMarkup

def two_buttons(label1: str, label2: str):
    return ReplyKeyboardMarkup([[label1, label2]], resize_keyboard=True, one_time_keyboard=False)
