import requests
from bs4 import BeautifulSoup
from config import TIMEOUT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RakutenScraper:
    def __init__(self):
        # URL for form submission
        self.base_url = "https://search.rakuten.co.jp/search/mall"

    def scrape_price(self, jan_code):
        try:
            # Data from the form, including the JAN code and other parameters
            form_data = {
                "sitem": jan_code,  # JAN code
                "p": "1",  # Page number
                "s": "11",  # Sorting order
                "used": "0",  # Used items filter
                "set": "priceDisplay",  # Price display setting
                "_mp": '{"display_options:price":2,"pricedisplay":0}',  # Display options in the form
                "pd": "0"  # Assuming the checkbox is checked (if you need it unchecked, set pd to 1)
            }

            # Send the GET request with form data
            response = requests.get(self.base_url, params=form_data, timeout=10)

            print("===========================")
            print(response)
            print("===========================")

            # If the request was successful, process the response
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Look for the price element (similar to the original scraping logic)
                items = soup.select(".final-price")

                print(items)

                # If price elements are found, extract the first one
                if items:
                    price = items[0].get_text(strip=True).translate(str.maketrans("", "", "円,"))
                    print(price)
                    return price

            return "N/A"

        except Exception as e:
            # Log the error and return a default value if something fails
            logger.error(f"Search by JAN failed: {e}")
            return "N/A"


    def close(self):
        # No need to close a request session as there is no persistent connection
        pass
