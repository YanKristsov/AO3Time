import os, sys, re, tempfile, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import bot.config as config
from bot.keyboards import format_kb, meta_kb
from core.ao3_parser import AO3Parser
from core.pdf_gen import PDFGenerator
from core.zip_utils import ZipUtils
from core.metadata import MetadataCollector
from core.fichub_api import FichubAPI
import csv

if __name__ == '__main__':
    from aiogram import executor
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    fichub = FichubAPI()

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

    @dp.message_handler(state='*', commands=['start'])
    async def start_any(m: types.Message, state: FSMContext):
        if not allowed(m.from_user.id):
            await m.answer('Доступ закрыт')
            return
        await state.finish()
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
            await m.answer('Не нашёл ссылок AO3.')
            return
        await state.update_data(links=links)
        await Form.waiting_format.set()
        await m.answer('Выбери формат:', reply_markup=format_kb())

    @dp.message_handler(state=Form.waiting_links, content_types=['document'])
    async def get_links_file(m: types.Message, state: FSMContext):
        doc = m.document
        if not doc.file_name.lower().endswith('.txt'):
            await m.answer('Нужен .txt файл')
            return
        try:
            file = await bot.get_file(doc.file_id)
            data = await bot.download_file(file.file_path)
            text = data.read().decode('utf-8', errors='ignore')
        except Exception:
            await m.answer('Ошибка при чтении файла')
            return
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
        await m.answer('Выбери формат:', reply_markup=format_kb())

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
        meta_flag = c.data.split(':')[1]
        data = await state.get_data()
        links = data.get('links', [])
        fmt = data.get('fmt')
        chat_id = c.from_user.id
        try:
            await c.answer()
            await bot.send_message(chat_id, f'Обработка {len(links)} ссылок...')
            parser = AO3Parser()
            pdfgen = PDFGenerator()
            zipper = ZipUtils()
            mcol = MetadataCollector()
            out_dir = tempfile.mkdtemp()
            epub_files = []
            pdf_files = []
            meta_rows = []
            for url in links:
                try:
                    if fmt == 'epub':
                        res = fichub.get_epub(url)
                        if res:
                            content, title = res
                            safe = re.sub(r'[^\w\- ]+', '', title or 'work')[:40] or 'work'
                            epub_path = os.path.join(out_dir, f'{safe}.epub')
                            with open(epub_path, 'wb') as f:
                                f.write(content)
                            epub_files.append(epub_path)
                            if meta_flag == 'yes':
                                try:
                                    meta_rows.append(mcol.collect(url))
                                except:
                                    pass
                            continue
                    info = parser.fetch(url)
                    title = info.get('title', 'untitled')
                    safe = re.sub(r'[^\w\- ]+', '', title)[:40] or 'work'
                    pdf_path = os.path.join(out_dir, f'{safe}.pdf')
                    pdfgen.generate(title, pdf_path)
                    if fmt == 'zip':
                        pdf_files.append(pdf_path)
                    else:
                        with open(pdf_path, 'rb') as f:
                            await bot.send_document(chat_id, types.InputFile(f, filename=os.path.basename(pdf_path)))
                    if meta_flag == 'yes':
                        try:
                            meta_rows.append(mcol.collect(url))
                        except:
                            pass
                except Exception:
                    continue
            for p in epub_files:
                with open(p, 'rb') as f:
                    await bot.send_document(chat_id, types.InputFile(f, filename=os.path.basename(p)))
            if fmt == 'zip' and pdf_files:
                zip_path = os.path.join(out_dir, 'ao3time.zip')
                zipper.pack(pdf_files, zip_path)
                with open(zip_path, 'rb') as f:
                    await bot.send_document(chat_id, types.InputFile(f, filename='ao3time.zip'))
            if meta_flag == 'yes' and meta_rows:
                csv_path = os.path.join(out_dir, 'metadata.csv')
                with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                    w = csv.DictWriter(f, fieldnames=['Название','Fandoms','Rating','Category','Relationships','Characters','Additional Tags','Words'])
                    w.writeheader()
                    for r in meta_rows:
                        rr = dict(r)
                        rr['Fandoms'] = '; '.join(rr.get('Fandoms') or [])
                        rr['Category'] = '; '.join(rr.get('Category') or [])
                        rr['Relationships'] = '; '.join(rr.get('Relationships') or [])
                        rr['Characters'] = '; '.join(rr.get('Characters') or [])
                        rr['Additional Tags'] = '; '.join(rr.get('Additional Tags') or [])
                        w.writerow(rr)
                with open(csv_path, 'rb') as f:
                    await bot.send_document(chat_id, types.InputFile(f, filename='metadata.csv'), caption='Таблица метаданных')
            await bot.send_message(chat_id, 'Готово. Можешь прислать новые ссылки.')
        except Exception as e:
            await bot.send_message(chat_id, f'Ошибка: {e}')
        finally:
            await state.finish()

    executor.start_polling(dp, skip_updates=True)
