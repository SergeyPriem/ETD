# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from inter_db.panels import get_eqip_tags, get_filtered_panels
from inter_db.read_all_tabs import get_all_blocks
from models import Equip, Panel, Block
from utilities import err_handler


def delete_block(df):
    pass

def edit_block(df):
    pass

def get_filtered_blocks(panel_id):
    try:
        with db_session:
            data = select(
                (
                    b.id,
                    p.panel_tag,
                    b.block_tag,
                    b.descr,
                    b.edit,
                    b.notes)
                for b in Block
                for p in b.pan_id
                if b.pan_id == panel_id
                 )[:]
            df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description', 'edit', 'notes'])
            return df
    except Exception as e:
        st.toast(err_handler(e))

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
            get_all_blocks.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Panel already exists!]""")
            st.toast(err_handler(e2))


def blocks_main(act, prev_dict, prev_sel):
    eq_tag_list = list(get_eqip_tags())
    eq_tag_list.insert(0, 'ALL')
    selected_equip = st.selectbox('Select the Equipment', eq_tag_list)

    if selected_equip == 'ALL' and act != 'Select required:':
        df_to_show_prel = prev_dict[prev_sel]()
    else:
        df_to_show_prel = get_filtered_panels(selected_equip)

    panel_list = df_to_show_prel.panel_tag.tolist()
    panel_list.insert(0, 'ALL')

    selected_panel = st.selectbox('Select the Panel', panel_list)

    selected_panel_id = None

    if selected_panel != 'ALL':
        selected_panel_id = df_to_show_prel[df_to_show_prel.panel_tag == selected_panel].index



    if selected_equip == 'ALL' and selected_panel == 'ALL':
        df_to_show = get_all_blocks()
    else:
        df_to_show = get_filtered_blocks(selected_panel_id)


    if isinstance(df_to_show, pd.DataFrame):
        data_to_show = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Panels not available...]")
        st.stop()

    if act == 'Create':
        data_to_show
        create_block()

    if act == 'View':
        data_to_show

    if act == 'Delete':
        edited_df = data_to_show
        if st.button("Delete Equipment"):
            delete_block(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        if st.button("Edit Panel"):
                edit_block(edited_df)
