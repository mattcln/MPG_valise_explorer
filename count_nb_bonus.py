import duckdb

from config.config_reader import get_config
from sql.duckdb_bonus import get_remaining_bonus_player
from utils.log import init_logger

init_logger()
config = get_config()

league_id = config['league']['league_id']
season_nb = config['league']['season_nb']
team_name = config['team']['name']
team_id = f"{league_id}_{season_nb}_{team_name}"

remaining_bonus = get_remaining_bonus_player(team_id=team_id, nb_players=6)

print(f"Remaining bonuses of {team_name} are:")
for bonus in remaining_bonus:
    print(f"{bonus} : {remaining_bonus[bonus]}")
