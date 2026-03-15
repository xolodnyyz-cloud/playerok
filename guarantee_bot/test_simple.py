from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🔍 Тестовый бот работает!\n\nОтправь /menu")

@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer(
        "💰 **Создание сделки с оплатой на карту**\n\n"
        "🏦 **Получатель карты**\n"
        "Укажите свой @username\n\n"
        "Введите @username получателя:",
        parse_mode="Markdown"
    )

async def main():
    print("✅ Тестовый бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())