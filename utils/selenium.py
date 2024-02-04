def get_url(driver, url, wait_time=2):
    driver.implicitly_wait(wait_time)
    driver.get(url)
    driver.fullscreen_window()
