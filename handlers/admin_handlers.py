from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType

from disp import bot, dp, botdb, data_profile
import config
from custom_keyboard.admin_keyboard import admin_kb, nav_order, data_orders
import text


@dp.message_handler(Text("Orders"))
async def orders(message: types.Message):
    user_id = message.from_user.id
    if user_id in config.ADMIN_ID:
        active_orders = botdb.data_order(status="active")
        list_orders, orders_id = data_orders(active_orders)

        if list_orders == "":
            await message.answer("На данный момент активных заказов нет")
        else:
            await message.answer(
                f"Текущие активные заказы:\n\n{list_orders}",
                reply_markup=nav_order(orders_id),
            )


@dp.message_handler(Text("Taken orders"))
async def taken_order(message: types.Message):
    orders = botdb.data_order(status="continued")
    if orders == []:
        await message.answer("Нет принятых заказов")
    else:
        list_orders, orders_id = data_orders(orders)
        await message.answer(
            f"Текущие принятые заказы:\n\n{list_orders}",
            reply_markup=nav_order(orders_id),
        )
