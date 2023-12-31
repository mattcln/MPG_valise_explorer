import requests
from requests.auth import HTTPBasicAuth
# from bs4 import BeautifulSoup
# import re
from scrap.league import League
from config.config_reader import get_config

config = get_config()

# Define your credentials
username = config["credentials"]["username"]
password = config["credentials"]["password"]

# URL of the MPG login page
url = "https://mpg.football/auth/login"

def get_session_auth(session):
    """
    This function authentificates the session using username and password from the config.json.

    :param session: Requests session
    """
    response = session.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        print("Authentication successful!")
    else:
        print(f"Authentication failed. Status code: {response.status_code}")

session = requests.Session()
get_session_auth(session)

MPG_multiligue = League(
    session,
    results_link=config["season"]["results_link"],
    season_number=config["season"]["season_number"],
    nb_division=config["season"]["nb_division"],
    nb_players_per_league=config["season"]["nb_players_per_league"]
)

MPG_multiligue.get_all_week_games_link()
