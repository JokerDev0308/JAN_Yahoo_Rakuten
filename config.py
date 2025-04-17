# config.py
HEADLESS = True  # Set to False if you want to see browser running
TIMEOUT = 10  # Selenium wait timeout
CHROMEDRIVER_PATH = "drivers/chromedriver-linux64/chromedriver"
JANCODE_SCV = 'data/jan_codes.csv'
JANCODE_YH_AFFILI_SCV = 'data/jan_YH_afiil_codes.csv'
SCRAPED_XLSX = 'data/scraped_prices.xlsx'

RUNNING = "tmp/running"
WAITING = False
CURRENT_USER = None
LOGIN_STATE = {}

JAN_COLUMNS = ['JAN', 'price', 'Yahoo Link', 'Rakuten Link']
SCRAPED_COLUMNS = ['JAN', 'price', 'Yahoo Price','Yahoo Link', 'Rakuten Price', 'Rakuten Link', 'datetime']
OUTPUT_COLUMNS = ['JAN（マスタ）', '価格（マスタ）', 'yahoo_実質価格', '楽天_実質価格', '価格差（マスタ価格‐Y!と楽の安い方）', '対象リンク（Y!と楽の安い方）', 'データ取得時間（Y!と楽の安い方）']
