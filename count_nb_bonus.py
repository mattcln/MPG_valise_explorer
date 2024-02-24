import duckdb

from config.config_reader import get_config
from sql.duckdb_bonus import get_remaining_bonus_player
from utils.log import init_logger

init_logger()
config = get_config()

get_remaining_bonus_player("KWGFGJUM_1_Frappe_de_Verratti", 8)
