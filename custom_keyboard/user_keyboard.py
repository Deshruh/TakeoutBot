from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from disp import bot, botdb, dp, PRICE
from config import PAYMENTS_TOKEN
from states.user import Description


user_kb = InlineKeyboardMarkup(row_width=2)

buttons = [
    "Вынести-takeout",
    "Оплатить-buy",
    "История-history",
    "Правила-rules",
    "Меню-menu",
]

for button in buttons:
    button = button.split("-")
    user_kb.insert(InlineKeyboardButton(button[0], callback_data=button[1]))  # type: ignore


@dp.callback_query_handler()
async def callback(call: types.CallbackQuery):
    if call.data == "menu":
        await call.message.answer("Button MENU succesful work!")

    elif call.data == "takeout":
        if botdb.order_exist(call.message.chat.id):
            await call.message.answer(f"Your order exist!")
        else:
            await Description.description.set()
            await call.message.answer("Leave your description for the order")

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
        await call.message.answer("Button HISTORY succesful work!")

    elif call.data == "rules":
        await call.message.answer("Button RULES succesful work!")

    await bot.answer_callback_query(call.id)
