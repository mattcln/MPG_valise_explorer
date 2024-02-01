import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver

# from bs4 import BeautifulSoup
# import re
from scrap.league import League
from scrap.game import Game
from config.config_reader import get_config

config = get_config()

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

# URL of the MPG login page
url = "https://mpg.football/auth/login"

driver = webdriver.Edge()
driver.get(url)
