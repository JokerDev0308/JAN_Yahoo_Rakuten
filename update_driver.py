import os
import config

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

chrome_driver_path = config.CHROMEDRIVER_PATH

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)


driver.get("https://www.google.com")
print("ChromeDriver is updated and working!")
driver.quit()