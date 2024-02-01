from bs4 import BeautifulSoup


class Game:
    def get_players_name(self):
        soup = BeautifulSoup(self.game_html, "html.parser")

        # Find the <p> element by class
        p_element = soup.find_all("p", class_="sc-dkrFOg sc-hLBbgP bnFDfZ jbaWzw")

        # Get the text content of the <p> element
        text_content = p_element
        print(text_content)

    def get_game_data(self):
        data = self.session.get(self.game_link)
        return data.text

    def __init__(
        self,
        session: str,
        game_link: str,
    ):
        self.session = session
        self.game_link = game_link
        self.game_html = self.get_game_data()
