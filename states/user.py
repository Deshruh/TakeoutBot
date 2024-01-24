from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    name = State()
    adress = State()
    successful = State()


class Description(StatesGroup):
    description = State()
    successful = State()


class Edit(StatesGroup):
    name = State()
    adress = State()
    successful = State()
