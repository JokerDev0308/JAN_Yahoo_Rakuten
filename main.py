import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
import os
import re
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
import config

def clean_price(price_str):
    cleaned_price = re.sub(r'[^\d.]', '', str(price_str))
    return float(cleaned_price) if cleaned_price else 0.0

class PriceScraper:
    def __init__(self, batch_size=10, rate_limit=1):
        self.df = None
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()
        self.batch_size = batch_size
        self.rate_limit = rate_limit  # Control request pacing
        self.load_data()

    def load_data(self):
        try:
            jan_df = pd.read_csv(config.JANCODE_SCV)
            out_df = pd.read_excel(config.OUTPUT_XLSX)
            
            if {'JAN', 'price'}.issubset(jan_df.columns) and {'JAN', 'price'}.issubset(out_df.columns):
                out_df.update(jan_df)  # Update existing prices from CSV
                self.df = out_df
            else:
                self.df = jan_df
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def process_product(self, row):
        jan, saved_url = row['JAN'], row.get('Yahoo! Link')
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.yahoo_scraper.scrape_price, jan, saved_url): 'yahoo',
                executor.submit(self.rakuten_scraper.scrape_price, jan): 'rakuten'
            }
            
            results = {source: None for source in ['yahoo', 'rakuten']}
            for future in as_completed(futures):
                source = futures[future]
                try:
                    results[source] = future.result()
                except Exception as e:
                    print(f"Error scraping {source} for {jan}: {e}")
                    results[source] = "N/A"
        
        yahoo_price, yahoo_url = (clean_price(results['yahoo'].get("price", "0")), results['yahoo'].get("url", "N/A")) if results['yahoo'] != "N/A" else ("N/A", "N/A")
        rakuten_price = clean_price(results['rakuten']) if results['rakuten'] != "N/A" else "N/A"
        rakuten_url = f"https://search.rakuten.co.jp/search/mall/{jan}/?s=11&used=0"
        
        min_price, min_price_url = (min(yahoo_price, rakuten_price), yahoo_url if yahoo_price <= rakuten_price else rakuten_url) if yahoo_price != "N/A" and rakuten_price != "N/A" else (yahoo_price if yahoo_price != "N/A" else rakuten_price, yahoo_url if yahoo_price != "N/A" else rakuten_url)
        price_diff = float(row['price']) - min_price if isinstance(row['price'], (int, float)) else "N/A"
        
        return {
            'Yahoo Price': yahoo_price, 'Yahoo! Link': yahoo_url,
            'Rakuten Price': rakuten_price, 'Min Price URL': min_price_url,
            'Price Difference': price_diff, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def scrape_running(self):
        if self.df is None or self.df.empty:
            return
        
        try:
            total_records = len(self.df)
            batch_indices = range(0, total_records, self.batch_size)
            
            for i in batch_indices:
                if not self.running():
                    print("Scraping stopped.")
                    return
                
                batch = self.df.iloc[i:i+self.batch_size]
                
                with ThreadPoolExecutor() as executor:
                    future_to_index = {executor.submit(self.process_product, row): idx for idx, row in batch.iterrows()}
                    
                    for future in as_completed(future_to_index):
                        index = future_to_index[future]
                        try:
                            self.df.loc[index, future.result().keys()] = future.result().values()
                        except Exception as e:
                            print(f"Error updating row {index}: {e}")
                
                self.save_results()
                self.save_yahoo_urls()
                sleep(self.rate_limit)
        finally:
            print("Scraping completed.")
    
    def save_results(self):
        os.makedirs(os.path.dirname(config.OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(config.OUTPUT_XLSX, index=False)
        print(f"Saved progress to {config.OUTPUT_XLSX}")
    
    def save_yahoo_urls(self):
        self.df[['JAN', 'price', 'Yahoo! Link']].to_csv(config.JANCODE_SCV, index=False)
        print(f"Saved Yahoo URLs to {config.JANCODE_SCV}")
    
    @staticmethod
    def running():
        return os.path.exists(config.RUNNING)

def main():
    try:
        while True:
            scraper = PriceScraper()
            scraper.scrape_running()
            sleep(5)
    except KeyboardInterrupt:
        print("Terminating scraper.")

if __name__ == "__main__":
    main()
