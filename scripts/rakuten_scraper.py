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

            # Check if the value is '0' (unchecked), and click it if so using JavaScript
            if filter_button.get_attribute('value') != '0':
                # Execute JavaScript to click the checkbox and submit the form
                self.driver.execute_script("""
                    var filterButton = document.querySelector("input[name='pd']");
                    filterButton.click()
                """)

                # Wait for the page to refresh or for new content to load (use explicit wait)
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".final-price"))
                )

            # Wait for the final price elements to load after submitting the form
            items = self.driver.find_elements(By.CSS_SELECTOR, ".final-price")

            # If there are price elements, extract the first one
            if items:
                # Clean the price text by removing '円' and commas
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
