import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH


# Set up logging
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

        try:
            self.driver.get(f"https://shopping.yahoo.co.jp/search?p={jan_code}")
            
            # Wait for the search results to load and find all items
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".SearchResult_SearchResult__cheapestButton__SFFlT"))
            )

            # Get the link to the first item in the list
            item_link = items[0].get_attribute('href')
            logger.info(f"Found item link: {item_link}")

            try:
                self.driver.get(item_link)
                
                # Wait for the price element to be available
                price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
                )
                
                if price_elements:
                    price = price_elements[0].text.translate(str.maketrans("", "", "円,"))
                else:
                    price = "N/A"
                    
            except Exception as e:
                logger.warning(f"Error retrieving price: {e}")
                price = "N/A"
        
        except Exception as e:
            logger.error(f"Failed to scrape data for JAN code {jan_code}: {e}")
            price = "N/A"

        logger.info(f"Final Yahoo price for {jan_code}: {price}")
        return price


    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None