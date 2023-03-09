# -*- coding: utf-8 -*-

from sqlmodel import create_engine
# from pre_sets import connect_sleep
from time import sleep


def get_engine(sqlite_file):
    sleep(0.75)
    sqlite_url = f"sqlite:///{sqlite_file}"
    return create_engine(sqlite_url, echo=True)


sqlite_file_name = "database.db"

engine = get_engine(sqlite_file_name)

###############################################################################################################


# import streamlit as st
# from supabase import create_client, Client
#
#
# # Initialize connection.
# # Uses st.cache_resource to only run once.
# @st.cache_resource
# def init_connection():
#     url = st.secrets["supabase_url"]
#     key = st.secrets["supabase_key"]
#     return create_client(url, key)
#
#
# engine = init_connection()
#

###############################################################################################################

# import streamlit as st
# import psycopg2
#
#
# # Initialize connection.
# # Uses st.cache_resource to only run once.
# # @st.cache_resource
# def init_connection():
#     return psycopg2.connect(**st.secrets["postgres"])
#
#
# conn = init_connection()
#
#
# # Perform query.
# # Uses st.cache_data to only rerun when the query changes or after 10 min.
# # @st.cache_data(ttl=600)
# def run_query(query):
#     with conn.cursor() as cur:
#         cur.execute(query)
#         return cur.fetchall()
#
#
# rows = run_query("SELECT * from appl_user;")
#
# # Print results.
# for row in rows:
#     st.write(row[1])
