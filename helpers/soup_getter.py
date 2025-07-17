from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger(__name__)

def html_url_to_soup(url):
    """Convert HTML from URL to BeautifulSoup object"""
    logger.info(f"Fetching HTML from {url}")
    response = requests.get(url)
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response content: {response.content}")
    return BeautifulSoup(response.content, 'html.parser')