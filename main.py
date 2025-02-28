import pandas as pd
from datetime import datetime

from webdriver_manager import WebDriverManager
# from scripts.amazon_scraper import AmazonScraper
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
import config 
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep


class PriceScraper:
    def __init__(self):
        self.df = None
        # self.amazon_scraper = AmazonScraper()
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()

    def load_data(self):
        self.df = pd.read_csv(config.JANCODE_SCV)
    
    def scrape_running(self):
        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                while not self.running():
                    print("Running was stopped")
                    return

                jan = row['JAN']
                saved_url = row.get('Yahoo URL')
                print(f"Processing {index + 1}/{total_records}: JAN {jan}")
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    yahoo_future = executor.submit(
                        self.yahoo_scraper.scrape_price, 
                        jan,
                        saved_url
                    )
                    rakuten_future = executor.submit(
                        self.rakuten_scraper.scrape_price, 
                        jan
                    )

                    yahoo_product = yahoo_future.result()

                    # Check if yahoo_product is a dictionary
                    if isinstance(yahoo_product, dict) and "price" in yahoo_product:
                        cleaned_price = yahoo_product["price"].strip()  # Strip the newline or extra spaces
                        self.df.at[index, 'Yahoo Price'] = cleaned_price
                        self.df.at[index, 'Yahoo! Link'] = yahoo_product.get("url", "N/A")
                    else:
                        # If yahoo_product is not a dictionary, handle it as an error
                        self.df.at[index, 'Yahoo Price'] = "N/A"
                        self.df.at[index, 'Yahoo! Link'] = "N/A"

                    # Continue with the Rakuten scraping
                    self.df.at[index, 'Rakuten Price'] = rakuten_future.result()
                    self.calculate_prices_for_row(index)

                    self.df.at[index, 'datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if (index + 1) % 10 == 0 or (index + 1) == total_records:
                    self.save_results()
                    self.save_yahoo_urls()  

                sleep(1)
        finally:
            WebDriverManager.close_all()



            
    def calculate_prices_for_row(self, index):
        prices = [
            # self.df.at[index, 'Amazon Price'],
            self.df.at[index, 'Yahoo Price'],
            self.df.at[index, 'Rakuten Price']
        ]

        # Filter out "N/A" values and convert valid prices to numeric
        valid_prices = [float(price) for price in prices if price != "N/A" and price is not None]

        # If there are valid prices, calculate the minimum; otherwise, handle the "no valid prices" case
        if valid_prices:
            min_price = min(valid_prices)
        else:
            min_price = "N/A"
            
        self.df.at[index, 'Price Difference'] = self.df.at[index, 'price'] - min_price


    def save_results(self):
        os.makedirs(os.path.dirname(config.OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(config.OUTPUT_XLSX, index=False)        
        print(f"Progress saved to {config.OUTPUT_XLSX}")

    def save_yahoo_urls(self):
        """Save JANs and their corresponding Yahoo URLs"""
        urls_df = self.df[['JAN', 'price', 'Yahoo! Link']].copy()
        urls_df.to_csv(config.JANCODE_SCV, index=False)
        print(f"URLs saved to {config.JANCODE_SCV}")

    def running(self):
       return os.path.exists(config.RUNNING)

def main():
    try:
        i = 0
        while True:
            print(f"init=={i}==", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            scraper = PriceScraper()
            scraper.load_data()
            print(f"loading =={i}==", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            scraper.scrape_running()
            print(f"scraping =={i}==", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sleep(5)
            i += 1
    except KeyboardInterrupt:
        WebDriverManager.close_all()

if __name__ == "__main__":
    main()
