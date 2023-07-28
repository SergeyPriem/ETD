# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import *

from inter_db.read_all_tabs import get_all_panels
from models import Equip, Panel
from utilities import err_handler, get_list_index


@st.cache_data(show_spinner=False)
def get_filtered_panels(equip):
    try:
        with db_session:
            equip_id = Equip.get(equipment_tag=equip)
            data = select(
                (p.id,
                 p.eq_id.equipment_tag,
                 p.panel_tag,
                 p.descr,
                 p.edit,
                 p.notes,
                 p.panel_un,
                 )
                for p in Panel
                if p.eq_id == equip_id
            )[:]
        df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description',
                                         'edit', 'notes', 'panel_un'])
        return df

    except Exception as e:
        st.toast(err_handler(e))
        return



def delete_panel(df):
    tag_list = df.loc[df.edit.astype('str') == "True", 'panel_tag'].tolist()
    if tag_list:
        try:
            with db_session:
                for tag in tag_list:
                    del_row = Panel.get(panel_tag=tag)
                    if not del_row:
                        st.toast(f"#### :red[Fail, equipment {tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Equipment: {tag} is deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_panels.clear()
            get_filtered_panels.clear()
            get_panel_tags.clear()
            st.button("OK", key='panel_deleted')
    else:
        st.toast(f"#### :orange[Select the Panel to delete in column 'Edit']")


def edit_panel(df):
    pan_df = df[df.edit.astype('str') == "True"]

    if len(pan_df):
        try:
            with db_session:
                for ind, row in pan_df.iterrows():
                    edit_row = Panel.get(panel_tag=row.panel_tag)
                    eq_id = Equip.get(equipment_tag=row.equipment_tag).id
                    if not edit_row:
                        st.toast(f"#### :red[Fail, Panel: {row.panel_tag} not found]")
                        continue

                    edit_row.set(eq_id=eq_id, panel_tag=row.panel_tag, descr=row.description,
                                 notes=row.notes, panel_un=str(row.equipment_tag)+":"+str(row.panel_tag))
                    st.toast(f"#### :green[Panel: {row.panel_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.panel_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_panels.clear()
            get_filtered_panels.clear()
            get_panel_tags.clear()
            st.button("OK", key='panels_updated')
    else:
        st.toast(f"#### :orange[Select the Panel to edit in column 'Edit']")


@st.cache_data(show_spinner=False)
def get_eqip_tags():
    try:
        with db_session:
            eq_tags = select(eq.equipment_tag for eq in Equip)[:]
        return eq_tags
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_panel_tags():
    try:
        with db_session:
            eq_tags = select(p.panel_un for p in Panel)[:]
        return eq_tags
    except Exception as e:
        st.toast(err_handler(e))


def create_panel(sel_equip):
    eqip_tag_list = get_eqip_tags()

    with st.form('add_panel'):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5], gap='medium')
        eq_tag = c1.selectbox('Equipment Tag', options=eqip_tag_list, index=get_list_index(eqip_tag_list, sel_equip))
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
                Panel(eq_id=eq_id, panel_tag=panel_tag, descr=panel_descr, edit=False, notes=panel_notes,
                      panel_un=str(eq_tag)+":"+str(panel_tag))

            st.toast(f"""#### :green[Panel {panel_tag}: {panel_descr} added!]""")
            get_all_panels.clear()
            get_filtered_panels.clear()
            get_panel_tags.clear()
            if st.button("OK", key='eq_added'):
                st.experimental_rerun()

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Panel already exists!]""")
            st.toast(err_handler(e2))
    else:
        st.toast(f"""#### :red[Please fill all required (*) fields!]""")


def panels_main(act, prev_dict, prev_sel):
    eq_tag_list = list(get_eqip_tags())
    eq_tag_list.insert(0, 'ALL')
    selected_equip = st.selectbox('Select the Equipment', eq_tag_list)

    if selected_equip == 'ALL' and act != 'Select required:':
        df_to_show = prev_dict[prev_sel]()
    else:
        df_to_show = get_filtered_panels(selected_equip)

    if isinstance(df_to_show, pd.DataFrame):
        data_to_show = st.data_editor(df_to_show, use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Panels not available...]")
        st.stop()

    if act == 'Create':
        data_to_show
        if selected_equip:
            create_panel(selected_equip)

    if act == 'View':
        data_to_show

    if act == 'Delete':
        edited_df = data_to_show
        if st.button("Delete Equipment"):
            delete_panel(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        if st.button("Edit Selected Panel"):
                edit_panel(edited_df)


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


