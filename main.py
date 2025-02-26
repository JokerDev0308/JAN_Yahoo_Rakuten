import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import config
from scripts.yahoo_scraper import YahooScraper
from scripts.rakuten_scraper import RakutenScraper

class PriceScraper:
    def __init__(self):
        self.df = None
        self.yahoo_scraper = YahooScraper()
        self.rakuten_scraper = RakutenScraper()

    def load_data(self):
        self.df = pd.read_csv(config.JANCODE_SCV)

    def scrape_running(self):
        try:
            total_records = len(self.df)
            for index, row in self.df.iterrows():
                while not config.RUNNING:
                    print("Running was stopped")
                    return False

                jan = row['JAN']
                yh_url = row['Yahoo Link']
                print(f"Processing {index + 1}/{total_records}: JAN {jan}")

                with ThreadPoolExecutor(max_workers=2) as executor:
                    yahoo_future = executor.submit(self.yahoo_scraper.scrape_price, jan, yh_url)
                    rakuten_future = executor.submit(self.rakuten_scraper.scrape_price, jan)

                    try:
                        yahoo_product = yahoo_future.result()
                    except Exception as e:
                        print(f"Failed to scrape Yahoo product for JAN {jan}: {e}")
                        yahoo_product = {"price": "N/A", "url": "N/A"}  # default to N/A

                    self.df.at[index, 'Yahoo Price'] = yahoo_product["price"]
                    self.df.at[index, 'Rakuten Price'] = rakuten_future.result()
                    self.calculate_prices_for_row(index)

                    self.df.at[index, 'Yahoo Link'] = yahoo_product["url"]
                    self.df.at[index, 'datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if (index + 1) % 10 == 0 or (index + 1) == total_records:
                    self.save_results()
                    self.save_yh_product_url_to_jancode()

                sleep(1)  # Adjust sleep time

        finally:
            # Ensure all drivers are closed properly
            self.yahoo_scraper.driver.quit()
            self.rakuten_scraper.driver.quit()

    def calculate_prices_for_row(self, index):
        prices = [
            self.df.at[index, 'Yahoo Price'],
            self.df.at[index, 'Rakuten Price']
        ]

        valid_prices = [float(price) for price in prices if price != "N/A" and price is not None]

        if valid_prices:
            min_price = min(valid_prices)
        else:
            min_price = "N/A"

        self.df.at[index, 'Price Difference'] = self.df.at[index, 'price'] - min_price

    def save_results(self):
        column_name_mapping = {
            'JAN': 'JAN（マスタ）',
            'price': '価格（マスタ）',
            'Yahoo Price': 'yahoo_実質価格',
            'Rakuten Price': '楽天_実質価格',
            'Price Difference': '価格差（マスタ価格‐Y!と楽の安い方）',
            'Yahoo Link': '対象リンク（Y!と楽の安い方）',
            'datetime': 'データ取得時間（Y!と楽の安い方）'
        }

        self.df.rename(columns=column_name_mapping, inplace=True)
        os.makedirs(os.path.dirname(config.OUTPUT_XLSX), exist_ok=True)
        self.df.to_excel(config.OUTPUT_XLSX, index=False)

        print(f"Progress saved to {config.OUTPUT_XLSX}")

    def save_yh_product_url_to_jancode(self):
        column_name_mapping = {
            'JAN': 'JAN',
            'price': '価格',
            'Yahoo Link': 'Yahooリンク'
        }

        self.df.rename(columns=column_name_mapping, inplace=True)
        self.df.to_excel(config.OUTPUT_XLSX, index=False)

def main():
    try:
        while config.RUNNING:
            scraper = PriceScraper()
            scraper.load_data()
            scraper.scrape_running()
            sleep(5)
    except KeyboardInterrupt:
        print("Process interrupted by user.")

if __name__ == "__main__":
    main()
