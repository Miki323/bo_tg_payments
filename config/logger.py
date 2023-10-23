import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter
import datetime

# Проверяем существование папки logging, если нет, создаем
log_folder = 'logging'
os.makedirs(log_folder, exist_ok=True)


# Определяем функцию для создания имени файла с учетом текущей даты
def get_log_filename():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    return os.path.join(log_folder, f'bot_log_{current_date}.log')


# Определяем обработчик для файла с ограничением на размер и кол-во файлов
log_file = get_log_filename()
file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=10, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Определяем форматтер для обработчика файла
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Определяем форматтер для обработчика потока вывода
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(ColoredFormatter(
    '%(log_color)s[%(asctime)s] - %(levelname)s: %(message)s',
    log_colors={
        'INFO': 'bold',
        'INFO_SUCCESS': 'green',
        'DEBUG': 'purple',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
))

# Создаем логгер и добавляем обработчики
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
