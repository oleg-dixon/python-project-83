import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Функция настройки базовой конфигурации логирования 
    для всего проекта
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = RotatingFileHandler(
        'py_log.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if not any(
        isinstance(h, RotatingFileHandler)
        and h.baseFilename == file_handler.baseFilename
        for h in root_logger.handlers
    ):
        root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)
