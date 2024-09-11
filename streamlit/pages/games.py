import duckdb

import streamlit as st

st.set_page_config(layout="wide")

st.title("Games database")

game_file_path = "exports/games.parquet"
bonus_file_path = "exports/bonus.parquet"

main_table_head = duckdb.query(
    f"""
    SELECT *
    FROM '{game_file_path}' G
    INNER JOIN '{bonus_file_path}' B ON G.match_id = B.match_id

    """
).df()

st.write(main_table_head)
