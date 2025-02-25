import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooScraper:
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

        url = f"https://shopping.yahoo.co.jp/search?p={jan_code}"
        self.driver.get(url)

        try:
            # Find all items
            items = self.driver.find_elements(By.CSS_SELECTOR, ".LoopList__item")

            # Initialize variables for tracking minimum price
            min_price = float('inf')
            min_price_link = None
            
            # Loop through items to find the lowest price
            for item in items:
                try:
                    price_element = item.find_element(By.CSS_SELECTOR, ".SearchResultItemPrice_SearchResultItemPrice__value__G8pQV")
                    current_price = int(price_element.text.replace("円", "").replace(",", "").strip())
                    
                    if current_price < min_price:
                        min_price = current_price
                        min_price_link = item.find_element(By.CSS_SELECTOR, "a.Button")
                
                except Exception as e:
                    logger.warning(f"Error finding price in item: {e}")
                    continue
            
            price = "N/A"  # Default value moved here
            if min_price != float('inf') and min_price_link:
                logger.info(f"Lowest price found: {min_price}")
                
                try:
                    WebDriverWait(self.driver, TIMEOUT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.Button")))
                    min_price_link.click()
                    logger.info("Button clicked successfully.")

                    try:
                        price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
                        )

                        all_prices = [p.text.replace("円", "").replace(",", "").strip() for p in price_elements]
                        logger.info(f"Extracted prices: {all_prices}")

                        if all_prices:
                            price = all_prices[0]  # Pick the first one if available
                        else:
                            price = str(min_price)  # Fallback if no price found
                    except Exception as e:
                        logger.error(f"Error while extracting price on new page: {e}")
                        price = str(min_price)
                        logger.info(f"Fallback to min_price: {price}")

                except Exception as e:
                    logger.error(f"Error clicking the button: {e}")
                    price = str(min_price)  # Fallback if click fails
            else:
                logger.info("No valid price found or no clickable link.")

        except Exception as e:
            logger.error(f"Error in main process: {e}")
            price = "N/A"
        
        logger.info(f"Final price: {price}")
        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None