from aiogram import types
from aiogram.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from disp import bot, botdb, dp, PRICE
from config import PAYMENTS_TOKEN
from states.user import Description
import text

successful_kb = ReplyKeyboardMarkup()  # type: ignore
successful_kb.add(types.KeyboardButton("Да")).add(types.KeyboardButton("Нет"))  # type: ignore

delete_kb = ReplyKeyboardRemove()  # type: ignore

# пользовательское меню
user_kb = InlineKeyboardMarkup(row_width=2)

buttons = [
    "Вынести-takeout",
    "Оплатить-buy",
    "История-history",
    "Правила-rules",
    "Профиль-profile",
]

for button in buttons:
    button = button.split("-")
    user_kb.insert(InlineKeyboardButton(button[0], callback_data=button[1]))  # type: ignore


@dp.callback_query_handler()
async def callback(call: types.CallbackQuery):
    if call.data == "profile":
        await call.message.answer("Button PROFILE succesful work!")

    elif call.data == "takeout":
        if botdb.order_exist(call.message.chat.id):
            await call.message.answer(f"У тебя уже есть активный заказ!")
        else:
            await Description.description.set()
            await call.message.answer("Оставьте описание к вашему заказ:")

    elif call.data == "buy":
        if PAYMENTS_TOKEN.split(":")[1] == "TEST":
            await call.message.answer("Тестовый платеж!")

        await bot.send_invoice(
            call.message.chat.id,
            title="Подписка на 1 месяц",
            description="Описание продукта",
            provider_token=PAYMENTS_TOKEN,
            currency="rub",
            photo_url="https://static.mk.ru/upload/entities/2023/03/09/08/articles/detailPicture/4c/4b/48/ec/e3ca4d5a88ca9c93f6b52524895fdd01.jpg",
            photo_width=550,
            photo_height=412,
            photo_size=550,
            is_flexible=False,  # type: ignore
            prices=[PRICE],
            start_parameter="one-match-subscripton",
            payload="test-invoice-payload",
        )

    elif call.data == "history":
        chat_id = call.message.chat.id
        orders = botdb.data_order(chat_id)

        name = botdb.data_user(chat_id)[0][1]
        history = ""
        for order in orders[::-1]:
            history += f"""
Номер заказа: {order[0]}
Статус: {order[1]}
Описание: {order[2]}
Дата оформления: {order[3].split(' ')[0]}
"""

        await call.message.answer(
            f"""
            История заказов пользователя \"{name}\":\n{history}
            """
        )

    elif call.data == "rules":
        await call.message.answer(text.rules)

    await bot.answer_callback_query(call.id)
