from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import TIMEOUT
from webdriver_manager import WebDriverManager
import re

def clean_price(price_str):
    # Ensure the input is a string
    if isinstance(price_str, (int, float)):  # If the input is numeric, convert it to a string
        price_str = str(price_str)
    
    # Regex to capture only numbers with commas (e.g., "25,582", "317,225") before "ポイント" or "円"
    match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?=ポイント|円)', price_str)
    
    if match:
        cleaned_price = match.group(0)  # Get the matched part, which is the number
        cleaned_price = cleaned_price.replace(',', '')  # Remove commas to get a pure numeric string
        
        try:
            return float(cleaned_price)  # Convert to float
        except ValueError:
            return 0.0  # Return 0 if conversion fails
    else:
        return 0.0  # Return 0 if no match is found


class RakutenScraper:
    def __init__(self):
        self.driver = WebDriverManager.get_driver("rakuten")

    def scrape_price(self, jan_code):
        try:
            # Navigate to the product search page
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?s=11&used=0")
            
            # Wait for the button that leads to the best shop link to load
            button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.dui-button.-bestshop.-fluid"))
            )
            
            # Retrieve the link to the best shop
            link = button[0].get_attribute('href')  # Corrected from getget_attribute to get_attribute

            # Navigate to the link of the best shop
            self.driver.get(link)

            # Wait for the search result item to appear
            searchresultitem = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".searchresultitem"))
            )
            
            # Assuming we're interested in the first item in the list
            item = searchresultitem[0]
            
            # Extract screen price and shipping price
            screen_price = item.find_element(By.CSS_SELECTOR, ".price--3zUvK").text
            ship_price = item.find_element(By.CSS_SELECTOR, ".points--DNEud").text
            print(screen_price,"=============", ship_price)
            # Clean and calculate the prices
            cleaned_screen_price = clean_price(screen_price)
            cleaned_ship_price = clean_price(ship_price)

            

            # Assuming shipping price is added, not subtracted
            result_price = cleaned_screen_price - cleaned_ship_price  # If you're including shipping, sum them.

            print("=========", result_price)

            return result_price

        except Exception as e:
            print(f"Error occurred: {e}")
            return "N/A"


    def close(self):
        pass  
