from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

btnBegin = InlineKeyboardButton(text='🤖 Начать работу', callback_data='begin')
btnLaunch = InlineKeyboardButton(text='🤖 Запуск', callback_data='launch')

beginMenu = InlineKeyboardMarkup(row_width=1).add(btnBegin)
mainMenu = InlineKeyboardMarkup(row_width=1).add(btnLaunch)
