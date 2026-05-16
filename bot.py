import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from states import AddTransaction
from db import init_db, add_transaction, get_month_stats
from keyboards import categories_kb
from categories import INCOME_CATEGORIES, EXPENSE_CATEGORIES

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# СТАРТ
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "💰 Бот учёта финансов\n\n"
        "Команды:\n"
        "/income — добавить доход\n"
        "/expense — добавить расход\n"
        "/stats — статистика"
    )


# ДОХОД
@dp.message(Command("income"))
async def income_start(message: Message, state: FSMContext):
    await state.set_state(AddTransaction.amount)
    await state.update_data(type="income")
    await message.answer("Введите сумму дохода:")


# РАСХОД
@dp.message(Command("expense"))
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
        await message.answer("❗ Введите число")
        return

    data = await state.get_data()
    await state.update_data(amount=amount)

    if data["type"] == "income":
        kb = categories_kb(INCOME_CATEGORIES, "income")
    else:
        kb = categories_kb(EXPENSE_CATEGORIES, "expense")

    await state.set_state(AddTransaction.category)
    await message.answer("Выберите категорию:", reply_markup=kb)


# ВЫБОР КАТЕГОРИИ
@dp.callback_query(F.data.startswith("income") | F.data.startswith("expense"))
async def category_chosen(callback: CallbackQuery, state: FSMContext):
    _, category = callback.data.split(":")

    if category == "custom":
        await callback.message.answer("Введите свою категорию:")
        return

    data = await state.get_data()

    await add_transaction(
        user_id=callback.from_user.id,
        amount=data["amount"],
        category=category,
        type_=data["type"]
    )

    await callback.message.answer("✅ Записано!")
    await state.clear()
    await callback.answer()


# СВОЯ КАТЕГОРИЯ
@dp.message(AddTransaction.category)
async def custom_category(message: Message, state: FSMContext):
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
@dp.message(Command("stats"))
async def stats(message: Message):
    stats = await get_month_stats(message.from_user.id)

    await message.answer(
        f"📊 За месяц:\n\n"
        f"💰 Доходы: {stats['income']}\n"
        f"💸 Расходы: {stats['expense']}\n"
        f"📉 Баланс: {stats['income'] - stats['expense']}"
    )


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())