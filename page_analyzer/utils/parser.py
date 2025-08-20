import requests
from bs4 import BeautifulSoup as bs


# Получение status_code
response = requests.get(url, timeout=10)
response.raise_for_status()
status_code = response.status_code

# Получение h1


# Получение 
soup = BeautifulSoup(response.text, features='lxml')

                title_tag = soup.find('title')  # Подумать как строки 170 - 190 перенести в отдельную функцию а здесь сделать итерацию
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