# -*- coding: utf-8 -*-

import streamlit as st
from pony.orm import db_session, select
import pandas as pd

from inter_db.panels import get_eqip_tags, get_filtered_panels
from models import Terminal, Block
from utilities import err_handler, tab_to_df, convert_txt_to_list



def edit_terminals(df, block_un):
    term_df = df[df.edit.astype('str') == "True"]

    if len(term_df):
        try:
            with db_session:
                for ind, row in term_df.iterrows():
                    edit_row = Terminal[row.id] #.get(cable_tag=row.cable_tag)
                    # eq_id = Equip.get(equipment_tag=row.equipment_tag).id
                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal: {row.terminal_num} not found]")
                        continue

                    # purpose = Cab_purpose.get(circuit_descr=row.purpose)
                    # c_type = Cab_types.get(cab_type=row.type)
                    # c_wires = Cab_wires.get(wire_num=row.wire)
                    # c_sect = Cab_sect.get(section=row.section)
                    # left_pan = Panel.get(panel_un=row.left_pan_tag)
                    # right_pan = Panel.get(panel_un=row.right_pan_tag)

                    edit_row.set(
                        cable_tag=row.cable_tag,
                        block_id=row.block_id,
                        terminal_num=row.terminal_num,
                        int_circuit=row.int_circuit,
                        int_link=row.int_link,
                        edit=False,
                        terminal_un=str(block_un)+":"+str(row.terminal_num),
                        notes=row.notes,
                    )
                    st.toast(f"#### :green[Cable: {row.cable_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.cable_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_terminals.clear()
            st.button("OK", key='terminal_updated')
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")



def delete_terminals(df):
    term_list = df.loc[df.edit.astype('str') == "True", 'terminal_un'].tolist()
    if term_list:
        sum_deleted = 0
        try:
            with db_session:
                for tag in term_list:
                    del_row = Terminal.get(terminal_un=tag)
                    if not del_row:
                        st.toast(f"##### :red[Fail, Terminal {tag} not found]")
                        continue
                    del_row.delete()
                    sum_deleted +=1
                    st.toast(f":green[Terminal: {tag.split(':')[-1]} is deleted]")
                st.toast(f"#### :green[{sum_deleted} terminals deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_terminals.clear()
            st.button("OK", key='terminal_deleted')
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
                    terminal_un=str(block_un)+":"+t,
                )
                st.toast(f"##### :green[Terminal {t} added]")

    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_terminals.clear()
        st.button("OK", key='terminals_added')


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
        # st.stop()

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

    if act == 'Delete':
        edited_df = data_to_show
        if st.button("Delete Selected Terminals"):
            delete_terminals(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        if st.button("Edit Selected Cables"):
            edit_terminals(edited_df)
