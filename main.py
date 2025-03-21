import pandas as pd
from datetime import datetime
from webdriver_manager import WebDriverManager
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper
import config 
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Optional, Dict, Any
import numpy as np
import re

def clean_price(price_str):
    # Remove non-numeric characters, keeping only digits and period (.)
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    
    # If the cleaned string is empty, return a default value (e.g., 0)
    if cleaned_price == "":
        return "N/A"
    
    return float(cleaned_price)

class PriceScraper:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()
        self.batch_size = 10  # Configurable batch size for saving

    def load_data(self):
        """Load JAN codes and prices from CSV file and update the output DataFrame if necessary."""
        
        try:
            # Read the CSV file with appropriate data types
            jan_df = pd.DataFrame(columns = config.JAN_COLUMNS)
            scraped_df = pd.DataFrame(columns = config.SCRAPED_COLUMNS)

            if Path(config.JANCODE_SCV).exists():
                saved_jan_df = pd.read_csv(config.JANCODE_SCV)
                for col in jan_df:
                    if col in saved_jan_df:
                        jan_df[col] = saved_jan_df[col].astype(str)

            if Path(config.SCRAPED_XLSX).exists():
                saved_scraped_df = pd.read_excel(config.SCRAPED_XLSX)
                for col in scraped_df:
                    if col in saved_scraped_df:
                        scraped_df[col] = saved_scraped_df[col].astype(str)
            else:
                self.df = jan_df
                return

            # Ensure 'JAN' and 'price' columns exist in both dataframes
            if 'JAN' not in jan_df.columns or 'price' not in jan_df.columns:
                print("CSV file is missing required 'JAN' or 'price' columns.")
                return
            
            if 'JAN' not in scraped_df.columns or 'price' not in scraped_df.columns:
                print("Excel file is missing required 'JAN' or 'price' columns.")
                return

            # Ensure the JAN columns match in both dataframes
            if jan_df["JAN"].equals(scraped_df["JAN"]):
                if not jan_df["price"].equals(scraped_df["price"]):
                    scraped_df["price"] = jan_df["price"]
                self.df = scraped_df
            else:
                self.df = jan_df

        except FileNotFoundError as e:
            print(f"File not found: {str(e)}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")



    def process_product(self, index: int, row: pd.Series) -> Dict[str, Any]:
        """Process a single product and return results"""
        jan = str(row['JAN'])
        saved_yahoo_url = str(row['Yahoo Link'])
        saved_rakuten_url = str(row['Rakuten Link'])
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan, saved_yahoo_url)
            rakuten_future = executor.submit(self.rakuten_scraper.scrape_price, jan, saved_rakuten_url)
            
            yahoo_product = yahoo_future.result()
            rakuten_product = rakuten_future.result()

        # Handle Yahoo product price and URL, default to None if not available
        if yahoo_product != "N/A":
            yahoo_price = clean_price(yahoo_product.get("price", "N/A"))
            yahoo_url = yahoo_product.get("url", "N/A")
        else:
            yahoo_price = "N/A"
            yahoo_url = "N/A"

        if rakuten_product != "N/A":
            rakuten_price = rakuten_product.get("price", "N/A")
            rakuten_url = rakuten_product.get("url", "N/A")
        else:
            rakuten_price = "N/A"
            rakuten_url = "N/A"

        return {
            'Yahoo Price': yahoo_price,
            'Yahoo Link': yahoo_url,
            'Rakuten Price': rakuten_price,
            'Rakuten Link': rakuten_url,
            # 'Min Price URL': min_price_url,
            # 'Price Difference': price_diff,
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

                if not not results:                    
                    # Update DataFrame
                    for key, value in results.items():
                        self.df.at[index, key] = value

                # Save results in batches
                if (index + 1) % self.batch_size == 0 or (index + 1) == total_records:
                    self.save_results()
                    self.save_yahoo_urls()
                    sleep(3)

                sleep(1)  # Rate limiting
                
        finally:
            WebDriverManager.close_all()

    def save_results(self) -> None:
        """Save results to Excel file"""
        os.makedirs(os.path.dirname(config.SCRAPED_XLSX), exist_ok=True)
        self.df.to_excel(config.SCRAPED_XLSX, index=False)
        print(f"Progress saved to {config.SCRAPED_XLSX}")

    def save_yahoo_urls(self) -> None:
        """Save JANs and their corresponding Yahoo URLs"""
        urls_df = self.df[config.JAN_COLUMNS].copy()
        urls_df.to_csv(config.JANCODE_SCV, index=False)
        print(f"URLs saved to {config.JANCODE_SCV}")

    @staticmethod
    def running() -> bool:
        """Check if scraping should continue"""
        return os.path.exists(config.RUNNING)

def main():
    try:
        while True:
            scraper = PriceScraper()
            scraper.load_data()
            scraper.scrape_running()
            sleep(10)
    except KeyboardInterrupt:
        WebDriverManager.close_all()

if __name__ == "__main__":
    main()
