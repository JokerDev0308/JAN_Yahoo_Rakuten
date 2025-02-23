import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
            items = self.driver.find_elements(By.CSS_SELECTOR, ".LoopList_item")
            
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
            
            if min_price != float('inf'):
                # Navigate to the page with lowest price
                min_price_link.click()
                # Wait for the new page to load and find the first price element
                time.sleep(2)  # Give the page time to load
                try:
                    price_element = self.driver.find_element(By.CSS_SELECTOR, ".style_Item__money__e2mFn")
                    price = price_element.text.replace("円", "").replace(",", "").strip()
                except Exception:
                    price = str(min_price)  # Fallback to the previous price if not found
            else:
                price = "N/A"
        except Exception:
            price = "N/A"
        
        print(price)

        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

if __name__ == "__main__":
    test_jan = "4902370519984"
    scraper = YahooScraper()
    try:
        price = scraper.scrape_price(test_jan)
        print(f"Yahoo Price for {test_jan}: ¥{price}")
    finally:
        scraper.close()
