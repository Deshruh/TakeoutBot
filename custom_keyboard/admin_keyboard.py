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

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)  # type: ignore
buttons = ["Orders", "History"]
admin_kb.add(types.KeyboardButton("Profile"))  # type: ignore
admin_kb.add(*buttons)
