from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from disp import bot, dp


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
        await call.message.answer("Button TAKEOUT succesful work!")
    elif call.data == "buy":
        await call.message.answer("Button BUY succesful work!")
    elif call.data == "history":
        await call.message.answer("Button HISTORY succesful work!")
    elif call.data == "rules":
        await call.message.answer("Button RULES succesful work!")

    await bot.answer_callback_query(call.id)
