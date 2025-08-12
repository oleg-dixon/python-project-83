import os
import logging
import psycopg2 

from datetime import datetime
from dotenv import load_dotenv
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    flash,
)
from page_analyzer import db
from validators.url import url as is_url

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

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    """
    Главная страница с формой добалвения URL
    """
    logger.info('Запрос главной страницы')
    return render_template(
        'index.html',
    )


@app.route('/urls', methods=['GET'])
def urls():
    """Страница со списком всех URL"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, created_at 
                FROM urls 
                ORDER BY created_at DESC
            """)
            urls = cur.fetchall()
            logger.info(f"Получено {len(urls)} URL из базы данных")
        return render_template('urls.html', urls=urls)
    except Exception as e:
        logger.error(f"Ошибка при получении списка URL: {e}")
        flash('Произошла ошибка при загрузке списка сайтов', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:id>')
def url_detail(id):
    """Страница с детальной информацией о URL"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cur:
            # Получаем информацию о URL
            cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
            url = cur.fetchone()
            
            if not url:
                logger.warning(f"URL с id={id} не найден")
                flash('Страница не найдена', 'danger')
                return redirect(url_for('index'))

            # Получаем проверки для этого URL
            cur.execute("""
                SELECT id, status_code, created_at 
                FROM url_checks 
                WHERE url_id = %s 
                ORDER BY id DESC
            """, (id,))
            checks = cur.fetchall()
            
            logger.info(f"Отображение деталей URL id={id}")
            return render_template('url_detail.html', url=url, checks=checks)
    except Exception as e:
        logger.error(f"Ошибка при загрузке деталей URL id={id}: {e}")
        flash('Произошла ошибка при загрузке страницы', 'danger')
        return redirect(url_for('index'))
    

@app.route('/add', methods=['POST'])
def add_url():
    url = request.form.get('url', '').strip()
    logger.info(f"Попытка добавления URL: {url}")

    # Валидация URL
    if not url:
        logger.warning("Пустой URL")
        flash('URL не может быть пустым', 'danger')
        return redirect(url_for('index'))
    
    if not is_url(url):
        logger.warning(f"Некорректный URL: {url}")
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index'))
    
    if len(url) > 255:
        logger.warning(f"URL превышает 255 символов: {url}")
        flash('URL превышает 255 символов', 'danger')
        return redirect(url_for('index'))

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Проверяем существование URL
                cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
                existing_url = cur.fetchone()
                
                if existing_url:
                    url_id = existing_url[0]
                    logger.info(f"URL уже существует в базе, id={url_id}")
                    flash('Страница уже существует', 'info')
                else:
                    # Добавляем новый URL
                    cur.execute("""
                        INSERT INTO urls (name, created_at) 
                        VALUES (%s, %s) 
                        RETURNING id
                    """, (url, datetime.now()))
                    url_id = cur.fetchone()[0]
                    conn.commit()
                    logger.info(f"URL успешно добавлен, id={url_id}")
                    flash('Страница успешно добавлена', 'success')
                
                return redirect(url_for('url_detail', id=url_id))
                
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {str(e)}")
        flash('Произошла ошибка при добавлении URL', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    logger.info(f"Запуск проверки для URL id={id}")
    
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Получаем URL из базы
                cur.execute("SELECT name FROM urls WHERE id = %s", (id,))
                url_record = cur.fetchone()
                
                if not url_record:
                    logger.error(f"URL с id={id} не найден")
                    flash('Страница не найдена', 'danger')
                    return redirect(url_for('index'))
                
                url = url_record[0]
                
                try:
                    # Здесь реализация проверки URL (requests/BeautifulSoup)
                    # Пример:
                    status_code = 200  # Заглушка для примера
                    
                    cur.execute("""
                        INSERT INTO url_checks (url_id, status_code, created_at)
                        VALUES (%s, %s, %s)
                    """, (id, status_code, datetime.now()))
                    conn.commit()
                    
                    flash('Страница успешно проверена', 'success')
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Ошибка проверки URL: {str(e)}")
                    flash('Ошибка при проверке страницы', 'danger')
                
                return redirect(url_for('url_detail', id=id))
                
    except Exception as e:
        logger.error(f"Ошибка БД при проверке URL: {str(e)}")
        flash('Ошибка при сохранении результатов проверки', 'danger')
        return redirect(url_for('url_detail', id=id))
    

if __name__ == '__main__':
    app.run(debug=True)


