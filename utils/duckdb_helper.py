import os

import duckdb
from typing_extensions import deprecated

games_file_path = "exports/games.parquet"
bonus_file_path = "exports/bonus.parquet"


@deprecated("This function is not used anymore. 04/09/2024")
def azure_secret():
    """
    This function is connection DuckDB to our Azure storage using connection string
    """
    conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    duckdb.sql("install azure")
    duckdb.sql("load azure")
    duckdb.sql(f"set azure_storage_connection_string = '{conn_string}'")
    duckdb.sql(f"set azure_transport_option_type = 'curl'")


def get_all_league_ids() -> list:

    league_ids = (
        duckdb.query(
            f"""
        SELECT
        DISTINCT league_id,
        FROM '{games_file_path}' G
        ORDER BY league_id
        """
        )
        .fetchnumpy()["league_id"]
        .tolist()
    )
    return league_ids


def get_all_seasons_nb(league_id: str) -> list:

    seasons_nb = (
        duckdb.query(
            f"""
        SELECT
        DISTINCT season_nb,
        FROM '{games_file_path}' G
        WHERE league_id = '{league_id}'
        ORDER BY season_nb
        """
        )
        .fetchnumpy()["season_nb"]
        .tolist()
    )
    return seasons_nb


def get_all_divisions_nb(league_id: str, season: int) -> list:

    divisions_nb = (
        duckdb.query(
            f"""
        SELECT
        DISTINCT division,
        FROM '{games_file_path}' G
        WHERE league_id = '{league_id}'
        AND season_nb = '{season}'
        ORDER BY division
        """
        )
        .fetchnumpy()["division"]
        .tolist()
    )
    return divisions_nb


def get_nb_players(league_id: str, season_nb: int, division: int) -> list:

    seasons_nb = (
        duckdb.query(
            f"""
        SELECT
            COUNT(DISTINCT id) AS nb_games
        FROM (
            SELECT 
                h_teamid AS id
            FROM '{games_file_path}'
            WHERE 
                league_id = '{league_id}' AND
                season_nb = '{season_nb}' AND
                division = '{division}'
            UNION
            SELECT 
                v_teamid AS id
            FROM '{games_file_path}'
            WHERE 
                league_id = '{league_id}' AND
                season_nb = '{season_nb}' AND
                division = '{division}'
        ) AS ids
        """
        )
        .fetchnumpy()["nb_games"]
        .tolist()
    )
    return seasons_nb[0]
