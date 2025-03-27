from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("yahoo")

    def scrape_price(self, jan_code, url):
        """
        Scrape price information from Yahoo Shopping.
        Returns a dictionary with 'url' and 'price', or 'N/A' if scraping fails.
        """
        try:
            # # If no URL provided, search by JAN code
            # if url == "nan" or url == "N/A" or not url  :
            #     logger.info(f"go to jan")
            #     return self._search_by_jan(jan_code)
            
            # # Direct URL scraping
            # logger.info(f"go to Direct url")
            # return self._scrape_from_url(url)

            return self._search_by_jan(jan_code)

        except Exception as e:
            logger.error(f"Scraping failed for JAN {jan_code}: {e}")
            return "N/A"

    def _search_by_jan(self, jan_code):
        """Helper method to search and find lowest price by JAN code"""
        try:
            search_url = f"https://shopping.yahoo.co.jp/search?used=2&p={jan_code}"
            self.driver.get(search_url)
            
            # link_item = WebDriverWait(self.driver, TIMEOUT).until(
            #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".SearchResults_SearchResults__page__OJhQP"))
            # )

            search_result = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#searchResults"))
            )

            link_items = search_result.find_elements(By.CSS_SELECTOR, '.SearchResult_SearchResult__cheapestButton__SFFlT')

            if link_items and len(link_items) > 0:
                cheapest_link = link_items[0].get_attribute('href')
                logger.info(f"Cheapest link: {cheapest_link}")
                return self._scrape_from_url(cheapest_link)
            else:
                items = self.driver.find_elements(By.CSS_SELECTOR, ".LoopList__item")
                min_price = float('inf')
                for item in items:
                    price = self._extract_price_from_item(item)
                    if price and price < min_price:
                        min_price = price
                                
                logger.info( {'price': str(min_price) if min_price != float('inf') else "N/A", 'url': search_url})
                return {'price': str(min_price) if min_price != float('inf') else "N/A", 'url': search_url}

        except Exception as e:
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"

    def _extract_price_from_item(self, item):
        """Helper method to extract price from an item element"""
        try:
            price_text = item.find_element(By.CSS_SELECTOR, 
                ".SearchResultItemPrice_SearchResultItemPrice__value__G8pQV").text
            return int(price_text.translate(str.maketrans("", "", "円,")))
        except Exception as e:
            logger.error(f"Search by JAN failed: {e}")
            return None

    def _scrape_from_url(self, url):
        """Helper method to scrape price from a specific URL"""
        try:
            self.driver.get(url)
            cheapest_result  = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "style_Item__money__e2mFn"))
            )

            logger.info(f"Cheapest result")

            # price_elements = cheapest_result[0].find_elements(By.CSS_SELECTOR, ".style_Item__money__e2mFn")
            # if not price_elements:
            #     logger.warning("No price elements found. Check the CSS selector or webpage structure.")
            #     return {
            #         'url': url,
            #         'price': "N/A"
            #     }

            # logger.info(f"Price elements: {[elem.text for elem in price_elements]}")

            return {
                'url': url,
                'price': 0
            }

        except Exception as e:
            logger.error(f"URL scraping failed: {e}")
            return {
                'url': url,
                'price': "N/A"
            }

        

    def close(self):
        """Close the web driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
