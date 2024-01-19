from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.types.message import ContentType
import aiogram.utils.markdown as md

from datetime import datetime

from disp import PRICE, bot, dp, botdb, check_sub
import config
from custom_keyboard.user_keyboard import user_kb
from states.user import Description


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_channel_status = await bot.get_chat_member(
        chat_id=config.CHANNEL_ID, user_id=user_id
    )
    check_mem = check_sub(user_channel_status)
    if check_mem != True:
        await message.answer(check_mem)
    elif botdb.user_exist(user_id):
        await message.answer("Hello, world!", reply_markup=user_kb)
    else:
        await message.answer(
            f"Здравствуй, {message.from_user.first_name}! Если ты здесь впервые, то рекомендую тебе отправить команду /help"
        )


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(
        f"""Этот бот предназначен для создания сервиса по вынесу вашего мусора не выходя из дома\n
Чтобы начать пользоваться ботом, необходимо подписаться на канал {config.CHANNEL_LINK} и предоставить ваше ФИО и адрес места жительства. Для регистрации отправьте команду /reg.\n
Дальше вам необходимо оформить подписку на сервис или же, если вы у нас впервые, воспользоваться бесплатной пробной заявкой!\n
Затем вы можете оформить заказ просто нажав на кнопку "Вынести".\n
Напоминаем, что первый заказ - бесплатный!"""
    )


# регистрация клиента
@dp.message_handler(commands=["reg"])
async def registration(message: types.Message):
    user_id = message.from_user.id
    if botdb.user_exist(user_id):
        await message.answer("Вы уже зарегестрированы!")
    elif message.text == "/reg":
        await message.answer(
            "Введите после команды ваше ФИО и адрес проживания.\nК примеру: /reg Иванов Иван Иванович Москва Советский район улица Ленина дом 116 квартира 20\nПишите без запятых и других знаков препинания!"
        )
    else:
        user_data = message.text.split(" ")[1:]
        name = f"{user_data[0]} {user_data[1]} {user_data[2]}"
        city = f"{user_data[3]}"
        area = f"{user_data[4]} {user_data[5]}"
        street = f"{user_data[6]} {user_data[7]}"
        house = f"{user_data[8]} {user_data[9]}"
        flat = f"{user_data[10]} {user_data[11]}"

        botdb.add_user(user_id, name, city, area, street, house, flat)

        await message.answer(
            "Поздравляю, вы зарегистрированы! Перезапустите бота командой /start"
        )


# сообщение с кнопкой оплаты
@dp.message_handler(commands=["buy"])
async def buy(message: types.Message):
    user_channel_status = await bot.get_chat_member(
        chat_id=config.CHANNEL_ID, user_id=message.from_user.id
    )
    check_mem = check_sub(user_channel_status)
    if check_mem != True:
        await message.answer(check_mem)
    else:
        if config.PAYMENTS_TOKEN.split(":")[1] == "TEST":
            await bot.send_message(message.chat.id, "Тестовый платеж!")

        await bot.send_invoice(
            message.chat.id,
            title="Подписка на 1 месяц",
            description="Описание продукта",
            provider_token=config.PAYMENTS_TOKEN,
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


# pre checkout (необходимо ответить в течении 10 секуд)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)  # type: ignore


# выдача Prime-статуса после оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} - {v}")

    await bot.send_message(
        message.chat.id,
        f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!",
    )


# отмена операции. Пример: отмена оформления заявки на вынос мусора
@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять")
        return

    await state.finish()
    await message.answer("Отмена операции")


# получаем описание к заказу
@dp.message_handler(state=Description.description)
async def write_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
        await message.answer(
            f"Вы уверены в своем описании(да/нет)?\n{data['description']}"
        )
    await Description.next()


# подтверждаем, что описание верное и формируем заявку
@dp.message_handler(state=Description.successful)
async def successful_order(message: types.Message, state: FSMContext):
    if message.text.lower() == "нет":
        await message.answer("Измените описание к вашему заказ:")
        await Description.description.set()
    else:
        async with state.proxy() as data:
            user_id = message.from_user.id
            date = str(datetime.now().strftime("%d-%m-%Y %H:%M"))
            botdb.add_order(user_id, data["description"], date)
            order_id = botdb.data_order(user_id, status="active")[0][0]
            await message.answer(f"Ваш заказ №{order_id} офомлен!")
        await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    user_channel_status = await bot.get_chat_member(
        chat_id=config.CHANNEL_ID, user_id=message.from_user.id
    )
    check_mem = check_sub(user_channel_status)
    if check_mem != True:
        await message.answer(check_mem)
    else:
        await message.answer(
            "Я не понимаю вас. Отправьте команду /help для получения справки по боту"
        )
