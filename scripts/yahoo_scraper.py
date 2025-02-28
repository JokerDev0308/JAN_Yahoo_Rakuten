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

    def scrape_price(self, jan_code, url=None):
        product = {}
        product['url'] = url

        try:
            # If no URL is provided, construct a URL from the JAN code
            if not url:
                search_url = f"https://shopping.yahoo.co.jp/search?p={jan_code}"
                logger.info(f"Fetching URL for JAN code {jan_code} from {search_url}")
                self.driver.get(search_url)

                items = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.SearchResult_SearchResult__cheapestButton__SFFlT"))
                )

                if not items:
                    logger.warning(f"No items found for JAN code {jan_code}")
                    return "N/A"

                product['url'] = items[0].get_attribute('href')

            logger.info(f"Scraping price from URL: {product['url']}")
            self.driver.get(product['url'])

            price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
            )
            
            if price_elements:
                product["price"] = price_elements[0].text.translate(str.maketrans("", "", "円,")).strip()
                return product
            
            logger.warning(f"Price element not found for {jan_code}")
            return "N/A"

        except Exception as e:
            logger.error(f"Yahoo scraping failed for {jan_code}: {e}")
            return "N/A"

    def close(self):
        pass  # Handling is done by WebDriverManager
