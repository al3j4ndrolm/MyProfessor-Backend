from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SeleniumConfig:
    @staticmethod
    def get_chrome_options(headless=True):
        """
        Get Chrome options with all necessary arguments for stable operation.
        
        Args:
            headless (bool): Whether to run in headless mode
        """
        chrome_options = Options()
        
        # Basic headless setup
        if headless:
            chrome_options.add_argument("--headless")
        
        # Stability arguments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Window and display settings
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Additional stability
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        return chrome_options
    
    @staticmethod
    def create_driver(headless=True):
        """
        Create and return a configured Chrome driver.
        
        Args:
            headless (bool): Whether to run in headless mode
        """
        options = SeleniumConfig.get_chrome_options(headless)
        return webdriver.Chrome(options=options)