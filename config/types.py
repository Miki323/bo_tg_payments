import json


class Message:
    def __init__(self, bot: any = None, chat_id: int = None, message_id: int = None, direction: str = None,
                 content_type: str = None, content: any = None, username: str = None, command: str = None,
                 user_id: int = None, timestamp: int = None, chat_title: str = None, user_location: dict = None,
                 reply_markup: dict = None, parse_mode: str = None, ):
        """
        Инициализирует объект сообщения с указанными атрибутами.

        Параметры:
        bot: Объект бота (по умолчанию None).
        chat_id (int, optional): Уникальный идентификатор чата (по умолчанию None).
        message_id (int, optional): Уникальный идентификатор сообщения (по умолчанию None).
        direction (str, optional): Направление сообщения ('incoming' или 'outgoing') (по умолчанию None).
        content_type (str, optional): Тип содержимого сообщения (например, 'text', 'image', 'audio', и т.д.) (по умолчанию None).
        content (any, optional): Содержимое сообщения (по умолчанию None).
        username (str, optional): Имя пользователя, связанное с сообщением (по умолчанию None).
        command (str): Команда, которую необходимо обработать (по умолчанию None).
        user_id (int, optional): Уникальный идентификатор пользователя (по умолчанию None).
        timestamp (int, optional): Временная метка сообщения (по умолчанию None).
        chat_title (str, optional): Название чата (по умолчанию None).
        user_location (dict, optional): Геолокационные данные пользователя (по умолчанию None).
        reply_markup (dict, optional): Дополнительная информация для настройки клавиатуры (по умолчанию None).
        parse_mode (str, optional): Режим парсинга для форматирования текста сообщения. Допустимые значения:
            'Markdown', 'MarkdownV2', 'HTML'. (по умолчанию None)
        """
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.direction = direction
        self.content_type = content_type
        self.content = content
        self.username = username
        self.command = command
        self.user_id = user_id
        self.timestamp = timestamp
        self.chat_title = chat_title
        self.user_location = user_location
        self.reply_markup = reply_markup
        self.parse_mode = parse_mode

    def to_json(self):
        """
        Преобразует объект сообщения в формат JSON.

        Возвращает:
        str: Сообщение в формате JSON.
        """
        message_json = {
            'chat_id': self.chat_id,
            'message_id': self.message_id,
            'content_type': self.content_type,
            'content': self.content,
            'bot': self.bot,
            'direction': self.direction,
            'username': self.username,
            'command': self.command,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'chat_title': self.chat_title,
            'user_location': self.user_location,
            'reply_markup': self.reply_markup,
            'parse_mode': self.parse_mode
        }

        return json.dumps(message_json)

    @classmethod
    def from_json(cls, json_data):
        """
        Создает объект сообщения из данных в формате JSON.

        Параметры:
        json_data (str): Строка JSON с данными сообщения.

        Возвращает:
        Message: Объект сообщения.
        """
        data = json.loads(json_data)
        return cls(
            bot=data.get('bot'),
            chat_id=data.get('chat_id'),
            message_id=data.get('message_id'),
            direction=data.get('direction'),
            content_type=data.get('content_type'),
            content=data.get('content'),
            username=data.get('username'),
            command=data.get('command'),
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp'),
            chat_title=data.get('chat_title'),
            user_location=data.get('user_location'),
            reply_markup=data.get('reply_markup'),
            parse_mode=data.get('parse_mode')
        )
