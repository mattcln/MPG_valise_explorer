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

# Load league options
league_id = config["league"]["league_id"]
results_link = config["league"]["results_link"]
season_nb = config["league"]["season_nb"]
division = config["league"]["division"]
nb_players = config["league"]["nb_players"]

Driver.logging(user, password)

league = League(
    driver=Driver.driver,
    league_id=league_id,
    results_link=results_link,
    season_nb=season_nb,
    division=division,
    nb_players=nb_players,
    matchweeks=[1]
)
