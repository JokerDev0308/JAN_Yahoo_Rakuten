# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 5  # Selenium wait timeout
CHROMEDRIVER_PATH = "drivers/chromedriver-linux64/chromedriver"
JANCODE_SCV = 'data/jan_codes.csv'
JANCODE_YH_AFFILI_SCV = 'data/jan_YH_afiil_codes.csv'
OUTPUT_XLSX = 'data/scraped_prices.xlsx'

RUNNING = "tmp/running"
WAITING = False