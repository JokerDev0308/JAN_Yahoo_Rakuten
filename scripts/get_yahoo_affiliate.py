import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooScraperForGetAffiliateCode:
    def __init__(self):
        self.driver = None

    def setup_driver(self):
        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.binary_location = "/usr/bin/google-chrome"  # Update if necessary
            options.add_argument("--remote-debugging-port=9222")
        
        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(TIMEOUT)

    def scrape_price(self, jan_code):
        if not self.driver:
            self.setup_driver()

        try:
            self.driver.get(f"https://shopping.yahoo.co.jp/search?p={jan_code}")
            
            # Find all items in one go
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.SearchResult_SearchResult__cheapestButton__SFFlT"))
            )

            prodcut_url = items[0].get_attribute('href')

            pattern = r"products/([a-zA-Z0-9]+)"
            match = re.search(pattern, prodcut_url)

            if match:
                affili = match.group(1)
        except Exception as e:
            logger.error(f"Scraping failed: {e}")

        logger.info(f"Final affil for {jan_code}: {affili}")
        return affili

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None