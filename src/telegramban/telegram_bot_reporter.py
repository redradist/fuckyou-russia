import argparse
import asyncio
import os
import re
import sys
import traceback
import random
import pandas as pd

from typing import Union, Optional, Tuple, Callable, Awaitable, List
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode, Message
from aiogram.utils import executor
from telethon import TelegramClient
from phonenumbers.phonenumberutil import country_code_for_region
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError
from telethon.sessions import SQLiteSession, StringSession
from database.database import async_db_session, UserSession
from loader import dp, bot
from scheduler import scheduler
from states import UserState
from telegram_ban import report_channels, fuckyou_russia_channels
from telegramban.telegram_bot_types import User

import telegram_keyboard as kb
import database.models
from telegramban.google_api import download_drive_file, download_sheet_file

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']

user_code_fut = dict()
user_password_fut = dict()

code_pattern = r"code(?P<code>\d+)"
code_regex = re.compile(code_pattern)


class BotException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return f"BotException({self.msg})"


async def create_or_update_session(user: User):
    users = await UserSession.filter_by_phone(user.phone)
    if len(users) > 0:
        users = await UserSession.update(id=user.id,
                                         user_id=user.id,
                                         name=user.name,
                                         phone=user.phone,
                                         session=user.session)
    else:
        users = await UserSession.create(user_id=user.id,
                                         name=user.name,
                                         phone=user.phone,
                                         session=user.session)

async def get_all_users() -> List[User]:
    return await UserSession.get_all()


async def get_session(user: User) -> str:
    users = await UserSession.filter_by_phone(user.phone)
    if len(users) > 0:
        return users[0].session
    else:
        return ''


async def is_start_command(msg):
    return msg.is_command() or msg.text in [kb.msg_restart_ru, kb.msg_restart_ua, kb.msg_restart_en]


async def hello_help(msg):
    locale = msg.from_user.locale
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


async def press_button_start_again(msg):
    locale = msg.from_user.locale
    user_id = msg.from_user.id
    if locale.language == 'ru':
        await bot.send_message(user_id, f"Время вышло, отправте команду 'Начать заново'")
    elif locale.language == 'ua':
        await bot.send_message(user_id, f"Время вийшло, відправте команду 'Почати знову'")
    else:
        await bot.send_message(user_id, f"Timeout, press command 'Start again️'")


async def enter_phone(msg):
    locale = msg.from_user.locale
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
        await bot.send_message(msg.from_user.id, f"Пожалуйста введите код подтверждения в формате: code|Code|. Для примера: code213243 або Сode213243")
    elif locale.language == 'ua':
        await bot.send_message(msg.from_user.id, f"Будь-даска введіть код підтвердження у форматі: code|Code|. Для примера: code213243 або Сode213243")
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


async def fuck_russia_channels(msg):
    locale = msg.from_user.locale
    user_id = msg.from_user.id
    if locale.language == 'ru':
        await bot.send_message(user_id, f"Вы залогинены, сейчас вы выебете рашисткие телеграм каналы !! Благодарю за сотрудничество !!")
    elif locale.language == 'ua':
        await bot.send_message(user_id, f"Ви залогінені, зараз ви виебет рашисткі телеграм канали !! Дякую за співпрацю !!")
    else:
        await bot.send_message(user_id, f"You are logged in, now you will fuck russian telegram channels !! Thank you for your cooperation !!")


async def enter_phone_again(user: User):
    if user.lang == 'ru':
        await bot.send_message(user.id, f"Сессия окончена, если вы хотите продолжить помогать блокировать рашисткие "
                                        f"телеграм каналы, полажуйста нажмите кнопку начать заново")
    elif user.lang == 'ua':
        await bot.send_message(user.id, f"Сесія закінчена, якщо ви хочете продовжити допомагати блокувати рашисткі "
                                        f"телеграм канали, будь ласка, натисніть кнопку почати заново ")
    else:
        await bot.send_message(user.id, f"The session is over, if you want to continue helping to block rassian "
                                        f"telegram channels, please click the button to start again ")



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


async def connect_using_phone(msg, phone):
    username = msg.from_user.mention
    session = await get_session(User(id=msg.from_user.id,
                                     name=username,
                                     phone=phone,
                                     lang=msg.from_user.locale.language))
    client = TelegramClient(StringSession(session), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await UserState.Code.set()
                response = await client.send_code_request(phone)
                await enter_code_confirmation(msg)
                loop = asyncio.get_running_loop()
                code_fut = loop.create_future()
                user_code_fut[username] = code_fut
                code = await code_fut
                await client.sign_in(phone=phone, code=code, phone_code_hash=response.phone_code_hash)
            if await client.is_user_authorized():
                await UserState.Done.set()
                await create_or_update_session(User(id=msg.from_user.id,
                                                    name=username,
                                                    phone=phone,
                                                    lang=msg.from_user.locale.language,
                                                    session=client.session.save()))
                await fuck_russia_channels(msg)
                await report_channels(client)
                await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except SessionPasswordNeededError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        await UserState.Password.set()
        await enter_password_confirmation(msg)

        loop = asyncio.get_running_loop()
        password_fut = loop.create_future()
        user_password_fut[username] = password_fut
        password = await password_fut
        response = await client.sign_in(password=password)
        if await client.is_user_authorized():
            user = response
            await UserState.Done.set()
            await create_or_update_session(User(id=msg.from_user.id,
                                                name=username,
                                                phone=phone,
                                                lang=msg.from_user.locale.language,
                                                session=client.session.save()))
            await fuck_russia_channels(msg)
            await report_channels(client)
            await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


async def send_code(msg, state, phone):
    username = msg.from_user.mention
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await UserState.Code.set()
                response = await client.send_code_request(phone)
                await enter_code_confirmation(msg)
                async with state.proxy() as data:
                    data['phone_code_hash'] = response.phone_code_hash
                    print(f"phone = {phone}, phone_code_hash = {response.phone_code_hash}")
            else:
                await fuck_russia_channels(msg)
                await report_channels(client)
                await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


async def connect_using_code(msg, phone, code, phone_code_hash):
    username = msg.from_user.mention
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
                await UserState.Done.set()
                await fuck_russia_channels(msg)
                await report_channels(client)
                await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except SessionPasswordNeededError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        await UserState.Password.set()
        await enter_password_confirmation(msg)

        loop = asyncio.get_running_loop()
        password_fut = loop.create_future()
        user_password_fut[username] = password_fut
        password = await password_fut
        response = await client.sign_in(password=password)
        if await client.is_user_authorized():
            user = response
            await UserState.Done.set()
            await fuck_russia_channels(msg)
            await report_channels(client)
            await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


async def connect_using_password(msg, state, phone, password):
    username = msg.from_user.mention
    client = TelegramClient(SQLiteSession(username), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                response = await client.sign_in(password=password)
                if await client.is_user_authorized():
                    user = response
                    await UserState.Done.set()
                    await fuck_russia_channels(msg)
                    await report_channels(client)
                    await all_channels_reported(msg.from_user.id, msg.from_user.locale.language)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        user_id = msg.from_user.id
        await bot.send_message(user_id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()


def create_report_channels_callback(msg) -> Callable[[Union[Optional[str], Tuple[str, Exception]]], Awaitable[None]]:
    locale = msg.from_user.locale
    user_id = msg.from_user.id

    async def report_channels_callback(arg: Union[Optional[str], Tuple[str, Exception]]):
        if type(arg) == str:
            ch_name = arg
            if locale.language == 'ru':
                await bot.send_message(user_id, f"Успешно отправлен репорт про {ch_name}")
            elif locale.language == 'ua':
                await bot.send_message(user_id, f"Успішно відправлено репорт про {ch_name}")
            else:
                await bot.send_message(user_id, f"Successfully reported about {ch_name}")
        elif type(arg) == tuple:
            ch_name, ex = arg
            if locale.language == 'ru':
                await bot.send_message(user_id, f"ОШИБКА: Репорт про канал {ch_name}:\n{ex}")
            elif locale.language == 'ua':
                await bot.send_message(user_id, f"ПОМИЛКА: Репорт про канал {ch_name}:\n{ex}")
            else:
                await bot.send_message(user_id, f"ERROR: Report about {ch_name}:\n{ex}")
        elif arg is None:
            if locale.language == 'ru':
                await bot.send_message(user_id, "Репорты на все каналы отправлены успешно !!")
            elif locale.language == 'ua':
                await bot.send_message(user_id, "Репорти на всі канали відправлені успішно !!")
            else:
                await bot.send_message(user_id, "All channels reported successfully !!")

    return report_channels_callback


@dp.message_handler(commands='start',
                    state='*')
async def process_start_command(msg: Message):
    username = msg.from_user.mention
    print(f"Received command 'start' from {username}")
    await UserState.Phone.set()
    await hello_help(msg)
    await enter_phone(msg)


@dp.message_handler(Text(equals=[kb.msg_restart_ru, kb.msg_restart_ua, kb.msg_restart_en], ignore_case=True),
                    state='*')
async def process_text_command(msg: Message, state: FSMContext):
    username = msg.from_user.mention
    if await is_start_command(msg):
        if username in user_code_fut:
            code_fut = user_code_fut[username]
            code_fut.cancel()

        if username in user_password_fut:
            password_fut = user_password_fut[username]
            password_fut.cancel()

        print(f"Received command 'restart' from {username}")
        await UserState.Phone.set()
        await enter_phone(msg)


@dp.message_handler(state=UserState.Phone, content_types=ContentType.CONTACT)
async def process_phone(msg: Message, state: FSMContext):
    username = msg.from_user.mention
    if not await is_start_command(msg):
        phone = msg.contact.phone_number
        phone = await phone_validate_and_update(msg, phone)
        if not phone:
            return

        print(f"Received phone = {phone} from {username}")
        async with state.proxy() as data:
            data['phone'] = phone

        # TODO: send_code do not work because using it creates separate client for sending code
        # See also the issue https://github.com/LonamiWebs/Telethon/issues/278 and other multiple errors
        # asyncio.create_task(send_code(msg, state, phone))
        asyncio.create_task(connect_using_phone(msg, phone))


@dp.message_handler(state=UserState.Phone, content_types=ContentType.TEXT)
async def process_phone_text(msg: Message, state: FSMContext):
    username = msg.from_user.mention
    if not await is_start_command(msg):
        phone = msg.text
        phone = await phone_validate_and_update(msg, phone)
        if not phone:
            return

        print(f"Received phone = {phone} from {username}")
        async with state.proxy() as data:
            data['phone'] = phone

        # TODO: send_code do not work because using it creates separate client for sending code
        # See also the issue https://github.com/LonamiWebs/Telethon/issues/278 and other multiple errors
        # asyncio.create_task(send_code(msg, state, phone))
        asyncio.create_task(connect_using_phone(msg, phone))


@dp.message_handler(state=UserState.Code)
async def process_code(msg: Message, state: FSMContext):
    username = msg.from_user.mention
    if not await is_start_command(msg):
        code_match = code_regex.match(msg.text.lower().replace(' ', ''))
        if not code_match:
            await confirmation_code_error(msg)
        else:
            code = code_match.group('code')
            print(f"Received code = {code} from {username}")
            username = msg.from_user.mention
            if username in user_code_fut:
                code_fut = user_code_fut[username]
                code_fut.set_result(code)
            else:
                async with state.proxy() as data:
                    data['code'] = code
                    phone = data['phone']
                    phone_code_hash = data['phone_code_hash']
                    print(f"phone = {phone}, phone_code_hash = {phone_code_hash}")

                    asyncio.create_task(connect_using_code(msg, phone, code, phone_code_hash))


@dp.message_handler(state=UserState.Password)
async def process_password(msg: Message, state: FSMContext):
    username = msg.from_user.mention
    if not await is_start_command(msg):
        password = msg.text
        print(f"Received password *** from {username}")
        if len(password) == 0:
            await confirmation_password_error(msg)
        else:
            username = msg.from_user.mention
            if username in user_password_fut:
                password_fut = user_password_fut[username]
                password_fut.set_result(password)
            else:
                phone = None
                async with state.proxy() as data:
                    data['password'] = password
                    phone = data['phone']
                await connect_using_password(msg, state, phone, password)


def download_channels_file(args):
    try:
        try:
            download_sheet_file(args.google_api_creds_path, args.save_sheet_path, args.sheet_filename)
        except Exception as ex:
            print(f"ERROR: {ex}", file=sys.stderr)
            traceback.print_stack(file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

        channels_df = pd.read_csv(f"{args.save_sheet_path}/{args.sheet_filename}.csv")
        channels_df = channels_df.reset_index()
        fuckyou_russia_channels.clear()
        for index, row in channels_df.iterrows():
            fuckyou_russia_channels.append([row['Channel Id'], row['Channel Name']])
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)


async def all_channels_reported(user_id ,lang):
    num_channels = len(fuckyou_russia_channels)
    if lang == 'ru':
        await bot.send_message(user_id, f"Репорты на {num_channels} каналы отправлены успешно !!")
    elif lang == 'ua':
        await bot.send_message(user_id, f"Репорти на {num_channels} канали відправлені успішно !!")
    else:
        await bot.send_message(user_id, f"All {num_channels} channels reported successfully !!")


async def report_channels_again(user):
    print(f"report_channels_again for user = {user.name}")
    client = TelegramClient(StringSession(user.session), API_ID, API_HASH)
    try:
        await client.connect()
        if client.is_connected():
            if await client.is_user_authorized():
                await report_channels(client)
                await all_channels_reported(user.id, user.lang)
            else:
                await enter_phone_again(user)
    except Exception as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        traceback.print_stack(file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        await bot.send_message(user.id, f"ERROR: {ex}")
    finally:
        if client.is_connected():
            await client.disconnect()
        scheduler.remove_job(user.name)


async def tick_report_channels_again():
    print(f"tick_report_channels_again")
    download_channels_file(args)

    users = await get_all_users()
    for user in users:
        minutes = int(random.uniform(5, 240))
        scheduler.add_job(report_channels_again,
                          'interval',
                          args=[user],
                          minutes=minutes,
                          id=user.name)


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--google_api_creds_path',
                        type=str,
                        required=True,
                        help='Path to google api credentials path')
    parser.add_argument('--save_sheet_path',
                        type=str,
                        required=True,
                        help='Save sheet path')
    parser.add_argument('--sheet_filename',
                        type=str,
                        required=True,
                        help='Sheet file name')

    return parser.parse_args()


async def main(args):
    scheduler.start()
    await tick_report_channels_again()
    scheduler.add_job(tick_report_channels_again, 'interval', hours=4)

    # NOTE: For debug purposes
    # await async_db_session.drop_all()
    await async_db_session.create_all()
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    args = parse_args()
    asyncio.run(main(args))
