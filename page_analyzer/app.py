import os
import psycopg2

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

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
    )


@app.route('/add', methods=['POST'])
def add_url():
    url = request.form['url'].strip()

    if not url:
        flash('The URL cannot be empty', 'danger')
        return redirect(url_for('index'))
    
    errors = validate_url(url)
    if errors:
        flash('An error has occurred! The site has not been added!')
        return render_template(
            'index.html',
            url=url,
            errors=errors
        ), 422
        

    with db.get_connection() as curs:
        curs.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
        db.get_connection.commit()
        flash('The site has been added!')
    
    return redirect(url_for('index'))


def validate_url(url):
    errors = {}
    if not is_url(url) or len(url) > 255:
        errors['name'] = 'URL is Invalid '
    return errors


