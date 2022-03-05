from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    Init = State()
    Phone = State()
    Code = State()
    Password = State()
    Done = State()
