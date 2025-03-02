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
            # Navigate to the Rakuten search URL with the given JAN code
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}?s=11&&used=0")

            # Locate the form element using the CSS selector for the form
            form = self.driver.find_element(By.CSS_SELECTOR, ".final-price-form--3Ko_l")

            # Locate the JAN code input field (p), set, and _mp within the form
            p = form.find_element(By.NAME, "p")
            set = form.find_element(By.NAME, "set")
            _mp = form.find_element(By.NAME, "_mp")

            # Clear any existing value in the JAN code field (not necessary since we're setting it directly)
            p.clear()  # Clear if there's any pre-existing value
            p.send_keys(jan_code)  # Set the value of the JAN code input field to the provided JAN code
            
            # Send additional required fields
            p.send_keys('1')
            set.send_keys('priceDisplay')
            _mp.send_keys("{'display_options:price':0,'pricedisplay':2}")

            # Submit the form
            form.submit()

            # Wait for the search results to load after form submission
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".searchresultitem"))
            )

            # Once the results are loaded, find the price elements
            items = self.driver.find_elements(By.CSS_SELECTOR, ".searchresultitem")

            # Check if there are any items found
            if items:
                # Extract the price from the first item
                price_elements = items[0].find_elements(By.CSS_SELECTOR, ".final-price")
                
                if price_elements:
                    # Extract the price and clean it up (remove '円' and commas)
                    price = price_elements[0].text.translate(str.maketrans("", "", "円,"))
                    print(price)
                    return price
            
            return "N/A"

        except Exception as e:
            # Log the error and return a default value if something fails
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"



    def close(self):
        pass  
