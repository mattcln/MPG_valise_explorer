def get_url(driver, url, wait_time=2):
    driver.implicitly_wait(wait_time)
    driver.get(url)
    driver.implicitly_wait(wait_time)
    driver.fullscreen_window()
