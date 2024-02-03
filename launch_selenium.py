from config.config_reader import get_config
from utils.driver import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

from bs4 import BeautifulSoup

config = get_config()

driver = Driver(docker=config["options"]["is_docker"]).driver

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

# URL of the MPG login page
url = "https://mpg.football/auth/login"


def accept_cookies(driver):
    """_summary_

    :param driver: _description_
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)
            button_XPATH = "//button[@class='sc-furwcr jhwOCG button button--filled button__acceptAll']"
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_XPATH))
            ).click()
            break
        except:
            print("Element not found")
    return driver


def logging(url):
    driver.get(url)
    driver.fullscreen_window()

    accept_cookies(driver)

    driver.implicitly_wait(5)

    driver.find_element(By.ID, "login").send_keys(user)
    driver.implicitly_wait(10)
    driver.find_element(By.ID, "password").send_keys(password)

    buttons = driver.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.text == "Je me connecte":
            button.click()
            print("YES SIR")
    time.sleep(100)

    stop

    soup = BeautifulSoup(driver.page_source, features="lxml")

    print(soup)
    time.sleep(10)


logging(url)
