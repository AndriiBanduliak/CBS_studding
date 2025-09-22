import logging
import os
from logging.handlers import RotatingFileHandler

# Создаем директорию для логов, если она не существует
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логгера
def setup_logger():
    logger = logging.getLogger('blackjack')
    logger.setLevel(logging.INFO)
    
    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Обработчик для файла
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'blackjack.log'), 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем экземпляр логгера
logger = setup_logger()