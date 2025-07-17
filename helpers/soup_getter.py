from bs4 import BeautifulSoup
import requests

def html_url_to_soup(url):
    """Convert HTML from URL to BeautifulSoup object"""
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')