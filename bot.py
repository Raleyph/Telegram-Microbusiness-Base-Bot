from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import main_menu, clients, records, analytics, expenses

import asyncio
import config as cfg


async def main():
    bot = Bot(token=cfg.token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(main_menu.router)
    dp.include_router(clients.router)
    dp.include_router(records.router)
    dp.include_router(analytics.router)
    dp.include_router(expenses.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
