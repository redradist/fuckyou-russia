from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

msg_contact_ru = 'Отправить свой контакт ☎️'
msg_contact_ua = 'Відправити свій контакт ☎️'
msg_contact_en = 'Send your phone number ☎️'

send_contact_ru = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_contact_ru, request_contact=True)
)
send_contact_ua = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_contact_ua, request_contact=True)
)
send_contact_en = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_contact_en, request_contact=True)
)

msg_restart_ru = 'Начать заново️'
msg_restart_ua = 'Почати знову️'
msg_restart_en = 'Start again️️'

restart_ru = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_restart_ru)
)
restart_ua = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_restart_ua)
)
restart_en = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(msg_restart_en)
)

menu_ru = ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(KeyboardButton(msg_contact_ru, request_contact=True))\
    .add(KeyboardButton(msg_restart_ru))
menu_ua = ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(KeyboardButton(msg_contact_ua, request_contact=True))\
    .add(KeyboardButton(msg_restart_ua))
menu_en = ReplyKeyboardMarkup(resize_keyboard=True)\
    .add(KeyboardButton(msg_contact_en, request_contact=True))\
    .add(KeyboardButton(msg_restart_en))