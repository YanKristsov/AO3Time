import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from .states import Form
from .keyboards import format_kb, meta_kb
from . import config

router = Router()

def allowed(uid: int):
    if not config.ALLOWED_USERS:
        return True
    return uid in config.ALLOWED_USERS

@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    if not allowed(m.from_user.id):
        await m.answer('Доступ закрыт')
        return
    await state.clear()
    await m.answer('Привет! Пришли ссылки на AO3 (по одной на строку) или .txt файл со списком.')
    await state.set_state(Form.waiting_links)

@router.message(Form.waiting_links, F.text)
async def get_links_text(m: Message, state: FSMContext):
    links = []
    for line in m.text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if 'archiveofourown.org' in s or s.startswith('http'):
            links.append(s)
    # unique
    links = list(dict.fromkeys(links))
    if not links:
        await m.answer('Не нашёл ссылок AO3. Пришли ссылки или .txt файл.')
        return
    await state.update_data(links=links)
    await m.answer('Формат выдачи:', reply_markup=format_kb())
    await state.set_state(Form.waiting_format)

@router.message(Form.waiting_links, F.document)
async def get_links_file(m: Message, state: FSMContext):
    doc = m.document
    if not doc.file_name.lower().endswith('.txt'):
        await m.answer('Нужен .txt файл')
        return
    file = await m.bot.get_file(doc.file_id)
    data = await m.bot.download_file(file.file_path)
    text = data.read().decode('utf-8', errors='ignore')
    links = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        if 'archiveofourown.org' in s or s.startswith('http'):
            links.append(s)
    links = list(dict.fromkeys(links))
    if not links:
        await m.answer('Не нашёл ссылок AO3 в файле')
        return
    await state.update_data(links=links)
    await m.answer('Формат выдачи:', reply_markup=format_kb())
    await state.set_state(Form.waiting_format)

@router.callback_query(Form.waiting_format, F.data.startswith('fmt:'))
async def choose_format(c: CallbackQuery, state: FSMContext):
    fmt = c.data.split(':')[1]
    await state.update_data(fmt=fmt)
    await c.message.edit_text('Сформировать таблицу метаданных?')
    await c.message.edit_reply_markup(reply_markup=meta_kb())
    await state.set_state(Form.waiting_meta)

@router.callback_query(Form.waiting_meta, F.data.startswith('meta:'))
async def choose_meta(c: CallbackQuery, state: FSMContext):
    meta = c.data.split(':')[1]
    await state.update_data(meta=meta)
    data = await state.get_data()
    await c.message.edit_text(f'Обработка начата. Ссылок: {len(data.get("links",[]))}. Формат: {data.get("fmt")}. Метаданные: {meta}')
    await c.answer()
    # TODO: запуск обработки через core модули
    await state.clear()
