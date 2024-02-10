import logging

import pandas as pd
from selenium.webdriver.common.by import By

from utils.selenium import get_url


class Game:
    tab_info_class = "sc-bcXHqe euGzhE"
    tab_info_class = "sc-bcXHqe sc-dmctIk gmwvWu jMJMOc"  ### Permet d'avoir toutes les infos dans le panneau (dont le numéro de la journée et les buteurs)
    home_goals_class = "sc-bcXHqe fNHVxg"
    home_scorers_class = "sc-bcXHqe gnMozL"
    away_goals_class = "sc-bcXHqe gFNZhX"
    away_scorers_class = "sc-bcXHqe bIJtk"
    right_modules_class = "sc-bcXHqe sc-dmctIk grPqgW jgCKGU"
    bonus_element_class = "sc-bcXHqe fuCkSG"

    # Unused
    goals_class = "sc-bcXHqe crTPxA"
    real_goals_color = "#696773"
    mpg_goals_color = "#45C945"
    save_goals_color = "#EF1728"

    def get_players_info_df(self, scores_tab_element):
        """_summary_
        Receiving the game scores tab element, this function retrieves all players informations displayed there as a pd df.
        1- 'team_goals_element' is either the full element for home team, either the full element for away team
        2- We get each 'scorer' in the 'team_goals_element' = one element by scorer (one scorer can have multiple goals)
        3- For each of scorer, we get both "p" elements:
            As of 10/02/2024, there are two elements, one looks always empty but might be kept for particularly long names
            We read them both and join them.
        4- We count the number of 'svg' elemnts = number of things displayed close to his names
        TODO: Find a way to classify those elements (real goals, mpg goals, goals saved etc.), in an other function ?
            For that, I recommend using 'print(scorer.get_attribute("innerHTML"))' and checking in an other window
            to understund each differences.

        Infos are saved as a list of dicts with one element per players in the scores tab element, structured as :
        {name:,nb_goals:,team:}
        Then, returned in a pandas dataframe

        :param scores_tab_element: Scores tab selenium element
        :param home_player: are we looking for the home or away player ?
        """
        players_info = []
        for team in ["home", "away"]:
            if team == "home":
                goals_class = self.home_goals_class
                scorers_class = self.home_scorers_class
            else:
                goals_class = self.away_goals_class
                scorers_class = self.away_scorers_class

            team_goals_element = scores_tab_element.find_element(By.XPATH, f"//*[@class='{goals_class}']")

            for scorer in team_goals_element.find_elements(By.XPATH, f"//*[@class='{scorers_class}']"):
                scorer_infos = {}
                scorer_names_element = scorer.find_elements(By.TAG_NAME, "p")
                all_scorer_names = []
                for scorer_name in scorer_names_element:
                    all_scorer_names.append(scorer_name.text)
                scorer_infos["name"] = " ".join(all_scorer_names).strip()
                scorer_infos["nb_goals"] = len(scorer.find_elements(By.TAG_NAME, "svg"))
                scorer_infos["team"] = team
                players_info.append(scorer_infos)
        return pd.DataFrame(players_info)

    def get_score_tab_info(self):
        """_summary_
        Taking all infos in the score table of a game
        1- Finding the tab element by class - TODO: This might change - be ready to update it.
        2- Taking all "p" tag elements
        3- Returning a dictionnary with all informations - TODO: Order might change. This approach is not robust.
        """
        tableau_scores = self.driver.find_element(By.XPATH, f"//*[@class='{self.tab_info_class}']")
        players_info = self.get_players_info_df(tableau_scores)
        text_lists = []
        for p in tableau_scores.find_elements(By.TAG_NAME, "p"):
            text_lists.append(p.text)

        print(text_lists)
        stop
        tab_info = {}
        tab_info["home_team"] = text_lists[0]
        tab_info["home_player"] = text_lists[1]
        tab_info["home_score"] = int(text_lists[4].split(" ")[0])
        tab_info["ext_team"] = text_lists[6]
        tab_info["ext_player"] = text_lists[7]
        tab_info["ext_score"] = int(text_lists[4].split(" ")[2])

        logging.info(f"Informations found in score tab : '{tab_info}'.")

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

    def sql_insert(self):
        """_summary_
        Inserting retrieved informations in the game sql db.

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
        pass

    def __init__(
        self,
        driver,
        game_link: str,
    ):
        self.driver = driver
        self.game_link = game_link
        get_url(driver=self.driver, url=game_link)
        self.tab_info = self.get_score_tab_info()
        self.get_bonus_info()
