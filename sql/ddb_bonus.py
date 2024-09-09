import duckdb
import polars as pl

from utils.bonus import bonus

game_file_path = "exports/games.parquet"
bonus_file_path = "exports/bonus.parquet"


def get_json_bonus():
    return bonus


def get_total_team_bonus_played(team_id: str) -> dict:
    results = []
    team_id = team_id.replace("'", "''")
    for prefix in ["h_", "v_"]:
        results.append(
            duckdb.query(
                f"""
        SELECT
            SUM({prefix}valise) AS valise, 
            SUM({prefix}ubereats) AS ubereats,
            SUM({prefix}suarez) AS suarez,
            SUM({prefix}zahia) AS zahia,
            SUM({prefix}miroir) AS miroir,
            SUM({prefix}chapron) AS chapron,
            SUM({prefix}tontonpat) AS tontonpat,
            SUM({prefix}decat) AS decat
        FROM '{game_file_path}' G
        INNER JOIN '{bonus_file_path}' B ON G.match_id = B.match_id
        WHERE {prefix}teamid = '{team_id}'
        GROUP BY {prefix}teamid
        """
            ).fetchnumpy()
        )
    return {k: int((results[0].get(k, 0) or 0) + (results[1].get(k, 0) or 0)) for k in results[0]}


def get_all_team_ids(league_id, season_nb, division):
    """
    Retourne tout les ids des joueurs d'une division en particulier

    :param league_id: _description_
    :param season_nb: _description_
    """
    query = f"""
    SELECT 
        DISTINCT(h_teamid)
    FROM '{game_file_path}' G
    WHERE G.league_id = '{league_id}'
    AND G.season_nb = '{season_nb}'
    AND G.division = '{division}'
    """
    return duckdb.query(query).fetchnumpy()


def get_remaining_bonus_player(team_id: str, nb_players: int):
    """
    Returns the number of bonuses remaining for the team in a particular league

    1- Retrieves the number of starting bonuses according to league size
    2- Returns the number of bonuses played since the start of the season
    3- Return the difference between the two

    :param team_id: team id (unique for each league, division, season_nb)
    :param nb_players: number players in the league, to know how much bonus the player had in the beginning
    :raises ValueError: Raise an error if nb players in not possible
    :return: dict with number of remaining bonus
    """
    if nb_players not in [4, 6, 8, 10]:
        raise ValueError("Number of players must be one of : [4, 6, 8, 10]")

    bonus = get_json_bonus()
    start_bonus = bonus[f"{nb_players}_players"]

    bonus_played = get_total_team_bonus_played(team_id)

    return {k: start_bonus.get(k, 0) - bonus_played.get(k, 0) for k in bonus_played}


def get_all_players_bonus(league_id: str, season_nb: int, nb_players: int, division: int):
    """
    Returns all remaining bonuses for all players in a league.
    Returned string is in HTML format.

    1- Retrieves the number of starting bonuses according to league size
    2- Returns the number of bonuses played since the start of the season
    3- Return the difference between the two

    :param team_id: team id (unique for each league, division, season_nb)
    :param nb_players: number players in the league, to know how much bonus the player had in the beginning
    :raises ValueError: Raise an error if nb players in not possible
    :return: dict with number of remaining bonus
    """
    if nb_players not in [4, 6, 8, 10]:
        raise ValueError("Number of players must be one of : [4, 6, 8, 10]")

    bonus = get_json_bonus()
    start_bonus = bonus[f"{nb_players}_players"]

    team_ids = get_all_team_ids(league_id=league_id, season_nb=season_nb, division=division)["h_teamid"]

    bonus_df = pl.DataFrame()
    for team_id in team_ids:
        bonus_played = get_total_team_bonus_played(team_id)
        remaining_bonus = {k: start_bonus.get(k, 0) - bonus_played.get(k, 0) for k in bonus_played}
        new_row = {}
        new_row["team"] = team_id
        for bonus in remaining_bonus:
            new_row[bonus] = remaining_bonus[bonus]
        bonus_df = bonus_df.vstack(pl.DataFrame(new_row))
    return bonus_df.sort("team")
