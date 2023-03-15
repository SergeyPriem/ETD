# -*- coding: utf-8 -*-
from sqlalchemy.pool import QueuePool
from sqlmodel import create_engine
import streamlit as st

def get_engine(sqlite_file):
    sqlite_url = f"sqlite:///{sqlite_file}"
    return create_engine(sqlite_url, echo=True)


sqlite_file_name = "database.db"
engine = get_engine(sqlite_file_name)

###############################################################################################################


# engine = create_engine(st.secrets['DATABASE_URL'],
#                        pool_size=10,
#                        pool_recycle=-1,
#                        pool_timeout=30,
#                        max_overflow=10,
#                        echo_pool=True,
#                        poolclass=QueuePool,
#                        pool_pre_ping=True,
#                        )
