import os
from dotenv import load_dotenv

load_dotenv()


def database_url():
    """Функция получения URL БД из env"""
    db_url = os.getenv('DATABASE_URL')
    return db_url


def secret_key():
    """Функция получения секретного ключа из env"""
    key = os.getenv('SECRET_KEY')
    return key

