# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.utils import get_eqip_tags
from models import Wire, Cable, Equip, Panel
from utilities import err_handler, tab_to_df


def get_all_terminals(equip_tag):
    try:
        with db_session:
            equip = Equip.get(equipment_tag=equip_tag)
            panels = select(p for p in Panel if p.eq_id == equip)[:]
            cables = select(cab for cab in Cable if cab.left_pan_id in panels)[:]
            wires = select(w for w in Wire if w.cable_id in cables)[:]

            return tab_to_df(wires)

    except Exception as e:
        st.toast(err_handler(e))


def generate_wd():
    eq_tag_list = list(get_eqip_tags())

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    else:
        if len(eq_tag_list) > 1:
            eq_tag_list.append("ALL")

    selected_equip = option_menu('Select the Equipment',
                                 options=eq_tag_list,
                                 icons=['-'] * len(eq_tag_list),
                                 orientation='horizontal',
                                 menu_icon='1-square')

    term_df = get_all_terminals(selected_equip)

    if isinstance(term_df, pd.DataFrame) and len(term_df):
        st.data_editor(term_df, use_container_width=True)
    else:
        st.write("##### :blue[Wires not found]")