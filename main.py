import pandas as pd
from scripts.amazon_scraper import AmazonScraper
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
from config import JANCODE_SCV, OUTPUT_XLSX, RUNNING, WAITING
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep


class PriceScraper:
    def __init__(self):
        self.df = None
        self.amazon_scraper = AmazonScraper()
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()

    def load_data(self):
        self.df = pd.read_csv(JANCODE_SCV)
    
    def scrape_running(self):
        total_records = len(self.df)
        for index, row in self.df.iterrows():
            while WAITING:
                sleep(1)
                continue

            jan = row['JAN']
            print(f"Processing {index + 1}/{total_records}: JAN {jan}")
            
            # Scrape prices concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                # amazon_future = executor.submit(self.amazon_scraper.scrape_price, jan)
                yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan)
                # rakuten_future = executor.submit(self.rakuten_scraper.scrape_price, jan)

                print(yahoo_future)
                
                # self.df.at[index, 'Amazon Price'] = amazon_future.result()
                self.df.at[index, 'Yahoo Price'] = yahoo_future.result()
                # self.df.at[index, 'Rakuten Price'] = rakuten_future.result()
            
            # Calculate prices for current record
            self.calculate_prices_for_row(index)
            
            # Save intermediate results
            self.save_results()

            sleep(2)
            
    def calculate_prices_for_row(self, index):
        prices = [
            self.df.at[index, 'Amazon Price'],
            self.df.at[index, 'Yahoo Price'],
            self.df.at[index, 'Rakuten Price']
        ]
        self.df.at[index, 'Min Price'] = min(prices)
        self.df.at[index, 'Price Difference'] = self.df.at[index, 'Master Price'] - self.df.at[index, 'Min Price']


    def save_results(self):
        os.makedirs(os.path.dirname(OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(OUTPUT_XLSX, index=False)
        print(f"Progress saved to {OUTPUT_XLSX}")

def main():
    while RUNNING:
        scraper = PriceScraper()
        scraper.load_data()
        scraper.scrape_running()
        
        sleep(10)

if __name__ == "__main__":
    main()
