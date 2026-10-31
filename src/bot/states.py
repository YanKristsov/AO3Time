from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    waiting_links = State()
    waiting_format = State()
    waiting_meta = State()
    processing = State()
