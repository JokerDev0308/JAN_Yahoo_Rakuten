import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import HEADLESS, TIMEOUT, CHROMEDRIVER_PATH

class YahooScraper:
    def __init__(self):
        self.driver = None

    def setup_driver(self):
        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")  # Add no-sandbox option
            options.add_argument("--disable-dev-shm-usage")  # Add disable-dev-shm-usage option
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
                
                except Exception:
                    continue
            
            # Check if min_price is not infinity
            if min_price != float('inf'):
                print("min_price_link", min_price_link)

                # Navigate to the page with the lowest price
                min_price_link.click()

                # Wait for the new page to load and the price element to become visible
                try:
                    # Wait until the price element is loaded on the new page (use an appropriate selector)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
                    )

                    # Try to find the price element and extract the price
                    price_element = self.driver.find_element(By.CSS_SELECTOR, ".style_Item__money__e2mFn")
                    price = price_element.text.replace("円", "").replace(",", "").strip()
                    print(price)

                except Exception as e:
                    # If an error occurs (e.g., element not found), print the error and fall back to min_price
                    print(f"Error while extracting price: {e}")
                    price = str(min_price)  # Fallback to the previous price if not found
                    print("Fallback to min_price:", price)
            else:
                print(1)
                price = "N/A"
        except Exception:
            print(2)
            price = "N/A"
        
        print(price)

        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None


