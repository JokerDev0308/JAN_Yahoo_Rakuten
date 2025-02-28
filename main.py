import pandas as pd
from datetime import datetime
from webdriver_manager import WebDriverManager
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
import config 
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Optional, Dict, Any

class PriceScraper:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()
        self.batch_size = 10  # Configurable batch size for saving

    def load_data(self) -> None:
        """Load JAN codes and prices from CSV file"""
        self.df = pd.read_csv(config.JANCODE_SCV)
    
    def process_product(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Process a single product and return results"""
        jan = row['JAN']
        saved_url = row.get('Yahoo! Link')
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan, saved_url)
            rakuten_future = executor.submit(self.rakuten_scraper.scrape_price, jan)
            
            yahoo_product = yahoo_future.result()
            rakuten_price = rakuten_future.result()

        yahoo_price = yahoo_product.get("price", "N/A") if yahoo_product != "N/A" else "N/A"
        yahoo_url = yahoo_product.get("url", "N/A") if yahoo_product != "N/A" else "N/A"
        rakuten_url = f"https://search.rakuten.co.jp/search/mall/{jan}/?ran=1001000{jan}&s=11&used=0/"

        # Determine minimum price URL
        min_price_url = "N/A"
        price_diff = "N/A"
        
        if yahoo_price != "N/A" and rakuten_price != "N/A":
            min_price = min(float(yahoo_price), float(rakuten_price))
            min_price_url = yahoo_url if min_price == float(yahoo_price) else rakuten_url
            price_diff = float(row['price']) - min_price
        elif yahoo_price != "N/A":
            min_price_url = yahoo_url
        elif rakuten_price != "N/A":
            min_price_url = rakuten_url

        return {
            'Yahoo Price': yahoo_price,
            'Yahoo! Link': yahoo_url,
            'Rakuten Price': rakuten_price,
            'Min Price URL': min_price_url,
            'Price Difference': price_diff,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def scrape_running(self) -> None:
        """Main scraping loop with optimized batch processing"""
        if self.df is None or self.df.empty:
            return

        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                if not self.running():
                    print("Running was stopped")
                    return

                print(f"Processing {index + 1}/{total_records}: JAN {row['JAN']}")
                
                # Process single product
                results = self.process_product(index, row)
                
                # Update DataFrame
                for key, value in results.items():
                    self.df.at[index, key] = value

                # Save results in batches
                if (index + 1) % self.batch_size == 0 or (index + 1) == total_records:
                    self.save_results()
                    self.save_yahoo_urls()

                sleep(1)  # Rate limiting
                
        finally:
            WebDriverManager.close_all()

    def save_results(self) -> None:
        """Save results to Excel file"""
        os.makedirs(os.path.dirname(config.OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(config.OUTPUT_XLSX, index=False)
        print(f"Progress saved to {config.OUTPUT_XLSX}")

    def save_yahoo_urls(self) -> None:
        """Save JANs and their corresponding Yahoo URLs"""
        urls_df = self.df[['JAN', 'price', 'Yahoo! Link']].copy()
        urls_df.to_csv(config.JANCODE_SCV, index=False)
        print(f"URLs saved to {config.JANCODE_SCV}")

    @staticmethod
    def running() -> bool:
        """Check if scraping should continue"""
        return os.path.exists(config.RUNNING)

def main():
    try:
        iteration = 0
        while True:
            print(f"Iteration {iteration} started at {datetime.now()}")
            scraper = PriceScraper()
            scraper.load_data()
            scraper.scrape_running()
            sleep(5)
            iteration += 1
    except KeyboardInterrupt:
        WebDriverManager.close_all()

if __name__ == "__main__":
    main()
