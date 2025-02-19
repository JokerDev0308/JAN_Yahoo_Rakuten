import requests
from bs4 import BeautifulSoup
# import pandas as pd
import time

# Function to scrape Yahoo Auctions
def scrape_yahoo_auctions(jan_code):
    url = f"https://shopping.yahoo.co.jp/search/search?p={jan_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    prices = []
    
    for item in soup.select(".Product__price"):
        price_text = item.get_text(strip=True).replace("円", "").replace(",", "")
        if price_text.isdigit():
            prices.append(int(price_text))
    
    return min(prices) if prices else "Not Found"

# Function to scrape Rakuten
def scrape_rakuten(jan_code):
    url = f"https://search.rakuten.co.jp/search/mall/{jan_code}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    prices = []
    
    for item in soup.select(".searchresultitem .important"):
        price_text = item.get_text(strip=True).replace("円", "").replace(",", "")
        if price_text.isdigit():
            prices.append(int(price_text))
    
    return min(prices) if prices else "Not Found"

# Load JAN codes from an Excel file
# file_path = "product_list.xlsx"  # Update with your actual file path
# df = pd.read_excel(file_path)

# Assuming the JAN codes are in a column named 'JAN Code'
# jan_codes = df["JAN Code"].tolist()

jan_codes = [4960759910639]

# Create a results list
results = []

for jan_code in jan_codes:
    print(f"Scraping JAN: {jan_code}...")
    
    yahoo_price = scrape_yahoo_auctions(jan_code)
    rakuten_price = scrape_rakuten(jan_code)
    print("JAN Code=", jan_code, "  Yahoo Price=", yahoo_price, "  Rakuten Price=", rakuten_price)
    results.append({"JAN Code": jan_code, "Yahoo Price": yahoo_price, "Rakuten Price": rakuten_price})
    
    time.sleep(2)  # Sleep to avoid getting blocked

# # Save results to a new Excel file
# output_df = pd.DataFrame(results)
# output_df.to_excel("scraped_prices.xlsx", index=False)


print("=======================")
print(results)
print("=======================")

print("Scraping complete! Results saved to scraped_prices.xlsx.")
