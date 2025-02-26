from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH

class WebDriverManager:
    _instance = None
    _drivers = {}

    @classmethod
    def get_driver(cls, scraper_name):
        if scraper_name not in cls._drivers:
            options = Options()
            if HEADLESS:
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.binary_location = "/usr/bin/google-chrome"
                options.add_argument("--remote-debugging-port=0")  # Use dynamic port
            
            service = Service(CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
            driver.implicitly_wait(TIMEOUT)
            cls._drivers[scraper_name] = driver
        
        return cls._drivers[scraper_name]

    @classmethod
    def close_all(cls):
        for driver in cls._drivers.values():
            driver.quit()
        cls._drivers.clear()