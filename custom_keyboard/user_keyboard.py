from aiogram import types
from aiogram.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from disp import PRICE, bot, botdb, dp, data_profile
from config import PAYMENTS_TOKEN
from states.user import Description, Edit
import text

successful_kb = ReplyKeyboardMarkup(resize_keyboard=True)  # type: ignore
successful_kb.add(types.KeyboardButton("Да")).add(types.KeyboardButton("Нет"))  # type: ignore

delete_kb = ReplyKeyboardRemove()  # type: ignore

# Меню редактирования профиля
edit_profile_kb = InlineKeyboardMarkup()
edit_profile_kb.add(InlineKeyboardButton("Назад", callback_data="menu"))  # type: ignore
edit_profile_kb.add(InlineKeyboardButton("Изменить профиль", callback_data="edit"))  # type: ignore

# Пользовательское меню
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
    if call.data == "menu":
        await call.message.answer(text.greeting, reply_markup=user_kb)

    elif call.data == "profile":
        chat_id = call.message.chat.id
        await call.message.answer(data_profile(chat_id), reply_markup=edit_profile_kb)  # type: ignore

    elif call.data == "takeout":
        prime = data_profile(call.message.chat.id, data=True)[-1]
        if prime <= 0:  # type: ignore
            await call.message.answer(text.not_prime)
        elif botdb.order_exist(call.message.chat.id):
            await call.message.answer(text.order_exist)
        else:
            await Description.description.set()
            await call.message.answer(text.order_description)

    elif call.data == "buy":
        if PAYMENTS_TOKEN.split(":")[1] == "TEST":
            await call.message.answer(text.test_payment)

        await bot.send_invoice(
            call.message.chat.id,
            title=text.prime,
            description=text.description_prime,
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
        if history == "":
            await call.message.answer("У вас нет ни одного оформленного заказа")
        else:
            await call.message.answer(
                f"""
                История заказов пользователя \"{name}\":\n{history}
                """
            )
        await call.message.answer(text.greeting, reply_markup=user_kb)

    elif call.data == "rules":
        await call.message.answer(text.rules)
        await call.message.answer(text.greeting, reply_markup=user_kb)

    elif call.data == "edit":
        await Edit.name.set()
        await call.message.answer(text.edit_name)

    await bot.answer_callback_query(call.id)
