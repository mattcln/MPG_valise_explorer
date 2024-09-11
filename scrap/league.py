from selenium.webdriver.common.by import By

from scrap.game import Game
from utils.selenium_helper import get_url


class League:
    def get_driver_to_season_nb(self, season_nb: int):
        """
        Switch driver to the correct season number
        Switch le driver à la bonne saison. Le lien des résultats donne toujours la dernière saison en base.
        On doit faire le switch entre chaque matchs.

        1. Clique sur la liste drop-down des saisons
        2. Créé une liste avec toutes les options du drop-down en question
        3. Les checks tous un par un jusqu'à avoir la bonne saison
        4. Raise une erreur si la saison demandée n'est pas trouvée

        :param season_nb: season_nb to switch to
        """
        get_url(driver=self.driver, url=self.results_link)

        button_class = "sc-ipEyDJ sc-ksBlkl gkaufK hrtLZX"
        self.driver.find_element(By.XPATH, f"//*[@class='{button_class}']").click()
        drop_down_class = "sc-hBxehG kLcwBk"
        drop_down_element = self.driver.find_element(By.XPATH, f"//*[@class='{drop_down_class}']")

        drop_down_options = drop_down_element.find_elements(By.TAG_NAME, "li")

        for option in drop_down_options:
            current_season_nb = int(option.find_element(By.TAG_NAME, "p").text.split(" ")[1])
            if current_season_nb == season_nb:
                option.click()
                return True
        raise ValueError(f"Je n'ai jamais trouvé la saison {season_nb}. J'ai échoué désolé.")

    def get_driver_matchweek(self) -> int:
        """
        Return on which matchweek driver is pointing
        matchweek_string ex : "Résultat J.5 /14"
        """
        matchweek_string = self.driver.find_element(By.XPATH, f"//*[@class='sc-bcXHqe eDkcLt']").text
        return int(matchweek_string.split(" ")[1])

    def get_driver_to_matchweek(self, matchweek: int):
        """
        Switch driver to the previous or next matchweek

        button XPATH is not the same when executing with Selenium and in local. (why ?)
        => Might change soon again

        :param next: switch to next matchweek if true, previous otherwise, defaults to True
        """
        # get_url(driver=self.driver, url=self.results_link)

        button_XPATH = "//*[@class='sc-ipEyDJ sc-kTxHUi xQelv droxzY']"
        while self.get_driver_matchweek() != matchweek:
            self.driver.find_elements(By.XPATH, button_XPATH)[1].click()

    def get_match_element_url(self, match_element_nb: int) -> str:
        """
        Click on the n-th match element on the current driver page
        Returns the game link url
        """
        games_XPATH = "//*[@class='sc-bhNKFk iZBBjh']"
        self.driver.find_elements(By.XPATH, games_XPATH)[match_element_nb].click()
        return self.driver.current_url

    def scrap_game(self, game_link: str, matchweek: int):
        Game(
            driver=self.driver,
            league_id=self.league_id,
            season_nb=self.season_nb,
            division=self.division,
            game_link=game_link,
            matchweek=matchweek,
        )

    def scrap_league(self, season_nb, matchweeks: list = []):
        """
        Scrap games from a specific league. By default all matches of the season
        otherwise only the matches in 'matchweeks' list

        1- Set 'matchweek_start' to the current matchweek (to know when you've made a loop)
        2- While as matchweek + 1 is not equal to matchweek_start, we continue scrapping.
            If it is, this means we'll start again from the first matchweek we traversed.
            3- If the current matchweek is in the list,
                or if matchweek is empty (meaning we want to scrap all games), we scrap it.

        :param matchweeks: list of int of matchweeks to scrap, defaults to []
        """
        matchweeks_scrapped = []
        for matchweek in matchweeks:
            for match_element_nb in range(int(self.nb_players / 2)):
                self.get_driver_to_season_nb(season_nb)
                self.get_driver_to_matchweek(matchweek)
                game_link = self.get_match_element_url(match_element_nb)
                self.scrap_game(game_link, matchweek)
            matchweeks_scrapped.append(matchweek)
        print(f"matchweek scrapped : {matchweeks_scrapped}")

    def __init__(
        self,
        driver,
        league_id: str,
        results_link: str,
        season_nb: str,
        division: int,
        nb_players: int,
        matchweeks: list,
    ):
        self.driver = driver
        self.league_id = league_id
        self.results_link = results_link
        self.season_nb = int(season_nb)
        self.division = division
        self.nb_players = nb_players

        get_url(driver=self.driver, url=results_link)

        self.scrap_league(season_nb=self.season_nb, matchweeks=matchweeks)
