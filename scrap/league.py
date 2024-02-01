class League:
    def get_all_week_games_link(self):
        "https://mpg.football/mpg-match/league/mpg_division_NKU1UAPG_5_1/mpg_division_match_NKU1UAPG_5_1_12"
        possible_links = []
        for division in range(self.nb_division):
            code_number_divison = f"{self.game_code}_{self.season_number}_{division+1}"
            base_link = f"https://mpg.football/mpg-match/league/mpg_division_{code_number_divison}/mpg_division_match_{code_number_divison}"
            for week_nb in range(self.nb_games):
                for i in range(9):
                    for j in range(9):
                        for k in range(9):
                            possible_links.append(
                                f"{base_link}_{week_nb+1}_{i}_{j}_{k}"
                            )
            # print(possible_links)
        print(f"nb links found : {len(possible_links)}")
        return possible_links

    def get_nb_games(self):
        return (self.nb_players_per_league - 1) * 2

    def get_game_code_from_results_link(self):
        return self.results_link.split("/")[4][-8:]

    def __init__(
        self,
        session: str,
        results_link: str,
        season_number: str,
        nb_division: int,
        nb_players_per_league: int,
    ):
        self.session = session
        self.results_link = results_link
        self.game_code = self.get_game_code_from_results_link()
        self.season_number = season_number
        self.nb_division = nb_division
        self.nb_players_per_league = nb_players_per_league
        self.nb_games = self.get_nb_games()
