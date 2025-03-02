from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RakutenScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("rakuten")

    def scrape_price(self, jan_code):
        try:
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?s=11&used=0")
            
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".final-price"))
            )

            print(items)

            
            if items:
                price = items[0].text.translate(str.maketrans("", "", "円,"))
                return price
                        
            return "N/A"

        except Exception as e:
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"

    def close(self):
        pass  
