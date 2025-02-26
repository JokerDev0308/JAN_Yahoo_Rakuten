import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo")

    def scrape_price(self, jan_code, url = None):
        product = {}
        product['url'] = url

        try:

            if not url:
                self.driver.get(f"https://shopping.yahoo.co.jp/search?p={jan_code}")
                
                items = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.SearchResult_SearchResult__cheapestButton__SFFlT"))
                )

                if not items:
                    return "N/A"

                product['url'] = items[0].get_attribute('href')

            self.driver.get(product['url'])

            price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
            )
            
            if price_elements:
                product["price"] = price_elements[0].text.translate(str.maketrans("", "", "円,"))
                return product
            
            return "N/A"

        except Exception as e:
            logger.error(f"Yahoo scraping failed for {jan_code}: {e}")
            return "N/A"

    def close(self):
        pass  # Handling is done by WebDriverManager