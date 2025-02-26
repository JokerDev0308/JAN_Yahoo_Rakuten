import pandas as pd

from webdriver_manager import WebDriverManager
# from scripts.amazon_scraper import AmazonScraper
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
from config import JANCODE_SCV, OUTPUT_XLSX, RUNNING, WAITING
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
        self.df = pd.read_csv(JANCODE_SCV)
    
    def scrape_running(self):
        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                while WAITING:
                    sleep(1)

                jan = row['JAN']
                print(f"Processing {index + 1}/{total_records}: JAN {jan}")
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan)
                    rakuten_future = executor.submit(self.rakuten_scraper.scrape_price, jan)

                    self.df.at[index, 'Yahoo Price'] = yahoo_future.result()
                    self.df.at[index, 'Rakuten Price'] = rakuten_future.result()
                
                self.calculate_prices_for_row(index)
                
                if (index + 1) % 10 == 0:  # Save more frequently
                    self.save_results()

                sleep(1)  # Reduced sleep time
        finally:
            WebDriverManager.close_all()  # Ensure all drivers are closed
            
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
            
        self.df.at[index, 'Min Price'] = min_price
        self.df.at[index, 'Price Difference'] = self.df.at[index, 'price'] - self.df.at[index, 'Min Price']


    def save_results(self):
        os.makedirs(os.path.dirname(OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(OUTPUT_XLSX, index=False)
        print(f"Progress saved to {OUTPUT_XLSX}")

def main():
    try:
        while RUNNING:
            scraper = PriceScraper()
            scraper.load_data()
            scraper.scrape_running()
            sleep(5)
    except KeyboardInterrupt:
        WebDriverManager.close_all()

if __name__ == "__main__":
    main()
