import platform
import re
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False


def _get_installed_chrome_major_version():
    """Detect the installed Chrome major version so undetected_chromedriver
    downloads a matching chromedriver instead of defaulting to latest.

    On Windows, `chrome.exe --version` forwards to an already-running
    session instead of printing the version, so we read the file's
    ProductVersion via PowerShell instead.
    """
    exe = uc.find_chrome_executable()
    if not exe:
        return None
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-Item '{exe}').VersionInfo.ProductVersion"],
                stderr=subprocess.STDOUT, text=True, timeout=10,
            )
        else:
            output = subprocess.check_output(
                [exe, "--version"], stderr=subprocess.STDOUT, text=True, timeout=10
            )
    except Exception:
        return None
    match = re.search(r"(\d+)\.\d+\.\d+\.\d+", output)
    return int(match.group(1)) if match else None


class SeleniumConfig:
    @staticmethod
    def get_chrome_options(headless=True):
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection measures
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        # Remove automation flags (most important!)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Window and display settings
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Performance optimizations
        chrome_options.add_argument("--disable-images")  # Don't load images
        chrome_options.add_argument("--disable-javascript")  # Only if you don't need JS
        
        # Additional stability
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        return chrome_options
        
    @staticmethod
    def create_driver(headless=True):
        if UNDETECTED_AVAILABLE:
            # Use undetected_chromedriver if available
            options = uc.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            
            # Add basic options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            driver = uc.Chrome(options=options, version_main=_get_installed_chrome_major_version())
            return driver
        else:
            # Fallback to regular selenium
            options = SeleniumConfig.get_chrome_options(headless)
            driver = webdriver.Chrome(options=options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver