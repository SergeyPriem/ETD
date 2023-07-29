﻿# -*- coding: utf-8 -*-

import streamlit as st
from pony.orm import db_session, select
import pandas as pd

from inter_db.panels import get_eqip_tags
from models import Terminal, Block
from utilities import err_handler, tab_to_df, convert_txt_to_list



def get_panel_terminals(pan):
    try:
        with db_session:
            data = select(str(b.block_id.block_tag)+":"+b.terminal_num for b in Terminal if pan in b.terminal_un)[:]
        return data
    except Exception as e:
        st.toast(err_handler(e))
def edit_terminals(df, block_un):
    term_df = df[df.edit.astype('str') == "True"]

    if len(term_df):
        try:
            with db_session:
                for ind, row in term_df.iterrows():
                    edit_row = Terminal[row.id]

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal: {row.terminal_num} not found]")
                        continue

                    block = Block.get(block_un=block_un)

                    edit_row.set(
                        block_id=block,
                        terminal_num=row.terminal_num,
                        int_circuit=row.int_circuit,
                        int_link=row.int_link,
                        edit=False,
                        notes=row.notes,
                        terminal_un=str(block_un) + ":" + str(row.terminal_num),
                    )
                    st.toast(f"#### :green[Terminal: {row.terminal_num} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.terminal_num}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_terminals.clear()
            st.experimental_rerun()
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")


def delete_terminals(df):
    del_term_df = df[df.edit.astype('str') == "True"]
    if len(del_term_df):
        sum_deleted = 0
        try:
            with db_session:
                for ind, row in del_term_df.iterrows():
                    del_row = Terminal[row.id]
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
            get_filtered_terminals.clear()
            st.experimental_rerun()
    else:
        st.toast(f"#### :orange[Select the Terminal to delete in column 'Edit']")


def create_terminals(block_un, terminals):
    try:
        with db_session:
            block = Block.get(block_un=block_un)
            exist_terminals = select(te.terminal_num for te in Terminal)[:]

            for t in terminals:
                t = str(t)
                if t in exist_terminals:
                    st.toast(f"##### :red[Terminal {t} already exists...]")
                    continue

                Terminal(
                    block_id=block,
                    terminal_num=t,
                    int_circuit="",
                    int_link="",
                    edit=False,
                    notes='',
                    terminal_un=str(block_un) + ":" + t,
                )
                st.toast(f"##### :green[Terminal {t} added]")

    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_terminals.clear()
        st.experimental_rerun()


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
            selected_block = Block.get(block_un=block)
            data = select((
                              t.id,
                              t.block_id.block_tag,
                              t.terminal_num,
                              t.int_circuit,
                              t.int_link,
                              t.edit,
                              t.notes,
                              t.terminal_un
                          ) for t in Terminal if t.block_id == selected_block)[:]

            df = pd.DataFrame(data, columns=['id', 'block_id', 'terminal_num', 'int_circuit', 'int_link',
                                             'edit', 'notes', 'terminal_un'])
            return df
    except Exception as e:
        st.toast(err_handler(e))


def terminals_main(act):
    eq_tag_list = list(get_eqip_tags())
    # pan_tag_list.insert(0, 'ALL')

    c1, c2 = st.columns(2, gap='medium')
    selected_equip = c1.selectbox('Select the Equipment', eq_tag_list)

    block_tag_list = list(get_filtered_blocks(selected_equip))
    selected_block = c2.selectbox('Select the Terminal Block', block_tag_list)

    if act != 'Select required:':
        if selected_equip and selected_block:
            df_to_show = get_filtered_terminals(selected_block)
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
                                                      "terminal_un": st.column_config.TextColumn(
                                                          "Terminal Unique Number",
                                                          width='large'
                                                      ),
                                                  },
                                                  use_container_width=True, hide_index=True)
                else:
                    data_to_show = st.write(f"#### :blue[Terminals not available...]")

        if act == 'Create':
            data_to_show
            c1, c2 = st.columns(2, gap='medium')
            terminals_str = c1.text_input("Terminals Numbers")
            c2.text("")
            c2.text("")
            if c2.button("Add Terminals", use_container_width=True):
                terminals = convert_txt_to_list(terminals_str)
                if all([len(terminals), isinstance(terminals, list)]):
                    create_terminals(selected_block, terminals)

        if act == 'View':
            data_to_show

        if isinstance(df_to_show, pd.DataFrame):
            if len(df_to_show):
                if act == 'Delete':
                    edited_df = data_to_show
                    if st.button("Delete Selected Terminals"):
                        delete_terminals(edited_df)

                if act == 'Edit':
                    edited_df = data_to_show
                    if st.button("Edit Selected Terminals"):
                        edit_terminals(edited_df, selected_block)


