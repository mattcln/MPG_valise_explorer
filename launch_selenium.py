import logging
import time

from selenium.webdriver.support import expected_conditions as EC

from config.config_reader import get_config
from scrap.game import Game
from utils.driver import Driver
from utils.log import init_logger

init_logger()
config = get_config()

Driver = Driver(docker=config["options"]["is_docker"])

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

Driver.logging(user, password)

game = Game(
    driver=Driver.driver,
    game_link="https://mpg.football/mpg-match/league/mpg_division_KWGFGJUM_1_1/mpg_division_match_KWGFGJUM_1_1_3_5_8_7",  # https://mpg.football/mpg-match/league/mpg_division_KWGFGJUM_1_1/mpg_division_match_KWGFGJUM_1_1_15_4_4_3
)
time.sleep(10)
stop
