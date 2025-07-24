from bs4 import BeautifulSoup
import requests
import logging
import os

logger = logging.getLogger(__name__)

def html_url_to_soup(url):
    """Convert HTML from URL to BeautifulSoup object"""
    logger.debug(f"Fetching HTML from {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    ZENROWS_API_KEY = os.getenv('ZENROWS_API_KEY')
    zenrows_url = 'https://api.zenrows.com/v1/'

    session = requests.Session()
    session.headers.update(headers)

    url = url
    params = {
        'url': url,
        'apikey': ZENROWS_API_KEY,
    }
    response = requests.get(zenrows_url, params=params)
    if response.status_code != 200:
        logger.error(f"Response status code: {response.status_code}")
        response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")