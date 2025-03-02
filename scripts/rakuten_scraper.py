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

            # Wait for the filter button to load and get its value
            filter_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='pd']"))
            )

            print("Initial filter button value:", filter_button.get_attribute('value'))

            # Check if the value is '0' (unchecked), and click it if so
            if filter_button.get_attribute('value') != '0':
                # Click the filter checkbox (no need for jQuery, use Selenium's click method)
                filter_button.click()

                # Submit the form (find the form and submit it directly)
                form = self.driver.find_element(By.CSS_SELECTOR, '.final-price-form--3Ko_l')
                form.submit()

                # Wait for the page to refresh or for new content to load (improve wait condition)
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".final-price"))
                )

            # Wait for the final price elements to load
            items = self.driver.find_elements(By.CSS_SELECTOR, ".final-price")

            # If there are price elements, extract the first one
            if items:
                # Assuming the first item has the price in text, clean it up by removing unwanted characters
                price = items[0].text.translate(str.maketrans("", "", "円,"))
                print("Price extracted:", price)
                return price
            
            return "N/A"

        except Exception as e:
            # Log the error and return a default value if something fails
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"



    def close(self):
        pass  
