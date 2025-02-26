import pandas as pd
from scripts.get_yahoo_affiliate import YahooScraperForGetAffiliateCode
from config import JANCODE_SCV, JANCODE_YH_AFFILI_SCV, RUNNING, WAITING
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep


class PriceScraper:
    def __init__(self):
        self.df = None
        self.yahoo_scraper = YahooScraperForGetAffiliateCode()

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
                try:
                    # amazon_future = executor.submit(self.amazon_scraper.scrape_price, jan)
                    yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan)

                    self.df.at[index, 'affiliate'] = yahoo_future.result()
                
                except Exception as e:
                    print(f"Error scraping prices for JAN {jan}: {e}")
                    self.df.at[index, 'Yahoo Price'] = "Error"
            
            
            # Save intermediate results
            if (index + 1) % 50 == 0 and (index+1 ) == total_records:
                self.save_results()

            sleep(2)
            
    


    def save_results(self):
        os.makedirs(os.path.dirname(JANCODE_YH_AFFILI_SCV), exist_ok=True)
        self.df.to_excel(JANCODE_YH_AFFILI_SCV, index=False)
        print(f"Progress saved to {JANCODE_YH_AFFILI_SCV}")

def main():
    while RUNNING:
        scraper = PriceScraper()
        scraper.load_data()
        scraper.scrape_running()
        
        sleep(10)

if __name__ == "__main__":
    main()
