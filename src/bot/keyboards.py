from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='/start')]],
        resize_keyboard=True
    )

def format_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='PDF по отдельности', callback_data='fmt:single')],
        [InlineKeyboardButton(text='ZIP со всеми PDF', callback_data='fmt:zip')],
    ])
    return kb

def meta_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='meta:yes')],
        [InlineKeyboardButton(text='Нет', callback_data='meta:no')],
    ])
    return kb
