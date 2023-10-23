import asyncio
from aiohttp import web
from config.logger import logger
from bot.hrbot import HrBot
from config.types import Message


async def run_bot():
    message = Message()
    bot = HrBot(message)
    app = web.Application()
    app.router.add_post('/webhook', bot.handle_webhook)  # Устанавливаем обработчик POST запросов на /webhook

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    await site.start()

    logger.info("Webhook started. Listening for updates...")
    await bot.start_webhook()
    # Бесконечный цикл для продолжения работы сервера
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
