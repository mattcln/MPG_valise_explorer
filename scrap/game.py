import logging
import time

import polars as pl
from selenium.webdriver.common.by import By

from utils.selenium import get_url


class Game:
    tab_info_class = "sc-bcXHqe euGzhE"
    tab_info_class = "sc-bcXHqe sc-dmctIk gmwvWu jMJMOc"  ### Permet d'avoir toutes les infos dans le panneau (dont le numéro de la journée et les buteurs)
    h_goals_class = "sc-bcXHqe fNHVxg"
    h_scorers_class = "sc-bcXHqe gnMozL"
    v_goals_class = "sc-bcXHqe gFNZhX"
    v_scorers_class = "sc-bcXHqe bIJtk"
    right_modules_class = "sc-bcXHqe sc-dmctIk grPqgW jgCKGU"
    bonus_element_class = "sc-bcXHqe fuCkSG"

    # Unused
    goals_class = "sc-bcXHqe crTPxA"
    real_goals_color = "#696773"
    mpg_goals_color = "#45C945"
    save_goals_color = "#EF1728"

    def create_game_id(self):
        """_summary_
        Create a unique id for each game
        """
        return f"{self.league_id}_{self.season_number}_{self.tab_info['h_team']}_{self.tab_info['v_team']}"

    def get_team_id(self, home: bool):
        """_summary_
        Get unique id for each team
        :param home: Is the team home or visitor ?
        :return: _description_
        """
        if home:
            team = "h_team"
        else:
            team = "v_team"
        return f"{self.league_id}_{self.season_number}_{self.tab_info[team]}"

    def get_players_info_df(self, scores_tab_element):
        """_summary_
        Receiving the game scores tab element, this function retrieves all players informations displayed there as a pd df.
        1- 'team_goals_element' is either the full element for home team, either the full element for away team
        2- We get each 'scorer' in the 'team_goals_element' = one element by scorer (one scorer can have multiple goals)
        3- For each of scorer, we get both "p" elements:
            As of 10/02/2024, there are two elements, one looks always empty but might be kept for particularly long names
            We read them both and join them.
            JUST FOUND OUT : it's the minutes of the goals, in case it's a real game and not mpg game
        4- We count the number of 'svg' elemnts = number of things displayed close to his names
        TODO: Find a way to classify those elements (real goals, mpg goals, goals saved etc.), in an other function ?
            For that, I recommend using 'print(scorer.get_attribute("innerHTML"))' and checking in an other window
            to understund each differences.

        Infos are saved as a list of dicts with one element per players in the scores tab element, structured as :
        {name:,nb_goals:,team:}
        Then, returned in a pandas dataframe

        Notes : not working for real games because of the "Dernières confrontation" at the end of the page. We retrieved both tabs
        both goal scorers etc. I didn't find a way to catch only the first tab easily, but should be doable

        :param scores_tab_element: Scores tab selenium element
        """
        players_info = []
        for team in ["home", "visitor"]:
            if team == "home":
                goals_class = self.h_goals_class
                scorers_class = self.h_scorers_class
            else:
                goals_class = self.v_goals_class
                scorers_class = self.v_scorers_class

            for scorer in scores_tab_element.find_elements(
                By.XPATH, f"//*[@class='sc-bcXHqe drrRfn'][1]//*[@class='{goals_class}']//*[@class='{scorers_class}']"
            ):
                scorer_infos = {}
                scorer_infos["name"] = scorer.find_elements(By.TAG_NAME, "p")[1].text
                scorer_infos["real_goals"] = len(scorer.find_elements(By.TAG_NAME, "svg"))
                scorer_infos["team"] = team
                players_info.append(scorer_infos)

        df_players_info = pl.DataFrame(players_info, schema=["name", "real_goals", "mpg_goals", "own_goals", "team"])
        # Fill null, might be a better way to do that
        df_players_info = df_players_info.with_columns(pl.col("real_goals", "mpg_goals", "own_goals").fill_null(0))
        return df_players_info.filter(pl.col("team") == "home"), df_players_info.filter(pl.col("team") == "visitor")

    def get_score_tab_info(self):
        """_summary_
        Taking all infos in the score table of a game
        1- Finding the tab element by class - TODO: This might change - be ready to update it.
        2- Taking all "p" tag elements
        3- Returning a dictionnary with all informations - TODO: Order might change. This approach is not robust.
        """
        tableau_scores = self.driver.find_element(By.XPATH, f"//*[@class='{self.tab_info_class}']")
        df_h_players_info, df_v_players_info = self.get_players_info_df(tableau_scores)

        text_lists = []
        for p in tableau_scores.find_elements(By.TAG_NAME, "p"):
            text_lists.append(p.text)

        tab_info = {}
        teams = tableau_scores.find_elements(By.XPATH, f"//*[@class='sc-dkrFOg sc-hbqYmb gappF ePpVLH']")
        tab_info["h_team"] = teams[0].text.replace(" ", "_")
        tab_info["v_team"] = teams[1].text.replace(" ", "_")

        players = tableau_scores.find_elements(By.XPATH, f"//*[@class='sc-dkrFOg dciwac']")
        tab_info["h_player"] = players[0].text.replace(" ", "_")
        tab_info["v_player"] = players[3].text.replace(" ", "_")

        score = tableau_scores.find_element(By.XPATH, f"//*[@class='sc-dkrFOg sc-jTjUTQ dfVVDa ibfwxi']").text
        tab_info["h_score"] = int(score.split(" ")[0])
        tab_info["v_score"] = int(score.split(" ")[2])

        tab_info["h_real_goals"] = df_h_players_info.select(pl.sum("real_goals"))[0, 0]
        tab_info["v_real_goals"] = df_v_players_info.select(pl.sum("real_goals"))[0, 0]

        tab_info["h_mpg_goals"] = df_h_players_info.select(pl.sum("mpg_goals"))[0, 0]
        tab_info["v_mpg_goals"] = df_v_players_info.select(pl.sum("mpg_goals"))[0, 0]

        tab_info["h_own_goals"] = df_h_players_info.select(pl.sum("own_goals"))[0, 0]
        tab_info["v_own_goals"] = df_v_players_info.select(pl.sum("own_goals"))[0, 0]

        return tab_info

    def get_bonus_info(self):
        """_summary_
        The bonus section has the same class as the "Replacements" and "Badges obtained" modules.
        The aim is to retrieve these three elements, then select the second, which should be the bonuses.

        TODO: J'arrive à récupérer tout les bonus mais je ne sais pas comment faire pour savoir quelle équipe en a profité.
        """
        right_modules = self.driver.find_elements(By.XPATH, f"//*[@class='{self.right_modules_class}']")
        if len(right_modules) != 3:
            raise AttributeError(
                f"Waiting to find 3 right modules. Found {len(right_modules)}. Have the right modules display changed ?"
            )
        bonus_elements = right_modules[1].find_elements(By.XPATH, f"//*[@class='{self.bonus_element_class}']")
        logging.info(f"Found {len(bonus_elements)} bonus.")
        for bonus in bonus_elements:
            for p in bonus.find_elements(By.TAG_NAME, "p"):
                print(p.text)

    def db_insert(self):
        """_summary_
        Saving game informations in file.

        TODO: Append a parquet file for each game (parquet is good for duckdb)
        The SQL Schema is planned as :
        match_id (PK)
        h_teamid (FK)
        v_teamid (FK)
        h_total_goals (int)
        h_mpg_goals (int)
        h_real_goals (int)
        h_own_goals (int)
        h_red_cards (int)
        v_total_goals (int)
        v_mpg_goals (int)
        v_real_goals (int)
        v_own_goals (int)
        v_red_cards (int)
        gameseason_nb (int)
        """
        df = pl.DataFrame(
            {
                "match_id": self.game_id,
                "h_teamid": self.game_id,
                "v_teamid": self.game_id,
                "h_total_goals": self.game_id,
                "h_mpg_goals": self.game_id,
                "h_real_goals": self.game_id,
                "h_own_goals": self.game_id,
                "h_red_cards": self.game_id,
                "v_total_goals": self.game_id,
                "v_mpg_goals": self.game_id,
                "v_real_goals": self.game_id,
                "v_own_goals": self.game_id,
                "v_red_cards": self.game_id,
                "gameseason_nb": self.game_season_number,
            }
        )
        return df

    def __init__(
        self,
        driver,
        league_id: str,
        season_number: int,
        game_season_number: int,
        game_link: str,
    ):
        self.driver = driver
        self.game_link = game_link
        self.league_id = league_id
        self.season_number = season_number
        self.game_season_number = game_season_number

        get_url(driver=self.driver, url=game_link)
        self.tab_info = self.get_score_tab_info()
        self.game_id = self.create_game_id()
        self.h_team_id = self.get_team_id(home=True)
        self.v_team_id = self.get_team_id(home=False)
        print(self.db_insert())
        # self.get_bonus_info()
