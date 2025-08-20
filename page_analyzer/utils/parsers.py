from bs4 import BeautifulSoup as bs

from page_analyzer.utils.logger import setup_logging

logger = setup_logging()


def parser(response):
    """Функция для парсера"""
    soup = bs(response.text, features='lxml')
    return soup


def get_status_code(response):
    """Функция получения кода ответа"""
    response.raise_for_status()
    status_code = response.status_code
    return status_code


def get_h1_tag(response):
    """Функция получения тега <h1>"""
    h1_tag = parser(response).find('h1')
    if h1_tag and h1_tag.get_text(strip=True):
        h1_tag_text = h1_tag.get_text(strip=True)
    else:
        logger.warning("The <h1> tag was not found on the URL")
        h1_tag_text = None
    return h1_tag_text


def get_title_tag(response):
    """Функция получения тега <title>"""
    title_tag = parser(response).find('title')  
    if title_tag and title_tag.get_text(strip=True):
        title_tag_text = title_tag.get_text(strip=True)
    else:
        logger.warning("The <title> tag was not found on the URL")
        title_tag_text = None
    return title_tag_text


def get_meta_tag(response):
    """
    Функция получения тега <meta>
    и name=description
    """
    meta_tag = parser(response).find('meta', attrs={"name": "description"})
    if meta_tag and meta_tag.get('content'):
        content = meta_tag.get('content')
    else:
        logger.warning(
            "The <meta> tag with 'name=description'" 
            "was not found on the URL"
        )
        content = None
    return content
