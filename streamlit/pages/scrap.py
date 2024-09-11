import time

import streamlit as st
from config.config_reader import get_config
from scrap.league import League
from sql.ddb_matchweek_not_scrapped import get_matchweeks_not_scrapped
from utils.driver import Driver
from utils.log import init_logger

# st.set_page_config(layout="wide")

st.title("Scrapping new games")

selected_league_id = st.text_input(
    "Quelle est l'ID de la ligue que vous souhaitez scrapper ?",
    "XXXXXXXX",
)
selected_results_link = st.text_input(
    "Quelle est le lien des résultats de la ligue en question ?",
    "https://mpg.football/winner/mpg_league_XXXXXXXX/mpg_division_XXXXXXXX_X_X/results",
)

selected_season_nb = st.number_input("Quelle saison ?", step=1)

selected_division = st.number_input("Quelle division ?", step=1)

selected_nb_players = st.slider("Combien de joueurs y a t-il par division ?", 4, 10, 6, step=2)

matchweek_not_scrapped = get_matchweeks_not_scrapped(
    league_id=selected_league_id,
    division=selected_division,
    season_nb=selected_season_nb,
    nb_players=selected_nb_players,
)

if matchweek_not_scrapped:
    st.write(f"I will scrap matchweeks {matchweek_not_scrapped}.")
    if st.button("Scrap games"):
        start_time = time.time()
        init_logger()
        Driver = Driver(docker=False)

        config = get_config()
        user = config["MAIL"]
        password = config["PASSWORD"]

        Driver.logging(user, password)

        league = League(
            driver=Driver.driver,
            league_id=selected_league_id,
            results_link=selected_results_link,
            season_nb=selected_nb_players,
            division=selected_division,
            nb_players=selected_nb_players,
            matchweeks=matchweek_not_scrapped,
        )
        Driver.driver.quit()
        st.write(f"Games scrapped in {time.time() - start_time} seconds.")
else:
    st.write(f"All games are already scrapped.")
