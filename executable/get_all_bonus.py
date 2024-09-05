from config.config_reader import get_config
from sql.ddb_bonus import get_all_players_bonus
from utils.log import init_logger

init_logger()
config = get_config()

all_bonus_df = get_all_players_bonus(
    league_id=config["LEAGUE_ID"], season_nb=config["SEASON_NB"], nb_players=config["NB_PLAYERS"]
)

print(all_bonus_df)
