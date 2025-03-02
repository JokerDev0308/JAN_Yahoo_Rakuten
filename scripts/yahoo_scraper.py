from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo")

    def scrape_price(self, jan_code):
        if not self.driver:
            self.setup_driver()

        try:
            self.driver.get(f"https://shopping.yahoo.co.jp/search?p={jan_code}")

            # Find all items in one go
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".LoopList__item"))
            )

            min_price = float('inf')
            min_price_link = None

            # Process items more efficiently
            for item in items:
                try:
                    price_text = item.find_element(By.CSS_SELECTOR, 
                        ".SearchResultItemPrice_SearchResultItemPrice__value__G8pQV").text
                    current_price = int(price_text.translate(str.maketrans("", "", "円,")))

                    if current_price < min_price:
                        min_price = current_price
                        temp = item.find_element(By.CSS_SELECTOR, 
                            "a.SearchResult_SearchResult__cheapestButton__SFFlT")
                        if temp:
                            min_price_link = temp

                except (ValueError, Exception) as e:
                    logger.debug(f"Skipping item due to: {e}")
                    continue

            if min_price != float('inf') and min_price_link:
                try:
                    self.driver.get(min_price_link.get_attribute('href'))

                    # Wait and find price elements
                    price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
                    )

                    if price_elements:
                        price = price_elements[0].text.translate(str.maketrans("", "", "円,"))
                    else:
                        price = str(min_price)

                except Exception as e:
                    logger.warning(f"Using fallback price due to: {e}")
                    price = str(min_price)
            else:
                price = str(min_price) if min_price != float('inf') else "N/A"

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            price = "N/A"

        logger.info(f"Final price for {jan_code}: {price}")
        return price
