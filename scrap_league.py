from config.config_reader import get_config
from scrap.league import League
from utils.driver import Driver
from utils.log import init_logger

init_logger()
config = get_config()

Driver = Driver(docker=config["options"]["is_docker"])

# Define your credentials
user = config["credentials"]["username"]
password = config["credentials"]["password"]

Driver.logging(user, password)

league = League(
    driver=Driver.driver,
    results_link="https://mpg.football/winner/mpg_league_KNCUPJTY/mpg_division_KNCUPJTY_1_1/results",
    season_nb=1,
    division=1,
)
