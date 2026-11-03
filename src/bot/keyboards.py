from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='/start')]],
        resize_keyboard=True
    )

def format_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='EPUB', callback_data='fmt:epub')],
        [InlineKeyboardButton(text='PDF', callback_data='fmt:pdf')],
        [InlineKeyboardButton(text='ZIP из PDF', callback_data='fmt:zip')],
    ])
    return kb

def meta_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='meta:yes')],
        [InlineKeyboardButton(text='Нет', callback_data='meta:no')],
    ])
    return kb
