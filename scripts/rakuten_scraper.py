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

class RakutenScraper:
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
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?ran=1001000{jan_code}&s=11&used=0/")
            logger.info(f"Page loading is succesful")
            # Find all items in one go
            items = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".price--3zUvK"))
            )
            print("=============================")
            logger.info("Item HTML: %s", items[0].get_attribute("outerHTML"))
            print("=============================")

            price = items[0].text().strip()
            print("Rakuten Price:", price)
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            price = "N/A"

        return price

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

if __name__ == "__main__":
    test_jan = "4902370519984"
    scraper = RakutenScraper()
    price = scraper.scrape_price(test_jan)
    print(f"Rakuten Price for {test_jan}: ¥{price}")
    scraper.close()
