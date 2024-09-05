import duckdb

import streamlit as st

st.set_page_config(layout="wide")

st.title("Games database")

game_file_path = "exports/games.parquet"

main_table_head = duckdb.query(
    f"""
    SELECT *
    FROM '{game_file_path}' G
    """
).df()

st.write("First 10 rows: ", main_table_head)
