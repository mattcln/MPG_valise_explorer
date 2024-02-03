from config.config_reader import get_config
from utils.driver import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

from bs4 import BeautifulSoup

config = get_config()

Driver
Driver = Driver(docker=config["options"]["is_docker"])

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

Driver.logging(user, password)

stop
