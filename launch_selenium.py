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

games_example = [
    "https://mpg.football/mpg-match/league/mpg_division_KWGFGJUM_1_1/mpg_division_match_KWGFGJUM_1_1_3_5_8_7",
    "https://mpg.football/mpg-match/league/mpg_division_KWGFGJUM_1_1/mpg_division_match_KWGFGJUM_1_1_5_1_0_7",  ### Avec bonus !!!
    "https://mpg.football/mpg-match/league/mpg_division_KWGFGJUM_1_1/mpg_division_match_KWGFGJUM_1_1_8_3_7_4",
    "https://mpg.football/championship-match/mpg_championship_match_2376969",
]

game = Game(driver=Driver.driver, league_id="KWGFGJUM", season_number=1, game_link=games_example[1], game_season_nb=5)
time.sleep(10)
stop
