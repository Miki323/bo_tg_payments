import time
import aiohttp
import asyncio
import requests
from aiohttp import web
from dotenv import load_dotenv
from pyngrok import ngrok
from config.types import Message
from config.logger import logger
from handler.handlers import CommandHandler
import os

# Загружаем переменные окружения из файла .env
load_dotenv()


class HrBot:
    def __init__(self, message: Message):

        """
        Инициализирует объект бота.

        Параметры:
        message (Message): Объект сообщения, который содержит начальные данные для бота.
        """
        self.base_url = os.getenv('BASE_URL')
        self.offset = None
        self.command_handler = CommandHandler(bot=self)  # Передаем ссылку на самого себя (бота) в CommandHandler
        self.message = message

    async def get_updates(self) -> list:
        """
        Получает обновления от сервера Telegram.

        Возвращает:
        list: Список обновлений (сообщений и других событий) от сервера Telegram.
        """
        params = {
            'timeout': 30
        }
        if self.offset is not None:
            params['offset'] = self.offset

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/getUpdates", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        updates = data.get('result', [])
                        if updates:
                            self.offset = updates[-1]['update_id'] + 1
                            logger.info(updates)
                        return updates
                    else:
                        logger.error(f"Failed to get updates: {response.status}")
            except Exception as e:
                logger.error(f"Error occurred while getting updates: {e}")
        return []

    async def handle_updates(self, updates: list):
        """
        Обрабатывает полученные обновления от сервера Telegram.

        Параметры:
        updates (list): Список обновлений от сервера Telegram.
        """
        for update in updates:
            message_obj = update.get('message')
            if message_obj:
                chat_id = message_obj['chat']['id']
                message_id = message_obj['message_id']
                text = message_obj.get('text', 'No text')
                user_id = message_obj['from']['id']
                username = message_obj['from'].get('username', 'No username')

                # Создаем объект Message
                message = Message(bot=self, chat_id=chat_id, message_id=message_id,
                                  content=text, username=username, timestamp=int(time.time()))

                # Логируем полученные данные
                logger.info(
                    f" Received message from user {username} {user_id} in chat {chat_id}."
                    f" Message ID: {message_id}. Message text: {text}")

                # Передаем объект сообщения в обработчике команд
                await self.command_handler.handle_command(message)

    async def start_polling(self):
        """
        Запускает бота и начинает ожидание обновлений от сервера Telegram.
        """
        logger.info("Bot started polling for updates...")
        while True:
            try:
                updates = await self.get_updates()
                if updates:
                    await self.handle_updates(updates)
            except Exception as e:
                logger.error(f"Error occurred: {e}")
            await asyncio.sleep(1)

    async def handle_webhook(self, request):
        """
        Обрабатывает входящие запросы от сервера Telegram (webhook).

        Параметры:
        request: Объект запроса от сервера Telegram.

        Возвращает:
        web.Response: Ответ сервера.
        """
        data = await request.json()  # Получаем данные из входящего запроса

        if 'message' in data:
            logger.error(data)
            # Обрабатываем обновление сообщения
            await self.handle_updates([data])
            return web.Response()
        else:
            logger.error(f"Error response {data}")
            return web.Response()

    @staticmethod
    async def start_webhook():
        """
        Настраивает и запускает вебхук для получения обновлений от сервера Telegram.
        """
        # Закрываем все активные сеансы ngrok
        ngrok.kill()

        # Запуск ngrok
        ngrok_process = ngrok.connect('3000')
        # logger.info(ngrok_process)

        # Ждем, пока ngrok будет готов
        ngrok_url = ngrok_process.public_url

        # Устанавливаем вебхук через API Telegram
        webhook_url = f"{ngrok_url}/webhook"
        api_url = f"{os.getenv('SET_WEBHOOK_URL')}?url={webhook_url}"

        try:
            response = requests.get(api_url)
            response_data = response.json()
            if response_data.get('ok'):
                logger.info(f"Webhook successfully set up. URL: {webhook_url}")
            else:
                logger.error(f"Failed to set up webhook. Telegram API response: {response_data}")
        except Exception as e:
            logger.error(f"Error occurred while setting up webhook: {e}")
