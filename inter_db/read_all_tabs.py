﻿# -*- coding: utf-8 -*-

from pony.orm import *
from util.utilities import err_handler, tab_to_df


def get_all_data(db_table):
    with db_session:
        try:
            table = select(u for u in db_table)[:]
            return tab_to_df(table)
        except Exception as e:
            return err_handler(e)

