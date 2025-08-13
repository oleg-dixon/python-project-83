import logging
from datetime import datetime

import psycopg2
from flask import (
    flash,
    redirect,
    url_for,
)
from validators.url import url as is_url

from page_analyzer import db

logger = logging.getLogger(__name__)

    
def get_urls():
    """Функция получения списка URL из базы данных"""
    try:
        cursor_ctx = db.get_cursor()
    except psycopg2.OperationalError:
        logger.critical('Database connection error!')
        flash('Ошибка подключения к базе данных', 'danger')
        return []

    try:
        with cursor_ctx as (conn, cur):
            cur.execute("""
                SELECT urls.id,
                       urls.name,
                       MAX(url_checks.created_at) AS last_check,
                       MAX(url_checks.status_code) AS status_code
                FROM urls
                LEFT JOIN url_checks
                  ON urls.id = url_checks.url_id
                GROUP BY urls.id, urls.name
                ORDER BY urls.id;
            """)
            urls = cur.fetchall()
            return urls

    except Exception as e:
        logger.exception(f"Error when getting the URL list: {e}")
        flash('Произошла ошибка при загрузке списка сайтов', 'danger')
        return []


def get_url_detail(id):
    """Функция получения детальной информации о URL"""
    try:
        cursor_ctx = db.get_cursor()
    except psycopg2.OperationalError:
        logger.critical('Database connection error!')
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))

    try:
        with cursor_ctx as (conn, cur):
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            url = cur.fetchone()
            
            if not url:
                logger.warning(f"URL with id={id} not found")
                return None
            
            cur.execute("""
                SELECT id, status_code, created_at 
                FROM url_checks 
                WHERE url_id = %s 
                ORDER BY id ASC
            """, (id,))
            checks = cur.fetchall()
            
            logger.info(f"Displaying URL id details={id}")
            return url, checks
                
    except psycopg2.OperationalError as e:
        logger.critical(f'Database connection error: {str(e)}')
    except Exception as e:
        logger.exception(f"Error processing URL id={id}: {str(e)}")
    
    return None


def add_new_url(url):
    """Функция добавления нового URL"""
    try:
        cursor_ctx = db.get_cursor()
    except psycopg2.OperationalError:
        logger.critical('Database connection error!')
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))
    
    url_id = None

    try:
        with cursor_ctx as (conn, cur):
            cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
            existing_url = cur.fetchone()

            if existing_url:
                url_id = existing_url[0]
                logger.info(
                    f"The URL already exists in the database, id={url_id}"
                    )
                flash('Страница уже существует', 'info')
            else:
                cur.execute("""
                    INSERT INTO urls (name, created_at) 
                    VALUES (%s, %s) 
                    RETURNING id
                """, (url, datetime.now()))
                url_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"URL successfully added, id={url_id}")
                flash('Страница успешно добавлена!', 'success')
           
    except Exception as e:
        logger.exception(f"Error when working with the database: {str(e)}")
        flash('Произошла ошибка при добавлении URL', 'danger')
        return redirect(url_for('index'))
    
    return url_id


def check_urls(id):   
    """Функция проверки URL с транзакцией"""
    try:
        cursor_ctx = db.get_cursor()
    except psycopg2.OperationalError:
        logger.critical('Database connection error!')
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('index'))
    
    try:
        with cursor_ctx as (conn, cur):
            cur.execute("SELECT name FROM urls WHERE id = %s", (id,))
            url_record = cur.fetchone()

            if not url_record:
                flash('Страница не найдена', 'danger')
                return redirect(url_for('index'))

            # Здесь логика проверки URL
            _ = 200  # заглушка переменная status_code

            cur.execute("""
                INSERT INTO url_checks (url_id, created_at)
                VALUES (%s, %s)
            """, (id, datetime.now()))

            flash('Страница успешно проверена', 'success')

        return redirect(url_for('url_detail', id=id))

    except psycopg2.OperationalError:
        flash('Ошибка подключения к базе данных', 'danger')
    except Exception as e:
        logger.exception(e)
        flash('Ошибка при проверке страницы', 'danger')

    return redirect(url_for('url_detail', id=id))


def validator(url):
    if not url:
        logger.warning("Пустой URL")
        return {'valid': False, 'message': 'URL не может быть пустым'}
    
    if len(url) > 255:
        logger.warning(f"Слишком длинный URL: {url}")
        return {'valid': False, 'message': 'URL превышает 255 символов'}
    
    try:
        if not is_url(url):
            logger.warning(f"Некорректный URL: {url}")
            return {'valid': False, 'message': 'Некорректный URL'}
    except Exception as e:
        logger.error(f"Ошибка при валидации URL: {str(e)}")
        return None
    
    normalized_url = url.lower().strip()
    return {'valid': True, 'url': normalized_url, 'message': ''}