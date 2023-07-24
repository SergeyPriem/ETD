# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from inter_db.panels import get_eqip_tags, get_filtered_panels, get_panel_tags
from inter_db.read_all_tabs import get_all_blocks
from models import Equip, Panel, Block
from utilities import err_handler


def delete_block(df):
    pass

def edit_block(df):
    pass


# @st.cache_data(show_spinner=False)
# def get_filtered_blocks(panel_id):
#     try:
#         with db_session:
#             data = select(
#                 (
#                     b.id,
#                     p.panel_tag,
#                     b.block_tag,
#                     b.descr,
#                     b.edit,
#                     b.notes,
#                     b.block_un
#                 )
#                 for b in Block
#                 for p in b.pan_id
#                 if b.pan_id == panel_id
#                  )[:]
#             df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description', 'edit',
#                                              'notes', 'block_un'])
#             return df
#     except Exception as e:
#         st.toast(err_handler(e))

def create_block():
    eqip_tag_list = list(get_eqip_tags())

    with st.form('add_block'):
        c2, c3, c4, c5 = st.columns([1, 1, 1.5, 0.5], gap='medium')
        # eq_tag = c1.selectbox('Equipment Tag', eqip_tag_list)
        panel_tag = c2.selectbox('Panel Tag', eqip_tag_list)
        block_tag = c3.text_input('Block Tag')
        block_descr = c3.text_input('Block Description')
        block_notes = c4.text_input('Notes')
        c5.text('')
        c5.text('')
        block_but = c5.form_submit_button("Add", use_container_width=True)

    if all([block_but, len(panel_tag), len(block_tag)]):
        try:
            with db_session:
                pan_id = Panel.get(panel_un=panel_tag)
                Block(pan_id=pan_id, block_tag=block_tag, descr=block_descr, edit=False,
                      notes=block_notes, block_un=str(panel_tag)+":"+str(block_tag))

            st.toast(f"""#### :green[Block {str(panel_tag)+":"+str(block_tag)} added!]""")
            get_all_blocks.clear()
            get_selected_blocks.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Panel already exists!]""")
            st.toast(err_handler(e2))

@st.cache_data(show_spinner=False)
def get_selected_blocks(panel_un):
    try:
        with db_session:
            # pan_id = Panel.get(panel_un=panel_un).id

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



def blocks_main(act, prev_dict, prev_sel):
    c1, c2 = st.columns(2, gap='medium')
    # eq_tag_list = list(get_eqip_tags())
    # eq_tag_list.insert(0, 'ALL')

    pan_tag_list = list(get_panel_tags())

    selected_panel = c1.selectbox('Select the Panel', pan_tag_list)

    df_to_show = get_selected_blocks(selected_panel)



    if isinstance(df_to_show, pd.DataFrame):
        data_to_show = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Blocks not available...]")
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
