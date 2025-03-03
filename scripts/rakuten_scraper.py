from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re

# Utility function to clean and extract numeric value from a price string
def clean_price(price_str):
    # Remove non-numeric characters, keeping only digits and periods
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    
    # If the cleaned string is empty, return a default value (e.g., "N/A")
    if cleaned_price == "":
        return "N/A"
    
    return float(cleaned_price)

class RakutenScraper:
    def __init__(self):
        # Initialize WebDriver using ChromeDriverManager
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

    def scrape_price(self, jan_code):
        try:
            # Navigate to the Rakuten page with the provided JAN code
            self.driver.get(f"https://search.rakuten.co.jp/search/mall/{jan_code}/?s=11&used=0")
            
            # Wait for the button to load and click on it
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.dui-button.-bestshop.-fluid"))
            )

            # Get the link from the button and navigate to it
            link = button.get_attribute('href')
            self.driver.get(link)

            # Wait for the product details to load
            searchresultitem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".searchresultitem"))
            )

            # Find the elements containing the screen price and shipping price
            screen_price = searchresultitem.find_element(By.CSS_SELECTOR, ".price--3zUvK").text
            ship_price = searchresultitem.find_element(By.CSS_SELECTOR, ".points--DNEud").text

            print("=====screen========", screen_price)
            print("=====screen========", ship_price)

            # Clean the price values and calculate the final price
            result_price = clean_price(screen_price) - clean_price(ship_price)

            print(f"Final Price: {result_price}")
            return result_price

        except Exception as e:
            print(f"Error occurred: {e}")
            return "N/A"

    def close(self):
        # Close the WebDriver
        self.driver.quit()

# Example usage:
if __name__ == "__main__":
    scraper = RakutenScraper()
    jan_code = "4549292200508"  # Example JAN code
    price = scraper.scrape_price(jan_code)
    print(f"Price for JAN code {jan_code}: {price}")
    scraper.close()
