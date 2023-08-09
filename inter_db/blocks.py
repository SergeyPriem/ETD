# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.read_all_tabs import get_all_blocks
from inter_db.utils import get_blocks_list_by_eq_pan, get_selected_block, create_block, create_terminals_with_internals, \
    add_block_to_db
from models import Panel, Block, Terminal
from utilities import err_handler, act_with_warning


def delete_block(df):
    del_block_df = df[df.edit.astype('str') == "True"]
    if len(del_block_df):
        try:
            with db_session:
                for ind, row in del_block_df.iterrows():
                    del_row = Block[row.id]
                    if not del_row:
                        st.toast(f"#### :red[Fail, Terminal Block {row.block_tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Terminal Block: {row.block_tag} is deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {row.block_tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_blocks.clear()
            get_blocks_list_by_eq_pan.clear()
            get_selected_block.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Terminal Block to delete in column 'Edit']")


def edit_block(df):
    block_df = df[df.edit.astype('str') == "True"]

    if len(block_df):
        try:
            with db_session:
                for ind, row in block_df.iterrows():
                    edit_row = Block[row.id]  # .get(block_un=row.block_un)

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal Block: {row.block_tag} not found]")
                        continue

                    pan_id = Panel.get(panel_un=row.panel_tag)
                    edit_row.set(pan_id=pan_id, block_tag=row.block_tag, descr=row.description, notes=row.notes)
                    st.toast(f"#### :green[Terminal Block: {row.block_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.block_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_blocks.clear()
            get_selected_block.clear()
            get_blocks_list_by_eq_pan.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Panel to edit in column 'Edit']")


def copy_block(init_block_id):
    with db_session:
        init_block = Block[init_block_id]

    if init_block:
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.7, 0.5, 1, 1, 1.5, 0.6, 0.4], gap='medium')
        eqip_tag_list = get_eqip_tags()
        eq_tag = c1.selectbox('Equipment Tag *', eqip_tag_list)

        pan_tag_list = []
        if eq_tag:
            pan_tag_list = get_panel_tags(eq_tag)

        pan_tag = c2.selectbox('Panel Tag *', pan_tag_list)
        block_tag = c3.text_input('Block Tag *', value=init_block.block_tag)
        block_descr = c4.text_input('Block Description', value=init_block.descr)
        block_notes = c5.text_input('Notes', value=init_block.notes)
        c6.text('')
        c6.text('')
        c6.checkbox('Copy nested terminals')
        c7.text('')
        c7.text('')
        block_but = c7.button("Copy", use_container_width=True)

        if block_but:
            if len(block_tag):
                try:
                    with db_session:
                        add_block_to_db(equip_tag=eq_tag, panel_tag=pan_tag,
                                        block_tag=block_tag,
                                        block_descr=block_descr,
                                        block_notes=block_notes)

                        terminals = select(t for t in Terminal if t.block_id == init_block)[:]

                        if len(terminals):
                            create_terminals_with_internals(eq_tag, pan_tag, block_tag, terminals)
                            st.toast(f"###### :green[Terminals {terminals} added]")

                        st.toast(f"""#### :green[Block {block_tag} added!]""")

                except Exception as e2:
                    st.toast(f"""#### :red[Seems, such Terminal Block already exists!]""")
                    st.toast(err_handler(e2))
                finally:
                    st.cache_data.clear()
                    st.experimental_rerun()
            else:
                st.toast(f"""#### :red[Please fill all required (*) fields!]""")
    else:
        st.toast(f"##### :red[Block with ID {init_block_id} not found]")


def blocks_main(act):
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
    else:
        if len(block_tag_list) > 1:
            block_tag_list.append('ALL')

    with c3:
        selected_block = option_menu('Select the Terminal Block',
                                     options=block_tag_list,
                                     icons=['-'] * len(block_tag_list),
                                     orientation='horizontal', menu_icon='3-square')

    df_to_show = get_selected_block(selected_equip, selected_panel, selected_block)

    if act == 'Create':
        create_block(selected_equip, selected_panel)

    if act == 'Copy':
        copy_block(int(df_to_show.id.to_numpy()[0]))

    if not (isinstance(df_to_show, pd.DataFrame) and len(df_to_show)):
        st.write(f"#### :blue[Blocks not available...]")
        st.stop()

    edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)

    if act == 'Delete':
        if st.button("Delete Terminal Block"):
            act_with_warning(left_function=delete_block, left_args=edited_df,
                             header_message="All related terminals will be deleted!",
                             warning_message="Are you sure?")

    if act == 'Edit':
        if st.button("Edit Selected Terminal Block"):
            edit_block(edited_df)
