from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor

from page_analyzer.utils.config import database_url
from page_analyzer.utils.logger import setup_logging

logger = setup_logging()

DATABASE_URL = database_url()


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
            except psycopg2.OperationalError:
                conn.rollback()
                raise

    except psycopg2.OperationalError as e:
        logger.error(f'Database connection error: {e}')
        raise

    finally:
        if conn:
            conn.close()
            logger.info('The database connection is closed!')

