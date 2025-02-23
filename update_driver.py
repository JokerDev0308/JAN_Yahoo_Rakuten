import os
import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_driver_path = config.CHROMEDRIVER_PATH

# Set up Chrome options for headless mode
options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode
options.add_argument("--no-sandbox")  # Disable sandbox (required for headless mode)
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources issue on VPS
options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (not needed in headless)

# Setup the ChromeDriver service
service = Service(chrome_driver_path)

# Initialize the WebDriver with the service and options
driver = webdriver.Chrome(service=service, options=options)

# Open a website (Google in this case)
driver.get("https://www.google.com")
print("ChromeDriver is updated and working!")

# Close the driver
driver.quit()
