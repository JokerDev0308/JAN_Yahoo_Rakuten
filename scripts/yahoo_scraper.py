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
                        min_price_link = item.find_element(By.CSS_SELECTOR, "a.SearchResult_SearchResult__detailsContainerLink__HrJQL")

                except Exception as e:
                    logger.warning(f"Error finding price in item: {e}")
                    continue

            if min_price != float('inf') and min_price_link:
                logger.info(f"Lowest price found: {min_price}")
                
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", min_price_link)
                    time.sleep(1)  # Short wait before clicking
                    min_price_link.click()
                    logger.info("Navigated to the lowest-priced product.")

                    try:
                        # Ensure the page has loaded
                        WebDriverWait(self.driver, TIMEOUT).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        logger.info("New page loaded successfully.")

                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        
                        time.sleep(1)

                        logger.info("page scrolled successfully.")

                        print("==========================")
                        # Wait for price element
                        price_elements = self.driver.find_elements(By.CSS_SELECTOR, ".style_Item__money__e2mFn")
                        print(self.driver.page_source)
                        print("==========================")

                        if price_elements:
                            all_prices = [p.text for p in price_elements]
                            logger.info(f"Extracted prices: {all_prices}")
                            price = all_prices[0]  # Select the first price
                        else:
                            logger.error("Price element not found.")
                            price = str(min_price)  # Fallback

                    except Exception as e:
                        logger.error(f"Error extracting price: {e}")
                        price = str(min_price)  # Fallback if not found

                except Exception as e:
                    logger.error(f"Error clicking the link: {e}")
                    price = str(min_price)  # Fallback if click fails


        except Exception as e:
            logger.error(f"Error in main process: {e}")
            price = "N/A"
        
        logger.info(f"Final price: {price}")
        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None