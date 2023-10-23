import os
from typing import Dict, Any, Tuple
import uuid
from dotenv import load_dotenv
from yookassa import Refund, Configuration, Payment

from config.logger import logger

load_dotenv()


class PaymentProcessor:
    def __init__(self):
        # Инициализация параметров магазина из переменных окружения
        self.shop_id = Configuration.account_id = os.getenv('ACCOUNT_ID')
        self.secret_key = Configuration.secret_key = os.getenv('SECRET_KEY')
        self.bot_token = os.getenv('BOT_TOKEN')

    @staticmethod
    async def create_payment(value: str, currency: str, description: str) -> Tuple[str, str]:
        """
        Создает платеж и возвращает ссылку для переадресации и уникальный идентификатор заказа.

        Параметры:
        - value (str): Сумма платежа в формате строки, например, "100.00".
        - currency (str): Валюта платежа, например, "RUB".
        - description (str): Описание платежа.

        Возвращает:
        - tuple: Ссылка для переадресации и уникальный идентификатор заказа.
        """
        Configuration.account_id = os.getenv('ACCOUNT_ID')
        Configuration.secret_key = os.getenv('SECRET_KEY')
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {
                "value": value,
                "currency": currency
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/test_miki323_payment_bot"
            },
            "description": description
        }, idempotence_key)

        # Получаем URL для переадресации и извлекаем идентификатор заказа из параметров URL
        confirmation_url = payment.confirmation.confirmation_url
        query_string = confirmation_url.split("?")[1]
        parameters = query_string.split("&")
        parameters_dict = {}
        for param in parameters:
            key, value = param.split("=")
            parameters_dict[key] = value
        order_id = parameters_dict.get("orderId")

        # Возвращаем URL и уникальный идентификатор заказа
        return confirmation_url, order_id

    @staticmethod
    def get_payment_info(payment_id: str) -> Dict[str, Any]:
        """
        Получает информацию о платеже по его уникальному идентификатору.

        Параметры:
        - payment_id (str): Уникальный идентификатор платежа.

        Возвращает:
        - dict: Информация о платеже в форме словаря.
        """
        try:
            payment_info = Payment.find_one(payment_id).confirmation
            return payment_info
        except Exception as e:
            # Обрабатываем возможные ошибки при поиске платежа
            logger.error(f"Error occurred while fetching payment information: {e}")
            return {}  # Возвращаем пустой словарь в случае ошибки

    @staticmethod
    async def capture_payment(payment_id: str, amount: str = None) -> None:
        """
        Подтверждает оплату платежа.

        Параметры:
        - payment_id (str): Уникальный идентификатор платежа.
        - amount (str): Сумма платежа, если она отличается от изначальной.

        Возвращает:
        - None
        """
        pass

    @staticmethod
    async def cancel_payment(payment_id: str) -> None:
        """
        Отменяет платеж по его уникальному идентификатору.

        Параметры:
        - payment_id (str): Уникальный идентификатор платежа.

        Возвращает:
        - None
        """
        pass

    @staticmethod
    async def create_refund(payment_id: str, value: str, currency: str) -> Dict[str, Any]:
        """
        Создает запрос на возврат средств для определенного платежа.

        Параметры:
        - payment_id (str): Уникальный идентификатор платежа.
        - value (str): Сумма возврата в формате строки, например, "100.00".
        - currency (str): Валюта возврата, например, "RUB".

        Возвращает:
        - dict: Информация о возврате в форме словаря.
        """
        refund = Refund.create({
            "amount": {
                "value": value,
                "currency": currency
            },
            "payment_id": payment_id
        })
        return refund.json()
