import streamlit as st
from config.config_reader import get_config
from sql.ddb_bonus import get_all_players_bonus
from utils.duckdb_helper import get_all_league_ids, get_all_seasons_nb, get_nb_players
from utils.log import init_logger

st.set_page_config(layout="wide")

st.title("Bonus restants")

init_logger()
config = get_config()

league_ids = get_all_league_ids()

selected_league_id = st.selectbox(
    "De quelle ligue voulez-vous connaître les bonus restants ?",
    (league_ids),
)

seasons = get_all_seasons_nb(league_id=selected_league_id)
selected_season = st.selectbox(
    "Quelle saison ?",
    (seasons),
)

selected_division = st.number_input("Quelle division ?", step=1)

nb_players = get_nb_players(league_id=selected_league_id, season_nb=selected_season, division=selected_division)
st.write(f"J'ai trouvé {nb_players} joueurs dans cette saison.")


all_bonus_df = get_all_players_bonus(league_id=selected_league_id, season_nb=selected_season, nb_players=nb_players)

st.write(f"Voici les bonus restants pour les joueurs de la ligue {selected_league_id}: ", all_bonus_df)
