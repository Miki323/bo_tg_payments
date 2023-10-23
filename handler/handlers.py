import json
import os
import time
import aiohttp
from config.logger import logger
from config.types import Message
from typing import Dict, Any, Optional, List
from db import Database
from handler.payment import PaymentProcessor


class CommandHandler:
    """
    Обработчик команд для бота.
    """

    def __init__(self, bot: Any) -> None:
        """
        Инициализация объекта CommandHandler.

        Параметры:
        - bot (Any): Объект бота, к которому привязан обработчик.
        """
        self.bot = bot
        self.db = Database('database.db')
        self.payment_processor: PaymentProcessor = PaymentProcessor()
        self.base_url: str = os.getenv('BASE_URL')
        self.commands: Dict[str, Any] = {
            "/start": self.send_initial_menu,
            "/help": self.send_help_command,
            "Мой профиль": self.send_profile_menu,
            "Оплатить подписку": self.send_payment_menu,
            "История платежей": self.send_payment_history,
            "Отписаться от бота": self.unsubscribe_user,
            "Главное меню": self.restart_bot,
            "Другие функции": self.send_other_features_menu
        }

    async def handle_command(self, message: Message) -> None:
        """
        Обработка команды из сообщения.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        command: str = message.content
        if command.startswith("Тариф"):
            await self.handle_payment_selection(message)
        else:
            handler: Any = self.commands.get(command, self.send_unknown_command_message)
            await handler(message)  # Всегда передаем объект message в обработчике команды

    @staticmethod
    async def send_message(message: Message) -> bool:
        """
        Отправляет сообщение через API Telegram.

        Параметры:
        - message (Message): Объект сообщения, содержащий chat_id и text.

        Возвращает:
        - bool: True, если сообщение успешно отправлено, False в противном случае.
        """
        try:
            async with aiohttp.ClientSession() as session:
                data: Dict[str, Any] = {
                    'chat_id': message.chat_id,
                    'text': message.content,
                }
                if message.reply_markup:
                    data['reply_markup'] = json.dumps(message.reply_markup)
                if message.parse_mode:
                    data['parse_mode'] = message.parse_mode
                async with session.post(os.getenv('SEND_MESSAGE'), data=data) as response:
                    if response.status == 200:
                        return True
                    else:
                        # Если не удалось отправить сообщение, записываем ошибку в логи
                        logger.error(f"Failed to send message: {response.status}")
                        return False
        except Exception as e:
            # Обрабатываем возможные ошибки при отправке сообщения
            logger.error(f"Error occurred while sending message: {e}")
            return False

    async def send_unknown_command_message(self, message: Message) -> None:
        """
        Обработчик для случая, когда пользователь вводит неизвестную команду.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        response_text: str = "Извините, не могу понять вашу команду. Пожалуйста, попробуйте другую команду."
        response_message: Message = Message(chat_id=message.chat_id, content=response_text)
        await self.send_message(response_message)

    async def send_initial_menu(self, message: Message) -> None:
        """
        Отправляет начальное меню пользователю с информацией о боте.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        username: Optional[str] = message.username
        chat_id: int = message.chat_id
        menu_buttons: List[List[Dict[str, str]]] = [
            [{"text": "Мой профиль"}],
            [{"text": "Оплатить подписку"}, {"text": "История платежей"}],
            [{"text": "Отписаться от бота"}],
            [{"text": "Другие функции"}]
        ]

        menu_button_rows: List[List[Dict[str, str]]] = []
        for row in menu_buttons:
            button_row: List[Dict[str, str]] = []
            for button in row:
                button_row.append({"text": button["text"]})
            menu_button_rows.append(button_row)

        menu: Dict[str, Any] = {
            "keyboard": menu_button_rows,
            "resize_keyboard": True
        }

        # Текст приветствия с информацией о боте
        hello_text: str = f'Привет, {username}!\n\nЯ - ваш персональный бот. Вот что я могу:\n\n' \
                          '- Показать ваш профиль\n' \
                          '- Помочь вам с оплатой подписки\n' \
                          '- Показать историю ваших платежей по подпискам\n' \
                          '- И многое другое (в разработке)'

        # Создаем объект Message с текстом приветствия и клавиатурой меню
        menu_message: Message = Message(chat_id=chat_id, content=hello_text, reply_markup=menu)
        await self.send_message(menu_message)

    async def send_help_command(self, message: Message) -> None:
        """
        Отправляет справочную информацию о командах бота в HTML-разметке.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        help_text = """
        <b>Справочная информация о командах бота</b>

        Команда <code>/help</code> выводит справочную информацию о доступных командах бота и их использовании.

        <b>Доступные команды:</b>

        1. <i>Мой профиль:</i> Просмотреть информацию о своем профиле.
        2. <i>Оплатить подписку:</i> Перейти к оплате подписки на сервис.
        3. <i>История платежей:</i> Просмотреть историю всех прошлых платежей.
        4. <i>Отписаться от бота:</i> Отменить подписку и отписаться от бота.
        5. <i>Перезапустить бота:</i> Перезапустить бота, если возникли проблемы.
        6. <i>Другие функции:</i> Посмотреть другие доступные функции (в разработке).

        <b>Примеры использования:</b>

        - <code>/start</code>: Начать взаимодействие с ботом и открыть главное меню.
        - <code>/help</code>: Просмотреть это сообщение со справочной информацией.
        - "Мой профиль": Посмотреть свою персональную информацию.

        Обратите внимание, что некоторые функции могут находиться в 
        разработке и будут доступны в будущих обновлениях бота.
        """

        # Создаем объект Message с текстом справочной информации и указанием HTML-разметки
        help_message = Message(chat_id=message.chat_id, content=help_text, parse_mode="HTML")
        # Отправляем сообщение справочной информации
        await self.send_message(help_message)

    async def send_profile_menu(self, message: Message) -> None:
        """
        Отправляет меню профиля пользователю.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        response_text: str = "Это меню профиля. В разработке."
        response_message: Message = Message(chat_id=message.chat_id, content=response_text)
        await self.send_message(response_message)

    async def send_payment_history(self, message: Message) -> None:
        """
        Отправляет историю платежей пользователю.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        response_text: str = "Это история платежей. В разработке."
        response_message: Message = Message(chat_id=message.chat_id, content=response_text)
        await self.send_message(response_message)

    async def unsubscribe_user(self, message: Message) -> None:
        """
        Отписывает пользователя от бота.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        response_text: str = "Отписка от бота. В разработке."
        response_message: Message = Message(chat_id=message.chat_id, content=response_text)
        await self.send_message(response_message)

    async def restart_bot(self, message: Message) -> None:
        """
        Перезапускает бота.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """

        # Отправляем приветственное сообщение и вернем пользователя к начальному меню
        await self.send_initial_menu(message)

    async def send_other_features_menu(self, message: Message) -> None:
        """
        Отправляет меню других функций пользователю.

        Параметры:
        - message (Message): Объект сообщения, содержащий информацию о чате и тексте сообщения.
        """
        # Отправляем приветственное сообщение и вернем пользователя к начальному меню
        await self.send_initial_menu(message)

    async def send_payment_menu(self, message: Message) -> None:
        """
        Отправляет меню оплаты подписки пользователю.

        Параметры:
        - message (Message): Объект сообщения пользователя.

        Возвращает:
        - None
        """
        try:
            # Отправляем приветственное сообщение и предлагаем выбрать тариф
            response_message = "Добро пожаловать! Выберите тариф для оплаты."
            reply_markup = {
                "keyboard": [
                    [{"text": "Тариф 1: 1000 RUB", "callback_data": "Тариф 1"}],
                    [{"text": "Тариф 2: 2000 RUB", "callback_data": "Тариф 2"}],
                    [{"text": "Тариф 3: 3000 RUB", "callback_data": "Тариф 3"}],
                    [{"text": "Главное меню", "callback_data": "Тариф 3"}]
                ],
                'resize_keyboard': True
            }
            msg = Message(chat_id=message.chat_id, content=response_message, reply_markup=reply_markup)
            await self.send_message(msg)
        except Exception as e:
            logger.error(e)

    async def handle_payment_selection(self, message: Message) -> None:
        """
        Обрабатывает выбор тарифа для оплаты, и отправляет счет на оплату.

        Параметры:
        - message (Message): Объект сообщения с выбором тарифа.

        Возвращает:
        - None
        """
        try:
            # Извлекаем выбранный тариф из сообщения
            selected_tariff = message.content.split(":")[0].strip()
            price = 0
            # Определяем цену в зависимости от выбранного тарифа
            if selected_tariff == 'Тариф 1':
                price = 1000
            elif selected_tariff == 'Тариф 2':
                price = 2000
            elif selected_tariff == 'Тариф 3':
                price = 3000

            # Создаем платеж и получаем ссылку для оплаты
            confirmation_url, order_id = await self.payment_processor.create_payment(
                value=str(price),
                currency="RUB",
                description=f"Оплата подписки на тариф '{selected_tariff}'"
            )

            # Сохраняем информацию о заказе в базе данных со статусом 'pending'
            self.db.insert_order(message.user_id, selected_tariff, 'pending')

            # Создаем кнопку оплаты с полученной ссылкой
            reply_markup: Dict[str, Any] = {
                "inline_keyboard": [[{"text": "Оплатить", "url": confirmation_url}]]
            }

            # Отправляем сообщение с кнопкой оплаты пользователю
            response_message = f"Оплатите подписку на тариф '{selected_tariff}'\n" \
                               f"После оплаты, платеж будет обработан в течении 10 минут\n" \
                               f"Спасибо!"
            msg = Message(chat_id=message.chat_id, content=response_message, reply_markup=reply_markup)
            await self.send_message(msg)

            # Ждем (60 секунд)
            time.sleep(30)
            order_status = self.payment_processor.get_payment_info(order_id)
            print(order_status)

            # Определяем сообщение в зависимости от статуса оплаты
            if order_status.get('paid', True):
                response_message = f'Ваш ID: {order_id}\n' \
                                   f'Спасибо за подписку на HRbot!'
            else:
                response_message = "Платеж не подтвержден. Пожалуйста, проверьте статус оплаты позже."

            # Отправляем сообщение пользователю
            msg = Message(chat_id=message.chat_id, content=response_message)
            await self.send_message(msg)

        except Exception as e:
            # Обрабатываем возможные ошибки и записываем их в логи
            logger.error(f"Error occurred while handling payment selection: {e}")

    async def handle_payment_info(self, message: Message) -> None:
        """
        Обрабатывает запрос пользователя о состоянии платежа.

        Параметры:
        - message (Message): Объект сообщения пользователя.

        Возвращает:
        - None
        """
        try:
            payment_id = message.content.split(":")[1].strip()  # Получаем идентификатор платежа из сообщения
            payment_info = self.payment_processor.get_payment_info(payment_id)
            response_message = f"Информация о платеже:\n{payment_info}"
            msg = Message(chat_id=message.chat_id, content=response_message)
            await self.send_message(msg)
        except Exception as e:
            logger.error(e)

    @staticmethod
    async def delete_message(chat_id, message_id):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(f'{os.getenv("DELETE_MESSAGE")}',
                                              json={'chat_id': chat_id, 'message_id': message_id})
                data = await response.json()
                if data.get('ok'):
                    logger.info('Last message deleted successfully.')
                else:
                    logger.error('Failed to delete last message.')
        except Exception as e:
            logger.error(f'Error occurred: {e}')
