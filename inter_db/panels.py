# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import *

from inter_db.read_all_tabs import get_all_panels
from models import Equip, Panel
from utilities import err_handler



def delete_panel(df):
    pass


def edit_panel(df):
    pan_df = df[df.to_del.astype('str') == "True"]

    if len(pan_df):
        try:
            with db_session:
                for ind, row in pan_df.iterrows():
                    edit_row = Panel.get(panel_tag=row.panel_tag)
                    if not edit_row:
                        st.toast(f"#### :red[Fail, Panel: {str(row.equipment_tag)} not found]")
                        continue

                    edit_row.set(equipment_tag=row.equipment_tag, descr=row.descr, notes=row.notes)

            st.toast(f"#### :green[Equipment: {str(row.equipment_tag)} is updated]")
        except Exception as e:
            st.toast(f"Can't update {str(row.equipment_tag)}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_panels.clear()
            st.button("OK", key='eq_updated')


@st.cache_data(show_spinner=False)
def get_eqip_tags():
    with db_session:
        eq_tags = select(eq.equipment_tag for eq in Equip)[:]
    return eq_tags


def create_panel():
    eqip_tag_list = get_eqip_tags()

    with st.form('add_panel'):
        c1, c2, c3, c4, c5 = st.columns(5, gap='medium')
        eq_tag = c1.selectbox('Equipment Tag', eqip_tag_list)
        panel_tag = c2.text_input('Panel Tag')
        panel_descr = c3.text_input('Panel Description')
        panel_notes = c4.text_input('Notes')
        c5.text('')
        c5.text('')
        pan_but = c5.form_submit_button("Add")

    if all([pan_but, len(eq_tag), len(panel_tag), len(panel_descr)]):
        try:
            with db_session:
                eq_id = Equip.get(equipment_tag=eq_tag)
                Panel(eq_id=eq_id, panel_tag=panel_tag, descr=panel_descr, to_del=False, notes=panel_notes)

            st.toast(f"""#### :orange[Panel {panel_tag}: {panel_descr} added!]""")
            get_all_panels.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Panel already exists!]""")
            st.toast(err_handler(e2))


def panels_main(act, prev_dict, prev_sel):
    if act == 'Create':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show)
        else:
            st.write(f"#### :blue[Panels not available...]")
        create_panel()

    if act == 'View':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show)
        else:
            st.write(f"#### :blue[Panels not available...]")

    if act == 'Delete':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show)
            if st.button("Delete Equipment"):
                delete_panel(edited_df)
        else:
            st.write(f"#### :blue[Panels not available...]")

    if act == 'Edit':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show)
            if st.button("Edit Equipment"):
                edit_panel(edited_df)
        else:
            st.write(f"#### :blue[Panels not available...]")


def check_panels(df):
    df.full_pan_tag = df.eq_tag.astype('str') + ":" + df.pan_tag.astype('str')
    check_list = df.loc[df.full_pan_tag.duplicated(), 'full_pan_tag'].tolist()

    if len(check_list):
        st.write(f"#### :red[Duplicated Panel Tags {check_list}. Please fix and save]")
        st.button('OK', key='duplicated_panels')
        st.stop()


def delete_panels(pan_to_del):
    st.session_state.intercon['panel'] = \
        st.session_state.intercon['panel'][~st.session_state.intercon['panel'].full_pan_tag.isin(pan_to_del)]
    st.experimental_rerun()


def save_panels(upd_panels_df, act_equip):
    temp_df = st.session_state.intercon['panel'].copy(deep=True)
    temp_df = temp_df[temp_df.eq_tag != act_equip]

    st.session_state.intercon['panel'] = pd.concat([temp_df, upd_panels_df])
    st.session_state.intercon['panel'].reset_index(drop=True, inplace=True)
    st.write("#### :green[Panels saved successfully]")
    st.button("OK", key='panels_saved')


def add_panels(act_equip, q_ty):
    df2 = pd.DataFrame()

    for w in range(0, q_ty):
        df2.loc[w, ["eq_tag", 'pan_to_del']] = [act_equip, False]

    st.session_state.intercon['panel'] = pd.concat([st.session_state.intercon['panel'], df2])
    st.session_state.intercon['panel'] = st.session_state.intercon['panel'].reset_index(drop=True)
    st.experimental_rerun()


# def edit_panel():
#     eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
#
#     if len(eq_list):
#         lc1, lc2, rc1, rc2 = st.columns([2, 1, 1, 2], gap='medium')
#         eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
#         eq_tag = lc1.selectbox('Equipment Tag', eq_list)
#         pan_to_add = lc2.number_input('Quantity of Panels to add', step=1, min_value=1, max_value=50)
#
#         rc1.text('')
#         rc1.text('')
#         add_pan_button = rc1.button("Add Panel to Document", use_container_width=True)
#
#         if eq_tag:
#             if add_pan_button:
#                 add_panels(eq_tag, pan_to_add)
#
#             pan_df = st.session_state.intercon['panel']
#             pan_filtered_df = pan_df[pan_df.eq_tag == eq_tag]
#
#             if len(pan_filtered_df):
#
#                 upd_pan_df = st.data_editor(
#                     pan_filtered_df,
#                     column_config={
#                         "eq_tag": st.column_config.TextColumn(
#                             "Equipment Tag",
#                             disabled=True,
#                             width='small',
#                         ),
#                         "pan_tag": st.column_config.TextColumn(
#                             "Panel Tag",
#                             width='small',
#                         ),
#                         "pan_descr": st.column_config.TextColumn(
#                             "Panel Description",
#                             width="medium",
#                         ),
#                         "full_pan_tag": st.column_config.TextColumn(
#                             "Full Panel Tag",
#                             width='small',
#                             disabled=True,
#                         ),
#                         "pan_to_del": st.column_config.CheckboxColumn(
#                             "Panel to delete",
#                             width="small",
#                             default=False,
#                         ),
#                     },
#                     hide_index=True, num_rows='fixed', use_container_width=True)
#
#                 rc2.text('')
#                 rc2.text('')
#
#                 # st.write(upd_pan_df.pan_to_del)
#
#                 pan_to_del = upd_pan_df.loc[upd_pan_df.pan_to_del.astype('str') == 'True', "full_pan_tag"].tolist()
#                 pan_to_show = upd_pan_df.loc[upd_pan_df.pan_to_del.astype('str') == 'True', "pan_tag"].tolist()
#                 del_pan_button = rc2.button(f"Delete selected Panels {pan_to_show}", use_container_width=True)
#
#                 if del_pan_button:
#                     delete_panels(pan_to_del)
#
#                 if st.button('SAVE PANELS'):
#                     check_panels(upd_pan_df)
#                     save_panels(upd_pan_df, eq_tag)
#
#             else:
#                 st.write("#### :blue[No panels for this equipment]")
#     else:
#         st.warning("Equipment not available...")
