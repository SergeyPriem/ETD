# -*- coding: utf-8 -*-

import streamlit as st
from pony.orm import db_session, select
import pandas as pd
from streamlit_option_menu import option_menu
from inter_db.blocks import get_blocks_list_by_eq_pan
from inter_db.panels import get_eqip_tags, get_panel_tags
from inter_db.utils import get_selected_block_terminals, get_panel_terminals, create_terminals
from models import Terminal, Block, Equip, Panel
from utilities import err_handler, convert_txt_to_list


def edit_terminals(df, selected_equip, selected_panel, selected_block):
    term_df = df[(df.edit.astype('str') == "True") & (df.terminal_num != "isolated")]

    if len(term_df):
        try:
            with db_session:
                for ind, row in term_df.iterrows():
                    edit_row = Terminal[ind]

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal: {row.terminal_num} not found]")
                        continue

                    equip = Equip.get(equipment_tag=selected_equip)
                    panel = select(p for p in Panel if p.panel_tag == selected_panel and p.eq_id == equip).first()
                    block = select(b for b in Block if b.pan_id == panel and b.block_tag == selected_block).first()

                    edit_row.set(
                        block_id=block,
                        terminal_num=row.terminal_num,
                        int_circuit=row.int_circuit,
                        int_link=row.int_link,
                        edit=False,
                        notes=row.notes,
                    )
                    st.toast(f"#### :green[Terminal: {row.terminal_num} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.terminal_num}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            # get_filtered_terminals.clear()
            get_panel_terminals.clear()

            st.experimental_rerun()
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")


def delete_terminals(df):
    del_term_df = df[(df.edit.astype('str') == "True") & (df.terminal_num != "isolated")]
    if len(del_term_df):
        sum_deleted = 0
        try:
            with db_session:
                for ind, row in del_term_df.iterrows():
                    del_row = Terminal[ind]
                    if not del_row:
                        st.toast(f"##### :red[Fail, Terminal {row.terminal_num} not found]")
                        continue
                    del_row.delete()
                    sum_deleted += 1
                    st.toast(f":green[Terminal: {row.terminal_num} deleted]")
                st.toast(f"#### :green[{sum_deleted} terminals deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {row.terminal_num}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_selected_block_terminals.clear()
            get_panel_terminals.clear()
            st.experimental_rerun()
    else:
        st.toast(f"#### :orange[Select the Terminal to delete in column 'Edit']")


def terminals_main(act):
    eq_tag_list = list(get_eqip_tags())

    c1, c2, c3 = st.columns([1, 2, 1], gap='medium')

    with c1:
        selected_equip = option_menu('Select the Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon='1-square')

    pan_tag_list = list(get_panel_tags(selected_equip))

    if len(pan_tag_list) == 0:
        pan_tag_list = ['No panels available']

    with c2:
        selected_panel = option_menu('Select the Panel',
                                     options=pan_tag_list,
                                     icons=['-'] * len(pan_tag_list),
                                     menu_icon='2-square',
                                     orientation='horizontal')

    if selected_panel == 'No panels available':
        st.stop()

    block_tag_list = list(get_blocks_list_by_eq_pan(selected_equip, selected_panel))

    if len(block_tag_list) == 0:
        block_tag_list = ['No blocks available']

    with c3:
        selected_block = option_menu('Select the Terminal Block',
                                     options=block_tag_list,
                                     icons=['-'] * len(block_tag_list),
                                     orientation='horizontal', menu_icon='3-square')

    df_to_show = get_selected_block_terminals(selected_equip, selected_panel, selected_block)

    if isinstance(df_to_show, pd.DataFrame):
        if len(df_to_show):
            data_to_show = st.data_editor(df_to_show,
                                          column_config={
                                              "id": st.column_config.TextColumn(
                                                  "ID",
                                                  disabled=True,
                                                  width='small'
                                              ),
                                              "block_id": st.column_config.TextColumn(
                                                  "Block Tag",
                                                  width='small',
                                                  disabled=True,
                                              ),
                                              "terminal_num": st.column_config.TextColumn(
                                                  "Number of Terminal",
                                                  width='medium'
                                              ),
                                              "int_circuit": st.column_config.TextColumn(
                                                  "Internal Circuit",
                                                  width='medium'
                                              ),
                                              "int_link": st.column_config.TextColumn(
                                                  "Jumper to Terminal",
                                                  width='medium'
                                              ),
                                              "edit": st.column_config.CheckboxColumn(
                                                  "Edit",
                                                  width='small'
                                              ),
                                              "notes": st.column_config.TextColumn(
                                                  "Notes",
                                                  width='large'
                                              ),
                                              # "terminal_un": st.column_config.TextColumn(
                                              #     "Terminal Unique Number",
                                              #     width='large'
                                              # ),
                                          },
                                          use_container_width=True, hide_index=True)
        else:
            data_to_show = st.write(f"#### :blue[Terminals not available...]")

        if act == 'Create':
            # data_to_show
            c1, c2 = st.columns(2, gap='medium')
            terminals_str = c1.text_input("Terminals Numbers")
            c2.text("")
            c2.text("")
            if c2.button("Add Terminals", use_container_width=True):
                terminals = convert_txt_to_list(terminals_str)
                if all([len(terminals), isinstance(terminals, list)]):
                    create_terminals(selected_equip, selected_panel, selected_block, terminals)
                    st.experimental_rerun()

        if len(df_to_show):
            if act == 'Delete':
                edited_df = data_to_show
                if st.button("Delete Selected Terminals"):
                    delete_terminals(edited_df)

            if act == 'Edit':
                edited_df = data_to_show
                if st.button("Edit Selected Terminals"):
                    edit_terminals(edited_df, selected_equip, selected_panel, selected_block)
