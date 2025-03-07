# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 1  # Selenium wait timeout
CHROMEDRIVER_PATH = "drivers/chromedriver-linux64/chromedriver"
JANCODE_SCV = 'data/jan_codes.csv'
JANCODE_YH_AFFILI_SCV = 'data/jan_YH_afiil_codes.csv'
SCRAPED_XLSX = 'data/scraped_prices.xlsx'

RUNNING = "tmp/running"
WAITING = False
CURRENT_USER = None
LOGIN_STATE = {}

JAN_COLUMNS = ['JAN', 'price', 'Yahoo! Link', 'Rakuten Link']
SCRAPED_COLUMNS = ['JAN', 'price', 'Yahoo! Price', 'Rakuten Price', 'datetime']
OUTPUT_COLUMNS = ['JAN', 'price', 'Yahoo! Price', 'Rakuten Price', 'Min Price', 'Min Link', 'datetime']
