from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Driver:
    chrome_options = Options()

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
                break
            except:
                print("Element not found")
