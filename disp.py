from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from db import BotDB
import text

# Инициализация бота
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация соединения с БД
botdb = BotDB("dash.db")

# Ценники
PRICE = types.LabeledPrice(
    label=text.prime, amount=299 * 100
)  # цена указывается в копейках: 299*100 = 299 рублей


# Проверка на подписку
def check_sub(check_mem):
    if check_mem["status"] == "left":
        return text.not_subscribed
    return True


# Данные пользователя для профиля
def data_profile(chat_id):
    count_orders = len(botdb.data_order(chat_id))
    user = botdb.data_user(chat_id)[0]
    name = user[1]
    adress = ""
    for i in range(2, 7):
        adress += user[i]
    if user[7] != 1:
        prime = "Не оплачено"
    else:
        prime = "Активирован"
    return f"Ваш профиль\n\nИмя: {name}\nАдрес: {adress}\nPrime-подписка: {prime}\nКол-во заказов: {count_orders}"
