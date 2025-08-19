from datetime import datetime

import psycopg2
import requests
from bs4 import BeautifulSoup
from flask import (
    flash,
    redirect,
    url_for,
)
from validators.url import url as is_url

from page_analyzer import db
from page_analyzer.logger import setup_logging

logger = setup_logging()

    
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
                SELECT 
                    u.id,
                    u.name,
                    uc.status_code,
                    uc.created_at as last_check_date
                FROM urls u
                LEFT JOIN LATERAL (
                    SELECT 
                        status_code,
                        created_at
                    FROM url_checks
                    WHERE url_id = u.id
                    ORDER BY created_at DESC, status_code DESC
                    LIMIT 1
                ) uc ON true
                ORDER BY u.id DESC
            """)
            return cur.fetchall()

    except Exception as e: # Указать конкртеный тип ошибки!!!
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
                SELECT 
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at 
                FROM url_checks 
                WHERE url_id = %s 
                ORDER BY id DESC
            """, (id,))
            checks = cur.fetchall()
            
            logger.info(f"Displaying URL id details={id}")
            return url, checks
                
    except psycopg2.OperationalError as e:
        logger.critical(f'Database connection error: {str(e)}')
    except Exception as e: # Указать конкртеный тип ошибки!!!
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
           
    except Exception as e: # Указать конкртеный тип ошибки!!!
        logger.exception(f"Error when working with the database: {str(e)}")
        flash('Произошла ошибка при добавлении URL', 'danger')
        return redirect(url_for('index'))
    
    return url_id


def check_urls(url_id):
    """Функция проверки URL с транзакцией"""
    try:
        cursor_ctx = db.get_cursor()
    except psycopg2.OperationalError as e:
        logger.critical(f'Database connection error: {str(e)}')
        return {
            'status': 'error',
            'message': 'Ошибка подключения к базе данных'
        }
    
    try:
        with cursor_ctx as (conn, cur):
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            url_record = cur.fetchone()

            if not url_record:
                logger.warning(f"URL with id={url_id} not found")
                return {'status': 'not_found', 'message': 'Страница не найдена'}

            url = url_record[0]

            try: # Подумать над тем где нужны блоки try а где нет!!!
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                status_code = response.status_code
                
                soup = BeautifulSoup(response.text, features='lxml')

                title_tag = soup.find('title') # Подумать как строки 170 - 190 перенести в отдельную функцию а здесь сделать итерацию
                if title_tag and title_tag.get_text(strip=True):
                    title_tag_text = title_tag.get_text(strip=True)
                else:
                    logger.warning("The <title> tag was not found on the URL")
                    title_tag_text = None

                h1_tag = soup.find("h1")
                if h1_tag and h1_tag.get_text(strip=True):
                    h1_tag_text = h1_tag.get_text(strip=True)
                else:
                    logger.warning("The <h1> tag was not found on the URL")
                    h1_tag_text = None

                meta_tag = soup.find('meta', attrs={"name": "description"})
                if meta_tag and meta_tag.get('content'):
                    content = meta_tag.get('content')
                else:
                    logger.warning(
                        "The <meta> tag with 'name=description'" 
                        "was not found on the URL"
                    )
                    content = None

                cur.execute("""
                    INSERT INTO url_checks 
                    (url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    url_id,
                    status_code,
                    h1_tag_text,
                    title_tag_text,
                    content,
                    datetime.now())
                )
                
                logger.info(f"Verification for URL {url_id} saved successfully")
                return {'status': 'success'}
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error to {url}: {str(e)}")
                return {
                    'status': 'error',
                    'message': 'Произошла ошибка при проверке'
                }

    except Exception as e: # Указать конкртеный тип ошибки!!!
        logger.exception(f"DB error when checking the URL: {str(e)}")
        if 'conn' in locals():
            return {'status': 'error', 'message': 'Внутренняя ошибка сервера'}


def validator(url):
    if not url:
        logger.warning("Empty URL")
        return {'valid': False, 'message': 'URL не может быть пустым'}
    
    if len(url) > 255:
        logger.warning(f"The URL is too long: {url}")
        return {'valid': False, 'message': 'URL превышает 255 символов'}
    
    try:
        if not is_url(url):
            logger.warning(f"Invalid URL: {url}")
            return {'valid': False, 'message': 'Некорректный URL'}
    except (ValueError, AttributeError, TypeError) as e:
        logger.error(f"Error during URL validation: {str(e)}")
        return None
    
    normalized_url = url.lower().strip()
    return {'valid': True, 'url': normalized_url, 'message': ''}