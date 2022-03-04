import asyncio
import os
import re
import sys

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, ParseMode, Message
from telethon import TelegramClient
from phonenumbers.phonenumberutil import country_code_for_region
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import SQLiteSession
from src.database.database import async_db_session
from loader import dp, bot
from src.database.models import TelegramSession

import telegram_keyboard as kb
from states import User
from telegram_ban import report_channels

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']

user_password_fut = dict()

code_pattern = r"(code|код)(?P<code>\d+)"
code_regex = re.compile(code_pattern)
restart_command_pattern = rf"({kb.msg_restart_ru}|{kb.msg_restart_ua}|{kb.msg_restart_en})"


class BotException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"BotException({self.msg})"


async def get_session(user_name):
    sessions = await TelegramSession.filter_by_user_name(user_name)
    if len(sessions) > 0:
        return sessions[0].user_session
    else:
        return ''


async def create_or_update_session(user_name, user_session):
    await TelegramSession.create(user_name=user_name, user_session=user_session)
    user = await TelegramSession.get(1)
    return user.id


async def is_start_command(msg):
    return msg.is_command() or msg.text in [kb.msg_restart_ru, kb.msg_restart_ua, kb.msg_restart_en]


async def press_button_start_again(msg):
    locale = msg.from_user.locale
    user_id = msg.from_user.id
    if locale.language == 'ru':
        await bot.send_message(user_id, f"Время вышло, отправте команду 'Начать заново'")
    elif locale.language == 'ua':
        await bot.send_message(user_id, f"Время вийшло, відправте команду 'Почати знову'")
    else:
        await bot.send_message(user_id, f"Timeout, press command 'Start again️'")


async def enter_phone_first(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id, f"Введите телефон первым !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Введіть телефон першим !!")
    else:
        await bot.send_message(msg.from_user.id, f"Enter phone first !!")


async def enter_phone_error_empty(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id, f"Телефоный номер должен содержать цифры !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Телефоний номер повинен містити цифри !!")
    else:
        await bot.send_message(msg.from_user.id, f"Phone number should contains digits !!")


async def enter_phone_error_plus(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id,
                               f"Телефоный номер должен иметь 13 символов если он начинается с символа '+' !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id,
                               f"Телефоний номер повинен мати 13 символів якщо він починається з символу '+' !!")
    else:
        await bot.send_message(msg.from_user.id,
                               f"Phone number should have size 13 symbols if it starts from symbol '+' !!")


async def enter_phone_error_3(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id,
                               f"Телефоный номер должен иметь 12 символов если он начинается с цифры '3' !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id,
                               f"Телефоний номер повинен мати 12 символів якщо він починається з цифри '3' !!")
    else:
        await bot.send_message(msg.from_user.id,
                               f"Phone number should have size 12 symbols if it starts from digit '3' !!")


async def enter_phone_error(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id,
                               f"Телефоный номер должен иметь 11 символов если он начинается с кода страны !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id,
                               f"Телефоний номер повинен мати 11 символів якщо він починається з кода країни !!")
    else:
        await bot.send_message(msg.from_user.id,
                               f"Phone number should have size 11 symbols if it starts from country code !!")


async def enter_code_confirmation(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id, f"Пожалуйста введите код подтверждения в формате: код|Код|. Для примера: код213243 або Код213243")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Будь-даска введіть код підтвердження у форматі: код|Код|. Для примера: код213243 або Код213243")
    else:
        await bot.send_message(msg.from_user.id, f"Enter code confirmation in format: code|Code|. For example: code213243 or Code213243")


async def enter_password_confirmation(msg):
    locale = msg.from_user.locale
    user_id = msg.from_user.id
    if locale.language == 'ru':
        await bot.send_message(user_id, f"Ошибка при получении кода, у вас включена Two Factor Autorization попробуйте ввести пароль !!")
    elif locale.language == 'ua':
        await bot.send_message(user_id, f"Помилка при отриманні коду, у вас включена Two Factor Autorization спробуйте ввести пароль !!")
    else:
        await bot.send_message(user_id, f"Error receiving code, you have Two Factor Autorization enabled try enter your password !!")


async def confirmation_code_error(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id, f"Код подтверждения не должен быть пустым !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Код підтвердження не повинен бути пустим !!")
    else:
        await bot.send_message(msg.from_user.id, f"Code confirmation shouldn't be empty !!")


async def confirmation_password_error(msg):
    locale = msg.from_user.locale
    if locale.language == 'ru':
        await bot.send_message(msg.from_user.id, f"Пароль подтверждения не должен быть пустым !!")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Пароль підтвердження не повинен бути пустим !!")
    else:
        await bot.send_message(msg.from_user.id, f"Password confirmation shouldn't be empty !!")


async def phone_validate_and_update(msg, phone):
    locale = msg.from_user.locale
    if len(phone) == 0:
        await enter_phone_error_empty(msg)
    elif phone[0] == '+':
        if len(phone) != 13:
            await enter_phone_error_plus(msg)
        else:
            return phone
    elif phone[0] == '3':
        phone = '+' + phone
        if len(phone) != 13:
            await enter_phone_error_3(msg)
        else:
            return phone
    else:
        if len(phone) == 10 and locale.territory is not None:
            phone = str(country_code_for_region(locale.territory)) + phone
        phone = '+3' + phone
        if len(phone) != 13:
            await enter_phone_error(msg)
        else:
            return phone


@dp.message_handler(commands=['start'])
async def process_start_command(msg: Message):
    locale = msg.from_user.locale
    await User.Phone.set()
    if locale.language == 'ru':
        await msg.answer(
            f"Привет, {msg.from_user.get_mention(as_html=True)} 👋!\n"
            f"Этот чат позволяет заблокировать телеграмм каналы которые распространяют ложную информацию об Украине, "
            f"а также платят террористам за терракты в Украине !\n",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.menu_ru
        )
    elif locale.language == 'ua':
        await msg.answer(
            f"Привіт, {msg.from_user.get_mention(as_html=True)} 👋!\n"
            f"Цей чат дозволяє заблокувати телеграмм канали котрі розповсюджують хибну інформацію про Україну, "
            f"а також платят терористам за теракти в Україні !\n",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.menu_ua
        )
    else:
        await msg.answer(
            f"Hello, {msg.from_user.get_mention(as_html=True)} 👋!\n"
            f"This chat bot allows to block the telegram channels that spread misinformation about Ukraine "
            f"and pay terrorists for tract on Ukraine !\n",
            parse_mode=ParseMode.HTML,
            reply_markup=kb.menu_en
        )


@dp.message_handler(state=User.Phone, content_types=ContentType.CONTACT)
async def process_phone(msg: Message, state: FSMContext):
    if not await is_start_command(msg):
        phone = msg.contact.phone_number
        phone = await phone_validate_and_update(msg, phone)
        if not phone:
            return

        print(f"Received phone = {phone}")
        async with state.proxy() as data:
            data['phone'] = phone

        await User.Code.set()

        await send_code(msg, state, phone)


@dp.message_handler(state=User.Phone, content_types=ContentType.TEXT)
async def process_phone_text(msg: Message, state: FSMContext):
    if not await is_start_command(msg):
        phone = msg.text
        phone = await phone_validate_and_update(msg, phone)
        if not phone:
            return

        print(f"Received phone = {phone}")
        async with state.proxy() as data:
            data['phone'] = phone

        await send_code(msg, state, phone)


async def send_code(msg, state, phone):
    username = msg.from_user.username
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await User.Code.set()
                response = await client.send_code_request(phone)
                await enter_code_confirmation(msg)
                async with state.proxy() as data:
                    data['phone_code_hash'] = response.phone_code_hash
            else:
                await report_channels(client)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


@dp.message_handler(state=User.Code)
async def process_code(msg: Message, state: FSMContext):
    if not await is_start_command(msg):
        code_match = code_regex.match(msg.text.lower().replace(' ', ''))
        if not code_match:
            await confirmation_code_error(msg)
        else:
            code = code_match.group('code')
            print(f"Received code = {code}")
            phone = None
            phone_code_hash = None
            async with state.proxy() as data:
                data['code'] = code
                phone = data['phone']
                phone_code_hash = data['phone_code_hash']

                asyncio.create_task(connect_using_code(msg, phone, code, phone_code_hash))


async def connect_using_code(msg, phone, code, phone_code_hash):
    username = msg.from_user.username
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
                await User.Done.set()
                await report_channels(client)
    except SessionPasswordNeededError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        await User.Password.set()
        await enter_password_confirmation(msg)

        loop = asyncio.get_running_loop()
        password_fut = loop.create_future()
        user_password_fut[username] = password_fut
        password = await password_fut
        response = await client.sign_in(password=password)
        if await client.is_user_authorized():
            user = response
            await User.Done.set()
            await report_channels(client)

    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


@dp.message_handler(state=User.Password)
async def process_password(msg: Message, state: FSMContext):
    if not await is_start_command(msg):
        password = msg.text
        print(f"Received password = {password}")
        if len(password) == 0:
            await confirmation_password_error(msg)
        else:
            username = msg.from_user.username
            if username in user_password_fut:
                password_fut = user_password_fut[username]
                password_fut.set_result(password)
            else:
                phone = None
                async with state.proxy() as data:
                    data['password'] = password
                    phone = data['phone']
                await connect_using_password(msg, state, phone, password)


async def connect_using_password(msg, state, phone, password):
    username = msg.from_user.username
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                response = await client.sign_in(password=password)
                if await client.is_user_authorized():
                    user = response
                    await User.Done.set()
                    await report_channels(client)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


@dp.message_handler(state=User.Done)
@dp.message_handler(state='*', commands=['start'])
@dp.message_handler(state='*', regexp=restart_command_pattern)
async def process_text_command(msg: Message, state: FSMContext):
    username = msg.from_user.username
    locale = msg.from_user.locale
    if await is_start_command(msg):
        if username in user_password_fut:
            password_fut = user_password_fut[username]
            password_fut.cancel()

        await User.Phone.set()
        if locale.language == 'ru':
            await msg.reply(
                f"Введите свой номер телефона\n",
                parse_mode=ParseMode.HTML,
                reply_markup=kb.menu_ru
            )
        elif locale.language == 'ua':
            await msg.reply(
                f"Введіть свій номер телефона\n",
                parse_mode=ParseMode.HTML,
                reply_markup=kb.menu_ua
            )
        else:
            await msg.reply(
                f"Enter your phone number\n",
                parse_mode=ParseMode.HTML,
                reply_markup=kb.menu_en
            )


async def main():
    await async_db_session.init()
    await async_db_session.create_all()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
