import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import markups as nav
from main import work as sender_begin

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token='ВСТАВИТЬ ТОКЕН СЮДА')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class StateWorker(StatesGroup):
    recipients_list = State()
    discount = State()
    date = State()
    link = State()
    work = State()

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Держи меню.", reply_markup=nav.beginMenu)

# Добавление Аккаунтов
@dp.message_handler(state=StateWorker.recipients_list)
async def add_recipients(message: types.Message, state: FSMContext):
    recipients = message.text.splitlines()
    if recipients:
        await state.update_data(recipients=recipients)
        await StateWorker.discount.set()
        await message.answer("Теперь введите процент скидки")
    else:
        await message.answer("Список невалидный, попробуйте ещё раз")


@dp.message_handler(state=StateWorker.discount)
async def set_discount(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        discount = int(message.text)
        await state.update_data(discount=discount)
        await message.answer("Введите дату окончания акции\nПример: 11 июня 2023 года")
        await StateWorker.date.set()
    else:
        await message.answer("Введите число")


@dp.message_handler(state=StateWorker.date)
async def set_date(message: types.Message, state: FSMContext):
    date = message.text
    await state.update_data(date=date)
    await message.answer("Введите ссылку для кнопки")
    await StateWorker.link.set()


@dp.message_handler(state=StateWorker.link)
async def set_link(message: types.Message, state: FSMContext):
    link = message.text
    await state.update_data(link=link)
    await message.answer("Ссылка задана", reply_markup=nav.mainMenu)
    await StateWorker.work.set()

@dp.callback_query_handler(state=StateWorker.work)
async def set_date(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'launch':
        data = await state.get_data()
        recipients = data['recipients']
        discount = data['discount']
        date = data['date']
        link = data['link']
        await call.message.edit_text(text='Рассылка запущена')
        sender_begin(recipients,discount,date,link)
        await state.finish()
        await call.message.answer("Рассылка завершена", reply_markup=nav.beginMenu)

# Обработка всех остальных сообщений
@dp.callback_query_handler(state='*')
async def menu(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'begin':
        await call.message.edit_text(text='Введите список адресатов в формате:\n'
                                          'адрес1\n'
                                          'адрес2\n'
                                          '...')
        await StateWorker.recipients_list.set()


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
