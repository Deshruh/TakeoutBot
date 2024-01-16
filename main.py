from aiogram import executor

from disp import dp
import handlers
import logging


# Логгирование
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
