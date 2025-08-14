import os
import logging

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer import utils
from page_analyzer.logger import setup_logging

logger = setup_logging()

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    """
    Обработчик для главной страницы с формой добалвения URL
    """
    logger.info('Home Page Request')
    return render_template(
        'index.html',
    )


@app.route('/urls', methods=['GET'])
def urls():
    """Обработчик для вывода списка всех URL"""
    urls = utils.get_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>')
def url_detail(id):
    """Обработчик для детальной информации о URL"""
    url_data = utils.get_url_detail(id)
    if not url_data:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('index'))
    
    url, checks = url_data
    return render_template(
        'url_detail.html',
        url=url,
        checks=checks
        )
    

@app.route('/add', methods=['POST'])
def add_url():
    """Обработчик добавления URL"""
    url = request.form.get('url', '').strip()
    logger.info(f"Попытка добавления URL: {url}")
    
    validation_result = utils.validator(url)
    if validation_result is None or not validation_result.get('valid'):
        message = (
        validation_result.get('message', 'Некорректный URL')
        if validation_result
        else 'Ошибка валидации URL'
        )
        flash(message, 'danger')
        return redirect(url_for('index'))
    
    url_id = utils.add_new_url(validation_result['url'])
    if url_id is None:
        flash('Произошла ошибка при добавлении URL', 'danger')
        return redirect(url_for('index'))
    
    return redirect(url_for('url_detail', id=url_id))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    """Обработчик проверки URL"""
    result = utils.check_urls(id)
    
    if result['status'] == 'success':
        flash('Страница успешно проверена', 'success')
    elif result['status'] == 'not_found':
        flash(result['message'], 'danger')
        return redirect(url_for('index'))
    else:
        flash(result.get('message', 'Произошла ошибка при проверке'), 'danger')
    
    return redirect(url_for('url_detail', id=id))


@app.template_filter('strftime')
def format_datetime(value, format='%Y-%m-%d'):
    """Фильтр для форматирования даты в шаблонах"""
    if value is None:
        return ''
    return value.strftime(format)
