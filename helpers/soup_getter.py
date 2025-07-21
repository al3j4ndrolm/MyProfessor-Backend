from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger(__name__)

def html_url_to_soup(url):
    """Convert HTML from URL to BeautifulSoup object"""
    logger.info(f"Fetching HTML from {url}")
    
    # Headers to mimic a real browser and avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        logger.info(f"Response status code: {response.status_code}")
        
        # Check if we got a 403 error
        if response.status_code == 403:
            logger.error(f"403 Forbidden error accessing {url}")
            logger.error("This might be due to bot detection or missing required headers")
            raise Exception(f"403 Forbidden: Access denied to {url}")
        
        # Check for other error status codes
        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code} error accessing {url}")
            raise Exception(f"HTTP {response.status_code} error accessing {url}")
        
        return BeautifulSoup(response.content, 'html.parser')
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        raise