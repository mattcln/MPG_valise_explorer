from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class Driver:
    chrome_options = Options()
    url = "https://mpg.football/auth/login"

    def __init__(self, docker=True) -> None:
        if docker:
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.page_load_strategy = "normal"

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options,
        )

    def accept_cookies(self):
        """_summary_

        :param driver: _description_
        """
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                self.driver.switch_to.frame(iframe)
                button_XPATH = "//button[@class='sc-furwcr jhwOCG button button--filled button__acceptAll']"
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, button_XPATH))
                ).click()
                print("BINGO COOKIES")
                break
            except:
                print("Element not found")

    def logging(self, user, password):
        self.driver.get(self.url)
        self.driver.fullscreen_window()

        self.accept_cookies()

        self.driver.implicitly_wait(10)

        self.driver.find_element(By.ID, "login").send_keys(user)
        self.driver.find_element(By.ID, "password").send_keys(password)

        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.text == "Je me connecte":
                print("FOUND IT")
                button.click()

        time.sleep(100)
