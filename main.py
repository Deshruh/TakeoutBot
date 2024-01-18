from aiogram import executor

from disp import dp
import handlers
import logging


# Логгирование
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
