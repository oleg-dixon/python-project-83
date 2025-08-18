import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

from page_analyzer.logger import setup_logging

logger = setup_logging()

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def get_cursor():
    """Функция подключения к БД"""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info('Successful connection to the database!')

        with conn.cursor(cursor_factory=DictCursor) as cur:
            try:
                yield conn, cur
                conn.commit()
            except Exception as e: # Указать какая именно ошибка должна выводится psycopg2 типа OperationalError!!!
                conn.rollback()
                raise

    except psycopg2.OperationalError as e:
        logger.error(f'Database connection error: {e}')
        raise

    finally:
        if conn:
            conn.close()
            logger.info('The database connection is closed!')

