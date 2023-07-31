# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags, get_panels_by_equip_panel_tag
from inter_db.read_all_tabs import get_all_blocks
from models import Panel, Block
from utilities import err_handler


def delete_block(df):
    del_block_df = df[df.edit.astype('str') == "True"]
    if len(del_block_df):
        try:
            with db_session:
                for ind, row in del_block_df.iterrows():
                    del_row = Block[ind]
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
            get_selected_blocks.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Terminal Block to delete in column 'Edit']")


def edit_block(df):
    block_df = df[df.edit.astype('str') == "True"]

    if len(block_df):
        try:
            with db_session:
                for ind, row in block_df.iterrows():
                    edit_row = Block[ind]  # .get(block_un=row.block_un)

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal Block: {row.block_tag} not found]")
                        continue

                    pan_id = Panel.get(panel_un=row.panel_tag)
                    edit_row.set(pan_id=pan_id, block_tag=row.block_tag, descr=row.description,
                                 notes=row.notes, block_un=str(row.panel_tag) + ":" + str(row.block_tag))
                    st.toast(f"#### :green[Terminal Block: {row.block_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.block_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_blocks.clear()
            get_selected_blocks.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Panel to edit in column 'Edit']")


def create_block(panel_tag):
    with st.form('add_block'):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5], gap='medium')
        c1.text_input('Panel Tag *', value=panel_tag, disabled=True)
        block_tag = c2.text_input('Block Tag *')
        block_descr = c3.text_input('Block Description')
        block_notes = c4.text_input('Notes')
        c5.text('')
        c5.text('')
        block_but = c5.form_submit_button("Add", use_container_width=True)

    if block_but:
        if all([len(panel_tag), len(block_tag)]):
            try:
                with db_session:
                    pan_id = Panel.get(panel_un=panel_tag)
                    Block(pan_id=pan_id, block_tag=block_tag, descr=block_descr, edit=False,
                          notes=block_notes, block_un=str(panel_tag) + ":" + str(block_tag))

                st.toast(f"""#### :green[Block {block_tag} added!]""")

            except Exception as e2:
                st.toast(f"""#### :red[Seems, such Terminal Block already exists!]""")
                st.toast(err_handler(e2))
            finally:
                get_all_blocks.clear()
                get_selected_blocks.clear()
                st.button("OK")


        else:
            st.toast(f"""#### :red[Please fill all required (*) fields!]""")

@st.cache_data(show_spinner=False)
def get_blocks_list_by_eq_pan(selected_equip, selected_panel):
    try:
        with db_session:

            data = select(b.block_tag
                          for b in Block
                          for p in b.pan_id
                          if selected_panel == b.pan_id.panel_tag and selected_equip == p.eq_id.equipment_tag
            )[:]

            return data
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_selected_blocks(panel_un):
    try:
        with db_session:

            data = select(
                (b.id,
                 b.pan_id.panel_un,
                 b.block_tag,
                 b.descr,
                 b.edit,
                 b.notes,
                 b.block_un)
                for b in Block if panel_un in b.block_un
            )[:]

            df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description',
                                             'edit', 'notes', 'block_un'])
            return df
    except Exception as e:
        st.toast(err_handler(e))


def get_selected_block(selected_equip, selected_panel, selected_block):
    try:
        with db_session:

            data = select(
                (
                    b.id,
                    b.pan_id.panel_un,
                    b.block_tag,
                    b.descr,
                    b.edit,
                    b.notes,
                    b.block_un
                )
                for b in Block
                for p in b.pan_id
                if selected_panel == b.pan_id.panel_tag and
                selected_equip == p.eq_id.equipment_tag and
                selected_block ==  b.block_tag
            )[:]

            df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description',
                                             'edit', 'notes', 'block_un'])
            return df
    except Exception as e:
        st.toast(err_handler(e))


def blocks_main(act):
    eq_tag_list = list(get_eqip_tags())

    c1, c2, c3 = st.columns([1, 2, 1], gap='medium')

    with c1:
        selected_equip = option_menu('Select the Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon=None)

    pan_tag_list = list(get_panel_tags(selected_equip))

    if len(pan_tag_list) == 0:
        pan_tag_list = ['No panels available']
        st.stop()

    with c2:
        selected_panel = option_menu('Select the Panel',
                                     options=pan_tag_list,
                                     icons=['-'] * len(pan_tag_list),
                                     orientation='horizontal', menu_icon=None)

    block_tag_list = list(get_blocks_list_by_eq_pan(selected_equip, selected_panel))
    if len(block_tag_list) == 0:
        block_tag_list = ['No blocks available']
        st.stop()

    with c3:
        selected_block = option_menu('Select the Terminal Block',
                                     options=block_tag_list,
                                     icons=['-'] * len(block_tag_list),
                                     orientation='horizontal', menu_icon="-")

    if selected_block == 'No blocks available':
        st.stop()

    df_to_show = get_selected_block(selected_equip, selected_panel, selected_block)

    if isinstance(df_to_show, pd.DataFrame) and len(df_to_show):
        data_to_show = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Blocks not available...]")

    if act == 'Create':
        data_to_show
        create_block(selected_panel)

    if act == 'View':
        data_to_show

    if act == 'Delete':
        edited_df = data_to_show
        if st.button("Delete Terminal Block"):
            delete_block(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        if st.button("Edit Selected Terminal Block"):
            edit_block(edited_df)
