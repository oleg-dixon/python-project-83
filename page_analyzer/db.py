import os
import logging
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_connection():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info('Успешное подключение к базе данных!')
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f'Ошибка подключения к базе данных: {e}')
        raise
    finally:
        if conn:
            logger.info('Соединение с базой данных закрыто!')
            conn.close()
