import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from states import AddTransaction
from db import init_db, add_transaction, get_month_stats
from keyboards import main_kb

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я бот для учета финансов 💰\n\n"
        "Выбери действие:",
        reply_markup=main_kb()
    )


# ДОХОД
@dp.message(F.text == "➕ Доход")
async def income_start(message: Message, state: FSMContext):
    await state.set_state(AddTransaction.amount)
    await state.update_data(type="income")
    await message.answer("Введите сумму дохода:")


# РАСХОД
@dp.message(F.text == "➖ Расход")
async def expense_start(message: Message, state: FSMContext):
    await state.set_state(AddTransaction.amount)
    await state.update_data(type="expense")
    await message.answer("Введите сумму расхода:")


# СУММА
@dp.message(AddTransaction.amount)
async def get_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except:
        await message.answer("Введите число!")
        return

    await state.update_data(amount=amount)
    await state.set_state(AddTransaction.category)
    await message.answer("Откуда доход / куда расход? (категория)")


# КАТЕГОРИЯ
@dp.message(AddTransaction.category)
async def get_category(message: Message, state: FSMContext):
    data = await state.get_data()

    await add_transaction(
        user_id=message.from_user.id,
        amount=data["amount"],
        category=message.text,
        type_=data["type"]
    )

    await message.answer("✅ Записано!")
    await state.clear()


# СТАТИСТИКА
@dp.message(F.text == "📊 Статистика")
async def stats(message: Message):
    stats = await get_month_stats(message.from_user.id)

    income = stats["income"]
    expense = stats["expense"]

    await message.answer(
        f"📊 Статистика за месяц:\n\n"
        f"💰 Доходы: {income}\n"
        f"💸 Расходы: {expense}\n"
        f"📉 Баланс: {income - expense}"
    )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())