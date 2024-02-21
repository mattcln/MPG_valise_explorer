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

    h_bonus_class = "sc-bcXHqe fhMvyb"
    v_bonus_class = "sc-bcXHqe jSNkIw"

    export_game_path = "export/games.parquet"
    export_bonus_path = "export/bonus.parquet"

    # Unused
    goals_class = "sc-bcXHqe crTPxA"
    real_goals_color = "#696773"
    mpg_goals_color = "#45C945"
    save_goals_color = "#EF1728"

    def create_game_id(self):
        """_summary_
        Create a unique id for each game
        """
        h_team_reduced = self.tab_info["h_team"][:4].strip()
        v_team_reduced = self.tab_info["v_team"][:4].strip()
        return f"{self.league_id}_{self.season_number}_{self.division}_{h_team_reduced}_{v_team_reduced}"

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

        1-On récupère tout les éléments avec le "bonus_element_class" qui correspond à une brique d'une équipe
        2-Ces élements prennent autant les briques de "Bonus posés" que de "Badges optenus"
            => On garde seulement les deux premiers (Bonus h team et bonus v team)
        3- sc-bcXHqe fhMvyb => H | sc-bcXHqe jSNkIw => V
        """
        h_bonus = self.driver.find_elements(By.XPATH, f"//*[@class='{self.h_bonus_class}']")
        h_bonus_list = []
        for bonus in h_bonus:
            h_bonus_list.append(bonus.find_element(By.TAG_NAME, "p").text)

        v_bonus = self.driver.find_elements(By.XPATH, f"//*[@class='{self.v_bonus_class}']")
        v_bonus_list = []
        for bonus in v_bonus:
            v_bonus_list.append(bonus.find_element(By.TAG_NAME, "p").text)

        print(f"H bonus : {h_bonus_list}")
        print(f"V bonus : {v_bonus_list}")
        stop

    def db_game_insert(self):
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
                "h_teamid": self.h_team_id,
                "v_teamid": self.v_team_id,
                "h_total_goals": self.h_total_goals,
                "h_mpg_goals": self.h_mpg_goals,
                "h_real_goals": self.h_real_goals,
                "h_own_goals": self.h_own_goals,
                "h_red_cards": self.h_red_cards,
                "v_total_goals": self.v_total_goals,
                "v_mpg_goals": self.v_mpg_goals,
                "v_real_goals": self.v_real_goals,
                "v_own_goals": self.v_own_goals,
                "v_red_cards": self.v_red_cards,
                "game_season_nb": self.game_season_nb,
            }
        )
        try:
            historical_df = pl.read_parquet(self.export_game_path)
            df = historical_df.vstack(df)
        except FileNotFoundError:
            print("No history file found.")
        df.write_parquet(self.export_game_path)
        print(df)

    def db_bonus_insert(self):
        """_summary_
        Saving bonus informations in file.

        TODO: Append a parquet file for each game (parquet is good for duckdb)
        The SQL Schema is planned as :
        match_id (FK)
        h_valise (bool)
        h_ubereats (bool)
        h_suarez (bool)
        h_zahia (bool)
        h_miroir (bool)
        h_chapron (bool)
        h_tonton (bool)
        h_decat (bool)
        v_valise (bool)
        v_ubereats (bool)
        v_suarez (bool)
        v_zahia (bool)
        v_miroir (bool)
        v_chapron (bool)
        v_tonton (bool)
        v_decat (bool)
        """
        df = pl.DataFrame(
            {
                "match_id": self.game_id,
                "h_valise": self.bonus["h_valise"],
                "h_ubereats": self.bonus["h_ubereats"],
                "h_suarez": self.bonus["h_suarez"],
                "h_zahia": self.bonus["h_zahia"],
                "h_miroir": self.bonus["h_miroir"],
                "h_chapron": self.bonus["h_chapron"],
                "h_tonton": self.bonus["h_tonton"],
                "h_decat": self.bonus["h_decat"],
                "v_valise": self.bonus["v_valise"],
                "v_ubereats": self.bonus["v_ubereats"],
                "v_suarez": self.bonus["v_suarez"],
                "v_zahia": self.bonus["v_zahia"],
                "v_miroir": self.bonus["v_miroir"],
                "v_chapron": self.bonus["v_chapron"],
                "v_tonton": self.bonus["v_tonton"],
                "v_decat": self.bonus["v_decat"],
            }
        )
        try:
            historical_df = pl.read_parquet(self.export_bonus_path)
            df = historical_df.vstack(df)
        except FileNotFoundError:
            print("No history file found.")
        df.write_parquet(self.export_bonus_path)
        print(df)

    def __init__(
        self,
        driver,
        league_id: str,
        season_number: int,
        division: int,
        game_season_nb: int,
        game_link: str,
    ):
        """_summary_

        :param driver: Selenium driver
        :param league_id: MPG league unique ID (eg: 'KWGFGJUM')
        :param season_number: Season number
        :param division: Division
        :param game_season_nb: How many matches has it been th
        is season?
        :param game_link: mpg full link
        """
        self.driver = driver
        self.game_link = game_link
        self.league_id = league_id
        self.season_number = season_number
        self.division = division
        self.game_season_nb = game_season_nb

        get_url(driver=self.driver, url=game_link)
        self.get_bonus_info()
        self.tab_info = self.get_score_tab_info()

        self.game_id = self.create_game_id()
        self.h_team_id = self.get_team_id(home=True)
        self.v_team_id = self.get_team_id(home=False)
        self.h_total_goals = self.tab_info["h_mpg_goals"] + self.tab_info["h_real_goals"]
        self.h_mpg_goals = self.tab_info["h_mpg_goals"]
        self.h_real_goals = self.tab_info["h_real_goals"]
        self.h_own_goals = 0
        self.h_red_cards = 0
        self.v_total_goals = self.tab_info["v_mpg_goals"] + self.tab_info["v_real_goals"]
        self.v_mpg_goals = self.tab_info["v_mpg_goals"]
        self.v_real_goals = self.tab_info["v_real_goals"]
        self.v_own_goals = 0
        self.v_red_cards = 0
        self.db_game_insert()
