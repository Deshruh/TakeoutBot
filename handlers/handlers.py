from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

# from aiogram.types import ParseMode
from aiogram.types.message import ContentType

# import aiogram.utils.markdown as md

from datetime import datetime

from disp import PRICE, bot, dp, botdb, check_sub, data_profile
import config
from custom_keyboard.user_keyboard import user_kb, successful_kb, delete_kb
from states.user import Description, Form
import text


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
        await message.answer(text.greeting, reply_markup=user_kb)
    else:
        await message.answer(f"{message.from_user.first_name}, {text.greet_no_reg}")


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(text.help_text)


# отмена операции. Пример: отмена оформления заявки на вынос мусора
@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(text.cancel[0])
        return

    await state.finish()
    await message.answer(text.cancel[1])


# регистрация клиента
@dp.message_handler(commands=["reg"])
async def registration(message: types.Message):
    user_id = message.from_user.id
    user_channel_status = await bot.get_chat_member(
        chat_id=config.CHANNEL_ID, user_id=user_id
    )
    check_mem = check_sub(user_channel_status)
    if check_mem != True:
        await message.answer(check_mem)
    elif botdb.user_exist(user_id):
        await message.answer(text.user_exist)
    else:
        await Form.name.set()
        await message.answer(text.registration[0])


# Выдача правил
@dp.message_handler(commands=["rules"])
async def rules(message: types.Message):
    await message.answer(text.rules)


# Выдача истории заказов
@dp.message_handler(commands=["history"])
async def history(message: types.Message):
    user_id = message.from_user.id
    if botdb.user_exist(user_id):
        orders = botdb.data_order(user_id)
        name = botdb.data_user(user_id)[0][1]

        history = ""
        for order in orders[::-1]:
            history += f"""
Номер заказа: {order[0]}
Статус: {order[1]}
Описание: {order[2]}
Дата оформления: {order[3].split(' ')[0]}
"""

        if history == "":
            await message.answer("У вас нет ни одного оформленного заказа")
        else:
            await message.answer(
                f"""
                История заказов пользователя \"{name}\":\n{history}
                """
            )
    else:
        await message.answer(text.not_registred)


# Профиль пользователя
@dp.message_handler(commands=["profile"])
async def profile(message: types.Message):
    user_id = message.from_user.id
    if botdb.user_exist(user_id):
        chat_id = message.chat.id
        await message.answer(data_profile(chat_id))
    else:
        await message.answer(text.not_registred)


# Профиль пользователя
@dp.message_handler(commands=["takeout"])
async def takeout(message: types.Message):
    user_id = message.from_user.id
    if botdb.user_exist(user_id):
        if botdb.order_exist(message.chat.id):
            await message.answer(text.order_exist)
        else:
            await Description.description.set()
            await message.answer(text.order_description)
    else:
        await message.answer(text.not_registred)


# Получаем имя клиента
@dp.message_handler(state=Form.name)
async def user_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
        await message.answer(text.registration[1])
        await Form.next()


# Получаем адрес клиента
@dp.message_handler(state=Form.adress)
async def user_adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["adress"] = message.text
        await message.answer(
            f'Ваши данные:\nИмя: {data["name"]}\nАдресс: {data["adress"]}\nВсё правильно?',
            reply_markup=successful_kb,
        )
        await Form.next()


# Подтверждение введеных данных
@dp.message_handler(state=Form.successful)
async def succesful_reg(message: types.Message, state: FSMContext):
    if message.text.lower() == "нет":
        await message.answer(text.reg_repeat, reply_markup=delete_kb)
        await Form.name.set()
    else:
        async with state.proxy() as data:
            adress = data["adress"].split(",")
            name = data["name"]
            city = adress[0]
            area = adress[1]
            street = adress[2]
            house = adress[3]
            flat = adress[4]

            botdb.add_user(message.from_user.id, name, city, area, street, house, flat)

            await message.answer(
                text.reg_finished,
                reply_markup=delete_kb,
            )
        await state.finish()


# сообщение с кнопкой оплаты
@dp.message_handler(commands=["buy"])
async def buy(message: types.Message):
    user_id = message.from_user.id
    if botdb.user_exist(user_id):
        if config.PAYMENTS_TOKEN.split(":")[1] == "TEST":
            await bot.send_message(message.chat.id, text.test_payment)

        await bot.send_invoice(
            message.chat.id,
            title=text.prime,
            description=text.description_prime,
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
    else:
        await message.answer(text.not_registred)


# pre checkout (необходимо ответить в течении 10 секуд)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)  # type: ignore


# выдача Prime-статуса после оплаты
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print(text.successful_payment)
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} - {v}")

    await bot.send_message(
        message.chat.id,
        f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!",
    )


# получаем описание к заказу
@dp.message_handler(state=Description.description)
async def write_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = message.text
        await message.answer(
            f"Вы уверены в своем описании(да/нет)?\n{data['description']}",
            reply_markup=successful_kb,
        )
    await Description.next()


# подтверждаем, что описание верное и формируем заявку
@dp.message_handler(state=Description.successful)
async def successful_order(message: types.Message, state: FSMContext):
    if message.text.lower() == "нет":
        await message.answer(text.change_description, reply_markup=delete_kb)
        await Description.description.set()
    else:
        async with state.proxy() as data:
            user_id = message.from_user.id
            date = str(datetime.now().strftime("%d-%m-%Y %H:%M"))
            botdb.add_order(user_id, data["description"], date)
            order_id = botdb.data_order(user_id, status="active")[0][0]
            await message.answer(
                f"Ваш заказ №{order_id} офомлен!", reply_markup=delete_kb
            )
        await state.finish()
        await message.answer(text.greeting, reply_markup=user_kb)


@dp.message_handler()
async def echo(message: types.Message):
    user_channel_status = await bot.get_chat_member(
        chat_id=config.CHANNEL_ID, user_id=message.from_user.id
    )
    check_mem = check_sub(user_channel_status)
    if check_mem != True:
        await message.answer(check_mem)
    else:
        await message.answer(text.not_understand)
