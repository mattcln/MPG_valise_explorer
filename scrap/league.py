import time

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrap.game import Game
from utils.selenium import get_url


class League:
    def get_driver_matchweek(self) -> int:
        """
        Return on which matchweek driver is pointing
        matchweek_string ex : "Résultat J.5 /14"
        """
        matchweek_string = self.driver.find_element(By.XPATH, f"//*[@class='sc-dkrFOg iKscri']").text
        return int(matchweek_string.split(".")[1].split("/")[0].strip())

    def switch_matchweek(self, next=True):
        """
        Switch driver to the previous or next matchweek

        :param next: switch to next matchweek if true, previous otherwise, defaults to True
        """
        if next:
            instance = 1
        else:
            instance = 0

        button_XPATH = "//*[@class='sc-ipEyDJ sc-hLirLb xQelv ciiqSe']"
        self.driver.find_elements(By.XPATH, button_XPATH)[instance].click()

    def _scrap_matchweek_games(self):
        """
        Scrap games on the current results driver page

        TODO: Comment faire pour scrapper les matchs un par un, sachant que quand je clique sur un match
            je perds la journée à laquelle j'étais juste avant... ?
            => Soit réussir à ouvrir dans un nouvel onglet
            => Soit refaire tout le trajet pour prendre une autre game à chaque fois...
        """
        games_XPATH = "//*[@class='sc-bcXHqe sc-gswNZR juGOxZ cjNVfZ']"
        games = self.driver.find_elements(By.XPATH, games_XPATH)
        for game in games:
            time.sleep(99999)
            ActionChains(self.driver).key_down(Keys.LEFT_CONTROL).pause(1).click(game).key_up(Keys.LEFT_CONTROL).perform()
            time.sleep(100)
            # game.click()
        print(len(games))
        stop

    def scrap_league(self, matchweeks: list = []):
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
        matchweek_start = self.get_driver_matchweek()
        matchweek = 99
        while matchweek + 1 != matchweek_start:
            matchweek = self.get_driver_matchweek()
            if matchweek in matchweeks or not matchweeks:
                self._scrap_matchweek_games()
                matchweeks_scrapped.append(matchweek)
            self.switch_matchweek()
        print(f"matchweek scrapped : {matchweeks_scrapped}")
        print(time.sleep(150))
        stop

    def __init__(
        self,
        driver,
        results_link: str,
        season_nb: str,
        division: int,
    ):
        self.driver = driver
        self.season_nb = season_nb
        self.division = division

        get_url(driver=self.driver, url=results_link)

        self.scrap_league(matchweeks=[7, 9, 10])
