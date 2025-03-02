from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager
from time import sleep

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RakutenScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("rakuten")

    def scrape_price(self, jan_code):
        try:
            # Navigate to the URL with the provided JAN code
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?s=11&used=0")

            # Wait for the filter button to load and click if needed
            filter_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".control--FQ2nD"))
            )

            # Click the filter button if its value is not 0
            filter_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".control--FQ2nD input[type='checkbox']"))
            )

            # Check if the value is '0' (unchecked), and click if so
            if filter_button.get_attribute('value') == '0':
                self.driver.execute_script("arguments[0].click();", filter_button)

                sleep(1)

            # Wait for the final price elements to load
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".final-price"))
            )

            # Print the raw list of items (debugging)
            print(items)

            # If there are price elements, extract the first one
            if items:
                # Assuming the first item has the price in text, remove unwanted characters
                price = items[0].text.translate(str.maketrans("", "", "円,"))
                return price
            
            return "N/A"

        except Exception as e:
            # Log the error and return a default value if something fails
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"


    def close(self):
        pass  
