from config.config_reader import get_config
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

docker = False

chrome_options = Options()

if docker:
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

config = get_config()

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

# URL of the MPG login page
url = "https://mpg.football/auth/login"

driver.get(url)

soup = BeautifulSoup(driver.page_source, features="lxml")

print(soup)
time.sleep(10)
