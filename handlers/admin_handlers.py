from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType

from disp import bot, dp, botdb, data_profile
import config
from custom_keyboard.admin_keyboard import admin_kb
import text


@dp.message_handler(Text("Orders"))
async def orders(message: types.Message):
    user_id = message.from_user.id
    if user_id in config.ADMIN_ID:
        active_orders = botdb.data_order(status="active")
        list_orders = ""
        for order in active_orders:
            user_id = order[-1]
            user = botdb.data_user(user_id)[0]
            list_orders += f"Номер заказа: {order[0]}\nИмя заказчика: {user[1]}\nАдрес: {user[2]}\nPrime: осталось {user[3]} заказов\nОписание заказа: {order[2]}\nДата оформления: {order[3]}\n\n"

        if list_orders == "":
            await message.answer("На данный момент активных заказов нет")
        else:
            await message.answer(f"Текущие активные заказы:\n\n{list_orders}")
