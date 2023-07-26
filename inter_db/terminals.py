# -*- coding: utf-8 -*-

import streamlit as st
from pony.orm import db_session, select
import pandas as pd

from inter_db.panels import get_eqip_tags, get_filtered_panels
from models import Terminal, Block
from utilities import err_handler, tab_to_df


@st.cache_data(show_spinner=False)
def get_filtered_blocks(equip):
    try:
        with db_session:
            data = select(b.block_un for b in Block if equip in b.block_un)[:]
            return data
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_filtered_terminals(block):
    try:
        with db_session:
            data = select(t for t in Terminal if t.block_id == block)[:]
            return tab_to_df(data)
    except Exception as e:
        st.toast(err_handler(e))


def terminals_main(act, prev_dict, prev_sel):

    eq_tag_list = list(get_eqip_tags())
    # pan_tag_list.insert(0, 'ALL')

    c1, c2 = st.columns(2, gap='medium')
    selected_equip = c1.selectbox('Select the Equipment', eq_tag_list)

    block_tag_list = list(get_filtered_blocks(selected_equip))
    selected_block = c2.selectbox('Select the Terminal Block', block_tag_list)

    if all([selected_equip, selected_block, act != 'Select required:']):
        df_to_show = get_filtered_terminals(selected_block)
    # else:
    #     df_to_show = get_filtered_cables(selected_pan_left, selected_pan_right)

    if isinstance(df_to_show, pd.DataFrame):
        # cab_purposes, cab_types, wire_numbers, wire_sections = get_cab_params()
        data_to_show = st.data_editor(df_to_show,
                                      # column_config={
                                      #     "id": st.column_config.TextColumn(
                                      #         "ID",
                                      #         disabled=True,
                                      #         width='small'
                                      #     ),
                                      #     "cable_tag": st.column_config.TextColumn(
                                      #         "Cable Tag",
                                      #         width='medium'
                                      #     ),
                                      #     "purpose": st.column_config.SelectboxColumn(
                                      #         "Cable Purpose",
                                      #         options=cab_purposes,
                                      #         width='small'
                                      #     ),
                                      #     "type": st.column_config.SelectboxColumn(
                                      #         "Cable Type",
                                      #         options=cab_types,
                                      #         width='medium'
                                      #     ),
                                      #     "wire": st.column_config.SelectboxColumn(
                                      #         "Wires' Number",
                                      #         options=wire_numbers,
                                      #         width='small'
                                      #     ),
                                      #     "section": st.column_config.SelectboxColumn(
                                      #         "Wires' Section",
                                      #         options=wire_sections,
                                      #         width='small'
                                      #     ),
                                      #     "left_pan_tag": st.column_config.SelectboxColumn(
                                      #         "Left Panel Tag",
                                      #         options=pan_tag_list,
                                      #         width='medium'
                                      #     ),
                                      #     "right_pan_tag": st.column_config.SelectboxColumn(
                                      #         "Right Panel Tag",
                                      #         options=pan_tag_list,
                                      #         width='medium'
                                      #     ),
                                      #     "edit": st.column_config.CheckboxColumn(
                                      #         "Edit",
                                      #         width='small'
                                      #     ),
                                      #     "notes": st.column_config.TextColumn(
                                      #         "Notes",
                                      #         width='large'
                                      #     ),
                                      # },
                                      use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Panels not available...]")
        # st.stop()

    if act == 'Create':
        data_to_show
        # create_terminals(???)

    if act == 'View':
        data_to_show

    if act == 'Delete':
        edited_df = data_to_show
        # if st.button("Delete Equipment"):
        #     delete_terminals(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        # if st.button("Edit Selected Cables"):
        #     edit_terminals(edited_df)
