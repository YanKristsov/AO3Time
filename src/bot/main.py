import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import bot.config as config
from bot.keyboards import format_kb, meta_kb

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    waiting_links = State()
    waiting_format = State()
    waiting_meta = State()

def allowed(uid: int):
    if not config.ALLOWED_USERS:
        return True
    return uid in config.ALLOWED_USERS

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    if not allowed(m.from_user.id):
        await m.answer('Доступ закрыт')
        return
    await Form.waiting_links.set()
    await m.answer('Привет! Пришли ссылки на AO3 (по одной на строку) или .txt файл со списком.')

@dp.message_handler(state=Form.waiting_links, content_types=['text'])
async def get_links_text(m: types.Message, state: FSMContext):
    links = []
    for line in m.text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if 'archiveofourown.org' in s:
            links.append(s)
    links = list(dict.fromkeys(links))
    if not links:
        await m.answer('Не нашёл ссылок AO3. Пришли ссылки или .txt файл.')
        return
    await state.update_data(links=links)
    await Form.waiting_format.set()
    await m.answer('Формат выдачи:', reply_markup=format_kb())

@dp.message_handler(state=Form.waiting_links, content_types=['document'])
async def get_links_file(m: types.Message, state: FSMContext):
    doc = m.document
    if not doc.file_name.lower().endswith('.txt'):
        await m.answer('Нужен .txt файл')
        return
    file = await bot.get_file(doc.file_id)
    data = await bot.download_file(file.file_path)
    text = data.read().decode('utf-8', errors='ignore')
    links = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if 'archiveofourown.org' in s:
            links.append(s)
    links = list(dict.fromkeys(links))
    if not links:
        await m.answer('Не нашёл ссылок AO3 в файле')
        return
    await state.update_data(links=links)
    await Form.waiting_format.set()
    await m.answer('Формат выдачи:', reply_markup=format_kb())

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('fmt:'), state=Form.waiting_format)
async def choose_format(c: types.CallbackQuery, state: FSMContext):
    fmt = c.data.split(':')[1]
    await state.update_data(fmt=fmt)
    await Form.waiting_meta.set()
    await c.message.edit_text('Сформировать таблицу метаданных?')
    await c.message.edit_reply_markup(reply_markup=meta_kb())
    await c.answer()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('meta:'), state=Form.waiting_meta)
async def choose_meta(c: types.CallbackQuery, state: FSMContext):
    meta = c.data.split(':')[1]
    await state.update_data(meta=meta)
    data = await state.get_data()
    await c.message.edit_text(f'Готово. Ссылок: {len(data.get("links",[]))}. Формат: {data.get("fmt")}. Метаданные: {meta}\nОбработка временно отключена.')
    await c.answer()
    await state.finish()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
