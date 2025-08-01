from bs4 import BeautifulSoup
import requests
import os

from logger import logger

def parse_html(html_content):
    """Convert HTML string to BeautifulSoup object for parsing"""
    return BeautifulSoup(html_content, "html.parser")

def html_url_to_soup(url):
    logger.debug(f"Parsing URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    logger.debug(f"HTTP response status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
        logger.error(f"Failed to fetch URL {url}: HTTP {response.status_code}")
        return None

def get_soup_zenrows(url):
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