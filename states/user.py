from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    name = State()
    adress = State()


class Description(StatesGroup):
    description = State()
    successful = State()
