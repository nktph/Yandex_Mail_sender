import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import markups as nav
from main import start as sender_begin

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Создание объектов бота и диспетчера
bot = Bot(token='ТОКЕН')
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
        with open("recipients.txt", 'r') as file:
            recipients = []
            for recip in file.readlines():
                recipients.append(recip)
        if recipients:
            discount = data['discount']
            date = data['date']
            link = data['link']
            await call.message.edit_text(text='Рассылка запущена')
            result = await sender_begin(recipients,discount,date,link)
            await call.message.answer(f"{result}", reply_markup=nav.beginMenu)
        else:
            await call.message.answer("Список получателей пуст.\nПроверьте файл recipients.txt и повторите попытку", reply_markup=nav.beginMenu)
        await state.finish()

# Обработка всех остальных сообщений
@dp.callback_query_handler(state='*')
async def menu(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'begin':
        await call.message.edit_text(text='Введите процент скидки')
        await StateWorker.discount.set()


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
