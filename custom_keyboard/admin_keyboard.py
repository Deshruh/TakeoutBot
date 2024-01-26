from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from disp import bot, botdb, dp, data_profile
import text

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)  # type: ignore
buttons = ["Orders", "History"]
admin_kb.add(types.KeyboardButton("Profile"))  # type: ignore
admin_kb.add(*buttons)


def nav_order(orders_id):
    nav = InlineKeyboardMarkup(row_width=7)
    i = 1
    buttons = []
    buttons.append(InlineKeyboardButton(text="Назад", callback_data=f"left_{orders_id[0]}"))  # type: ignore
    for id in orders_id:
        buttons.append(InlineKeyboardButton(text=i, callback_data=f"order_{id}"))  # type: ignore
        i += 1
    buttons.append(InlineKeyboardButton(text="Вперед", callback_data=f"right_{orders_id[-1]}"))  # type: ignore

    nav.add(*buttons)
    return nav


def order_keyboard(order_id):
    order_kb = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton("Назад", callback_data=f"back_{order_id}"),  # type: ignore
        InlineKeyboardButton("Принять", callback_data=f"access_{order_id}"),  # type: ignore
    ]
    order_kb.add(*buttons)
    return order_kb


def data_orders(active_orders, start=0):
    list_orders = ""
    orders_id = []
    end = start + 5
    for order in active_orders[start:end]:
        orders_id.append(order[0])
        user_id = order[-1]
        user = botdb.data_user(user_id)[0]
        list_orders += f"Имя заказчика: {user[1]}\nАдрес: {user[2]}\nДата оформления: {order[3]}\n\n"

    return list_orders, orders_id


@dp.callback_query_handler(Text(startswith="order_"))
async def callback_orders(call: types.CallbackQuery):
    order_id = call.data.split("_")[1]
    orders = botdb.data_order()
    for order in orders:
        if order[0] == int(order_id):
            user_id = order[-1]
            user = botdb.data_user(user_id)[0]
            await call.message.answer(
                f"Номер заказа: {order[0]}\nИмя заказчика: {user[1]}\nАдрес: {user[2]}\nPrime: осталось {user[3]} заказов\nОписание заказа: {order[2]}\nДата оформления: {order[3]}\n\n",
                reply_markup=order_keyboard(order[0]),
            )
    await call.answer()


@dp.callback_query_handler(Text(startswith="left_"))
async def left_orders(call: types.CallbackQuery):
    start = int(call.data.split("_")[1]) - 5
    if start < 1:
        await call.answer("Вы и так в самом начале списка")
        return

    active_orders = botdb.data_order(status="active")
    list_orders, orders_id = data_orders(active_orders, start)
    await call.message.answer(
        f"Текущие активные заказы:\n\n{list_orders}",
        reply_markup=nav_order(orders_id),
    )
    await call.answer()


@dp.callback_query_handler(Text(startswith="right_"))
async def right_orders(call: types.CallbackQuery):
    start = int(call.data.split("_")[1]) + 1
    active_orders = botdb.data_order(status="active")
    if start > active_orders[-1][0]:
        await call.answer("Вы и так в самом конце списка")
        return

    list_orders, orders_id = data_orders(active_orders, start)
    await call.message.answer(
        f"Текущие активные заказы:\n\n{list_orders}",
        reply_markup=nav_order(orders_id),
    )
    await call.answer()


@dp.callback_query_handler(Text(startswith="back_"))
async def back(call: types.CallbackQuery):
    await bot.delete_message(
        chat_id=call.from_user.id, message_id=call.message.message_id
    )
    await call.answer()


@dp.callback_query_handler(Text(startswith="access_"))
async def access(call: types.CallbackQuery):
    await call.message.answer("All good!")
