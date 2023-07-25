# -*- coding: utf-8 -*-
import pandas as pd
from pony.orm import *
import streamlit as st
from models import Equip, Panel, Block, Terminal, Cable
from utilities import err_handler, tab_to_df


@st.cache_data(show_spinner=False)
def get_all_equip():
    with db_session:
        try:
            table = select(u for u in Equip)[:]
            return tab_to_df(table)
        except Exception as e:
            return err_handler(e)


@st.cache_data(show_spinner=False)
def get_all_panels():
    with db_session:
        try:
            data = select(
                (p.id,
                 p.eq_id.equipment_tag,
                 p.panel_tag,
                 p.descr,
                 p.edit,
                 p.notes,
                 p.panel_un,
                 )
                for p in Panel)[:]
            df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description', 'edit',
                                             'notes', 'panel_un'])
            return df
        except Exception as e:
            return err_handler(e)


@st.cache_data(show_spinner=False)
def get_all_blocks():
    with db_session:
        try:
            data = select(
                (b.id,
                 p.eq_id.panel_un,
                 # b.pan_id.panel_tag,
                 b.block_tag,
                 b.descr,
                 b.edit,
                 b.notes,
                 b.block_un
                 )
                for b in Block
                for p in b.pan_id
            )[:]
            df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description',
                                             'edit', 'notes', 'block_un'])
            return df
        except Exception as e:
            return err_handler(e)


@st.cache_data(show_spinner=False)
def get_all_terminals():
    with db_session:
        try:
            data = select(
                (t.id,
                 p.eq_id.equipment_tag,
                 b.pan_id.panel_tag,
                 t.block_id.block_tag,
                 t.terminal_num,
                 t.int_circuit,
                 t.int_link,
                 t.edit,
                 t.notes,
                 )
                for t in Terminal
                for b in t.block_id
                for p in b.pan_id
            )[:]
            df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'block_tag', 'terminal_num',
                                             'internal_circuit', 'internal_link', 'edit', 'notes'])
            return df
        except Exception as e:
            return err_handler(e)


@st.cache_data(show_spinner=False)
def get_all_cables():
    try:
        with db_session:
            data = select(
                (c.id,
                 c.cable_tag,
                 # c.purpose_id.circuit_descr,
                 # c.type_id.cab_type,
                 # c.wires.wire_num,
                 # c.sect_id.section,
                 # c.wires_id.wire_num,
                 # c.left_pan_id.panel_un,
                 # c.right_pan_id.panel_un,
                 # c.edit,
                 c.notes,
                 )
                for c in Cable)[:]

        df = pd.DataFrame(data, columns=[
            'id',
            'cable_tag',
            # 'purpose',
            # 'type',
            # 'wire',
            # 'section',
            # 'wires_num',
            # 'left_pan_tag',
            # 'right_pan_tag',
            # 'edit',
            'notes',
        ])
        return df
    except Exception as e:
        return err_handler(e)
