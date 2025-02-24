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
            
        url = f"https://search.rakuten.co.jp/search/mall/{jan_code}/"
        self.driver.get(url)

        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, ".searchresultitem-price")
            price = price_element.text.replace("円", "").replace(",", "").strip()
        except Exception:
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
