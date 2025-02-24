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
                        # Find the link element within this item
                        min_price_link = item.find_element(By.CSS_SELECTOR, "a.Button")
                
                except Exception as e:
                    logger.warning(f"Error finding price in item: {e}")
                    continue
            
            # Check if min_price is not infinity
            if min_price != float('inf'):
                logger.info("Lowest price link found, navigating to it.")
                min_price_link.click()

                # Wait for the new page to load and the price element to become visible
                try:
                    price_element = WebDriverWait(self.driver, TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
                    )
                    price = price_element.text.replace("円", "").replace(",", "").strip()
                    logger.info(f"Price on new page: {price}")
                except Exception as e:
                    logger.error(f"Error while extracting price on new page: {e}")
                    price = str(min_price)  # Fallback to the previous price if not found
                    logger.info(f"Fallback to min_price: {price}")
            else:
                logger.info("No valid price found.")
                price = "N/A"
        except Exception as e:
            logger.error(f"Error in main process: {e}")
            price = "N/A"
        
        logger.info(f"Final price: {price}")
        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None