# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session

from inter_db.panels import get_eqip_tags
from models import Equip, Panel


def create_block():
    eqip_tag_list = get_eqip_tags()

    with st.form('add_panel'):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5], gap='medium')
        eq_tag = c1.selectbox('Equipment Tag', eqip_tag_list)
        panel_tag = c2.text_input('Panel Tag')
        panel_descr = c3.text_input('Panel Description')
        panel_notes = c4.text_input('Notes')
        c5.text('')
        c5.text('')
        pan_but = c5.form_submit_button("Add", use_container_width=True)

    if all([pan_but, len(eq_tag), len(panel_tag), len(panel_descr)]):
        try:
            with db_session:
                eq_id = Equip.get(equipment_tag=eq_tag)
                Panel(eq_id=eq_id, panel_tag=panel_tag, descr=panel_descr, edit=False, notes=panel_notes)

            st.toast(f"""#### :green[Panel {panel_tag}: {panel_descr} added!]""")
            get_all_panels.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Panel already exists!]""")
            st.toast(err_handler(e2))


def blocks_main(act, prev_dict, prev_sel):
    if act == 'Create':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show, use_container_width=True, hide_index=True)
        else:
            st.write(f"#### :blue[Panels not available...]")
        create_block()

    if act == 'View':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show, use_container_width=True, hide_index=True)
        else:
            st.write(f"#### :blue[Terminal Blocks not available...]")

    if act == 'Delete':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
            if st.button("Delete Equipment"):
                delete_block(edited_df)
        else:
            st.write(f"#### :blue[Panels not available...]")

    if act == 'Edit':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
            if st.button("Edit Panel"):
                edit_block(edited_df)
        else:
            st.write(f"#### :blue[Panels not available...]")
