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

class YahooScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo")

    def scrape_price(self, jan_code, url=None):
        """
        Scrape price information from Yahoo Shopping.
        Returns a dictionary with 'url' and 'price', or 'N/A' if scraping fails.
        """
        try:
            # If no URL provided, search by JAN code
            if not url or url == "nan":
                return self._search_by_jan(jan_code)
            
            # Direct URL scraping
            return self._scrape_from_url(url)

        except Exception as e:
            logger.error(f"Scraping failed for JAN {jan_code}: {e}")
            return "N/A"

    def _search_by_jan(self, jan_code):
        """Helper method to search and find lowest price by JAN code"""
        try:
            self.driver.get(f"https://shopping.yahoo.co.jp/search?p={jan_code}")
            
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.SearchResult_SearchResult__cheapestButton__SFFlT"))
            )

            items = self.driver.find_elements(By.CSS_SELECTOR, ".LoopList__item")

            min_price = float('inf')
            min_price_link = None

            for item in items:
                price = self._extract_price_from_item(item)
                if price and price < min_price:
                    link = item.find_element(By.CSS_SELECTOR, 
                        "a.SearchResult_SearchResult__cheapestButton__SFFlT")
                    if link:
                        min_price = price
                        min_price_link = link

            if min_price != float('inf') and min_price_link:
                return self._scrape_from_url(min_price_link.get_attribute('href'), min_price)
            
            return {'price': str(min_price) if min_price != float('inf') else "N/A", 'url': None}

        except Exception as e:
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"

    def _extract_price_from_item(self, item):
        """Helper method to extract price from an item element"""
        try:
            price_text = item.find_element(By.CSS_SELECTOR, 
                ".SearchResultItemPrice_SearchResultItemPrice__value__G8pQV").text
            return int(price_text.translate(str.maketrans("", "", "円,")))
        except Exception:
            return None

    def _scrape_from_url(self, url, fallback_price=None):
        """Helper method to scrape price from a specific URL"""
        try:
            self.driver.get(url)
            price_elements = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".style_Item__money__e2mFn"))
            )
            
            if price_elements:
                return {
                    'url': url,
                    'price': price_elements[0].text.translate(str.maketrans("", "", "円,")).strip()
                }
            
            return {
                'url': url,
                'price': str(fallback_price) if fallback_price else "N/A"
            }

        except Exception as e:
            logger.error(f"URL scraping failed: {e}")
            return "N/A"

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")


if __name__ == "__main__":
    scraper = YahooScraper()
    print(scraper.scrape_price("4549980770559"))
    sleep(1)
    print(scraper.scrape_price("4549980789025"))
    sleep(1)
    print(scraper.scrape_price("4960759913784"))
    sleep(1)
    print(scraper.scrape_price("4545350056452"))
    sleep(1)
    print(scraper.scrape_price("4549980789018"))
    scraper.close()