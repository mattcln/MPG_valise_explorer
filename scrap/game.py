import logging

from selenium.webdriver.common.by import By

from utils.selenium import get_url


class Game:
    def get_score_tab_info(self):
        """_summary_
        Taking all infos in the score table of a game
        1- Finding the tab element by class - TODO: This might change - be ready to update it.
        2- Taking all "p" tag elements
        3- Returning a dictionnary with all informations - TODO: Order might change. This approach is not robust.
        """
        tableau_scores = self.driver.find_element(By.XPATH, "//*[@class='sc-bcXHqe euGzhE']")
        text_lists = []
        for p in tableau_scores.find_elements(By.TAG_NAME, "p"):
            text_lists.append(p.text)

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

        TODO: J'arrive à récupérer tout les bonus mais je ne sais pas comment faire pour savoir quel équipe en a profité.
        """
        right_modules = self.driver.find_elements(By.XPATH, "//*[@class='sc-bcXHqe sc-dmctIk grPqgW jgCKGU']")
        if len(right_modules) != 3:
            raise AttributeError(
                f"Waiting to find 3 right modules. Found {len(right_modules)}. Have the right modules display changed ?"
            )
        bonus_elements = right_modules[1].find_elements(By.XPATH, "//*[@class='sc-bcXHqe fuCkSG']")
        logging.info(f"Found {len(bonus_elements)} bonus.")
        for bonus in bonus_elements:
            for p in bonus.find_elements(By.TAG_NAME, "p"):
                print(p.text)

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
