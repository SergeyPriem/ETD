# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from inter_db.panels import get_eqip_tags, get_filtered_panels, get_panel_tags
from inter_db.read_all_tabs import get_all_blocks
from models import Equip, Panel, Block
from utilities import err_handler


def delete_block(df):
    block_list = df.loc[df.edit.astype('str') == "True", 'block_un'].tolist()
    if block_list:
        try:
            with db_session:
                for tag in block_list:
                    del_row = Block.get(block_un=tag)
                    if not del_row:
                        st.toast(f"#### :red[Fail, Terminal Block {del_row.block_tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Terminal Block: {del_row.block_tag} is deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {del_row.block_tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_blocks.clear()
            get_selected_blocks.clear()
            st.button("OK", key='block_deleted')
    else:
        st.toast(f"#### :orange[Select the Terminal Block to delete in column 'edit']")


def edit_block(df):
    block_df = df[df.edit.astype('str') == "True"]

    if len(block_df):
        try:
            with db_session:
                for ind, row in block_df.iterrows():
                    edit_row = Block[row.id] #.get(block_un=row.block_un)

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Terminal Block: {row.block_tag} not found]")
                        continue

                    pan_id = Panel.get(panel_un=row.panel_tag)
                    edit_row.set(pan_id=pan_id, block_tag=row.block_tag, descr=row.description,
                                 notes=row.notes, block_un=str(row.panel_tag)+":"+str(row.block_tag))
                    st.toast(f"#### :green[Terminal Block: {row.block_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.block_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_blocks.clear()
            get_selected_blocks.clear()
            st.button("OK", key='blocks_updated')
    else:
        st.toast(f"#### :orange[Select the Panel to edit in column 'edit']")


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

def create_block(panel_tag):

    with st.form('add_block'):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5], gap='medium')
        c1.text_input('Panel Tag', value=panel_tag, disabled=True)
        block_tag = c2.text_input('Block Tag')
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

            st.toast(f"""#### :green[Block {block_tag} added!]""")
            get_all_blocks.clear()
            get_selected_blocks.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Terminal Block already exists!]""")
            st.toast(err_handler(e2))

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



def blocks_main(act, prev_dict, prev_sel):

    pan_tag_list = list(get_panel_tags())
    selected_panel = st.selectbox('Select the Panel', pan_tag_list)
    df_to_show = get_selected_blocks(selected_panel)

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
