from aiogram.types import Message

from disp import dp
from text import not_understand


@dp.message_handler()
async def echo(message: Message):
    await message.answer(not_understand)
