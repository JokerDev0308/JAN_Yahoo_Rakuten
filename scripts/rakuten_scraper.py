from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager
import re

def clean_price(price_str):
    # Remove non-numeric characters, keeping only digits and period (.)
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    
    # If the cleaned string is empty, return a default value (e.g., 0)
    if cleaned_price == "":
        return "N/A"
    
    return float(cleaned_price)

class RakutenScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("rakuten")

    def scrape_price(self, jan_code):
        try:
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?s=11&used=0")
            
            button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.dui-button.-bestshop.-fluid"))
            )

            link = button[0].getget_attribute('href')

            self.driver.get(link)

            searchresultitem = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".searchresultitem"))
            )

            screen_price = searchresultitem.find_element(By.CSS_SELECTOR, ".price--3zUvK")

            ship_price = searchresultitem.find_element(By.CSS_SELECTOR, ".points--DNEud")
            
            result_price = clean_price(screen_price) - clean_price(ship_price)

            print("=========result_price")
            
            return result_price

        except Exception as e:
            return "N/A"

    def close(self):
        pass  
