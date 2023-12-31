import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
from config.config_reader import get_config

config = get_config()

# Define your credentials
username = config["credentials"]["username"]
password = config["credentials"]["password"]

# URL of the MPG login page
url = "https://mpg.football/auth/login"

def get_session_auth(session):
    response = session.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        print("Authentication successful!")
    else:
        print(f"Authentication failed. Status code: {response.status_code}")


class league:
    def get_all_week_games_link(self):
        "https://mpg.football/mpg-match/league/mpg_division_NKU1UAPG_5_1/mpg_division_match_NKU1UAPG_5_1_12_1_2_1"
        for division in range(self.nb_division):
            code_number_divison = f"{self.game_code}_{self.season_number}_{division+1}"
            base_link = f"https://mpg.football/mpg-match/league/mpg_division_{code_number_divison}/mpg_division_match_{code_number_divison}"
            possible_links = []
            for week_nb in range(self.nb_games):
                for i in range(9):
                    for j in range(9):
                        for k in range(9):
                            possible_links.append(f"{base_link}_{week_nb}_{i}_{j}_{k}")
            print(possible_links)
            print(len(possible_links))

    def get_nb_games(self):
        return (self.nb_players_per_league - 1) * 2

    def get_game_code_from_result_link(self):
        return self.result_link.split("/")[4][-8:]

    def __init__(
        self,
        session: str,
        result_link: str,
        season_number: str,
        nb_division: int,
        nb_players_per_league: int,
    ):
        self.session = session
        self.result_link = result_link
        self.game_code = self.get_game_code_from_result_link()
        self.season_number = season_number
        self.nb_division = nb_division
        self.nb_players_per_league = nb_players_per_league
        self.nb_games = self.get_nb_games()


session = requests.Session()
get_session_auth(session)

response = session.get(
    "https://mpg.football/league/mpg_league_NKU1UAPG/mpg_division_NKU1UAPG_5_2/results"
)
multiligue_results = (
    "https://mpg.football/league/mpg_league_NKU1UAPG/mpg_division_NKU1UAPG_5_2/results"
)
MPG_multiligue = league(
    session, multiligue_results, season_number=5, nb_division=2, nb_players_per_league=8
)
MPG_multiligue.get_all_week_games_link()
