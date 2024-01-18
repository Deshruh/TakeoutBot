from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from db import BotDB

# Инициализация бота
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация соединения с БД
botdb = BotDB("dash.db")

# Ценники
PRICE = types.LabeledPrice(
    label="Подписка на 1 месяц", amount=299 * 100
)  # цена указывается в копейках: 299*100 = 299 рублей


def check_sub(check_mem):
    # Проверка на подписку
    if check_mem["status"] == "left":
        return f"Ты не подписан на каннал. Подпишись на {config.CHANNEL_LINK}"
    return True
