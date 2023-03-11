# -*- coding: utf-8 -*-

from sqlmodel import create_engine
import streamlit as st

# def get_engine(sqlite_file):
#     sleep(0.75)
#     sqlite_url = f"sqlite:///{sqlite_file}"
#     return create_engine(sqlite_url, echo=True)
#
#
# sqlite_file_name = "database.db"
#
# engine = get_engine(sqlite_file_name)

###############################################################################################################

engine = create_engine('mysql://{0}:{1}@{2}:{3}/{4}'.format(st.secrets["db_user"], st.secrets["db_password"],
                                                            st.secrets["db_host"], st.secrets["db_port"],
                                                            st.secrets["db_database"]))

