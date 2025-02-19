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
        service = Service(CHROMEDRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(TIMEOUT)

    def scrape_price(self, jan_code):
        if not self.driver:
            self.setup_driver()

        url = f"https://auctions.yahoo.co.jp/search/search?p={jan_code}"
        self.driver.get(url)

        try:
            price_element = self.driver.find_element(By.CSS_SELECTOR, ".Product__priceValue")
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
    scraper = YahooScraper()
    try:
        price = scraper.scrape_price(test_jan)
        print(f"Yahoo Price for {test_jan}: ¥{price}")
    finally:
        scraper.close()
