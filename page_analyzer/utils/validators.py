from urllib.parse import urlparse

from validators.url import url as is_url

from page_analyzer.utils.logger import setup_logging

logger = setup_logging()


def get_normalized_url(url):
    """
    Функция для нормализации
    введеного пользователем URL
    """
    normalized_url = url.lower().strip()
    return normalized_url


def validator(url):
    """Функция валидации URL"""
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
    
    normalized_url = get_normalized_url(url)
    return {'valid': True, 'url': normalized_url, 'message': ''}


def get_domain_from_url(url):
    """Функция для приведения URL 
    к доменному имени"""
    normalized_url = get_normalized_url(url)
    parsed_normalized_url = urlparse(normalized_url)
    domain = f'{parsed_normalized_url.scheme}://{parsed_normalized_url.netloc}'
    return domain
