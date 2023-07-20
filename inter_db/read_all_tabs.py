﻿# -*- coding: utf-8 -*-
import pandas as pd
from pony.orm import *

from models import Equip, Panel, Block, Terminal
from util.utilities import err_handler, tab_to_df


def get_all_equip():
    with db_session:
        try:
            table = select(u for u in Equip)[:]
            return tab_to_df(table)
        except Exception as e:
            return err_handler(e)

def get_all_panels():
    with db_session:
        try:
            data = select(
                (p.id,
                 p.eq_id.equipment_tag,
                 p.panel_tag,
                 p.descr,
                 p.to_del,
                 p.notes,
                 )
                for p in Panel)[:]
            df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description', 'to_del', 'notes'])
            return df
        except Exception as e:
            return err_handler(e)

def get_all_blocks():
    with db_session:
        try:
            data = select(
                (b.id,
                 p.eq_id.equipment_tag,
                 b.pan_id.panel_tag,
                 b.block_tag,
                 b.descr,
                 b.to_del,
                 b.notes,
                 )
                for b in Block
                for p in b.pan_id
            )[:]
            df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag',
                                             'block_tag', 'description', 'to_del', 'notes'])
            return df
        except Exception as e:
            return err_handler(e)

def get_all_terminals():
    with db_session:
        try:
            data = select(
                (t.id,
                 p.eq_id.equipment_tag,
                 b.pan_id.panel_tag,
                 t.block_id.block_tag,
                 t.eq_id.equipment_tag,
                 t.pan_id.panel_tag,
                 t.block_tag,
                 t.descr,
                 t.to_del,
                 t.notes,
                 )
                for t in Terminal
                for b in t.block_id
                for p in b.pan_id
            )[:]
            df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag',
                                             'block_tag', 'terminal_num', 'description', 'to_del', 'notes'])
            return df
        except Exception as e:
            return err_handler(e)
