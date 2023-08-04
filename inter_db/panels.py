# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import *
from streamlit_option_menu import option_menu
from inter_db.equipment import get_eqip_tags
from inter_db.read_all_tabs import get_all_panels
from models import Equip, Panel
from utilities import err_handler, get_list_index, act_with_warning


@st.cache_data(show_spinner=False)
def get_panels_by_equip_panel_tag(equip_tag, pan_tag):
    try:
        with db_session:
            if pan_tag != 'ALL':
                data = select(
                    (
                        p.id,
                        p.eq_id.equipment_tag,
                        p.panel_tag,
                        p.descr,
                        p.edit,
                        p.notes,
                        p.panel_un,
                    )
                    for p in Panel
                    if equip_tag == p.eq_id.equipment_tag and pan_tag == p.panel_tag)[:]
            else:
                data = select(
                    (
                        p.id,
                        p.eq_id.equipment_tag,
                        p.panel_tag,
                        p.descr,
                        p.edit,
                        p.notes,
                        p.panel_un,
                    )
                    for p in Panel
                    if equip_tag == p.eq_id.equipment_tag)[:]

        df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description',
                                         'edit', 'notes', 'panel_un'])
        return df
    except Exception as e:
        return err_handler(e)


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
        return err_handler(e)


def delete_panel(df):
    del_pan_df = df[df.edit.astype('str') == "True"]
    if len(del_pan_df):
        try:
            with db_session:
                for ind, row in del_pan_df.iterrows():
                    del_row = Panel[row.id]
                    if not del_row:
                        st.toast(f"#### :red[Fail, equipment with {row.panel_tag} not found]")
                        continue
                    tag = del_row.panel_tag
                    del_row.delete()
                    st.toast(f"#### :green[Panel: {tag} is deleted]")
        except Exception as e:
            st.toast(f"#### :red[Can't delete {tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_panels.clear()
            get_filtered_panels.clear()
            get_panel_tags.clear()
            get_panels_by_equip_panel_tag.clear()
            st.experimental_rerun()
    else:
        st.toast(f"#### :orange[Select the Panel to delete in column 'Edit']")


def edit_panel(df):
    pan_df = df[df.edit.astype('str') == "True"]

    if len(pan_df):
        try:
            with db_session:
                for ind, row in pan_df.iterrows():
                    edit_row = Panel[row.id]
                    eq_id = Equip.get(equipment_tag=row.equipment_tag).id
                    if not edit_row:
                        st.toast(f"#### :red[Fail, Panel: {row.panel_tag} not found]")
                        continue

                    edit_row.set(eq_id=eq_id, panel_tag=row.panel_tag, descr=row.description,
                                 notes=row.notes, panel_un=str(row.equipment_tag) + ":" + str(row.panel_tag))
                    st.toast(f"#### :green[Panel: {row.panel_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.panel_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_all_panels.clear()
            get_filtered_panels.clear()
            get_panel_tags.clear()
            get_panels_by_equip_panel_tag.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Panel to edit in column 'Edit']")


@st.cache_data(show_spinner=False)
def get_panel_tags(eq_tag):
    try:
        with db_session:
            eq_tags = select(p.panel_tag for p in Panel if p.eq_id.equipment_tag == eq_tag)[:]
        return eq_tags
    except Exception as e:
        return [err_handler(e)]


def create_panel(sel_equip):
    # eqip_tag_list = get_eqip_tags()

    with st.form('add_panel'):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 0.5], gap='medium')
        eq_tag = c1.text_input('Equipment Tag *', value=sel_equip)
        panel_tag = c2.text_input('Panel Tag *')
        panel_descr = c3.text_input('Panel Description *')
        panel_notes = c4.text_input('Notes')
        c5.text('')
        c5.text('')
        pan_but = c5.form_submit_button("Add", use_container_width=True)

    if pan_but:
        if all([len(eq_tag), len(panel_tag), len(panel_descr)]):
            try:
                with db_session:
                    eq_id = Equip.get(equipment_tag=eq_tag)
                    Panel(eq_id=eq_id, panel_tag=panel_tag, descr=panel_descr, edit=False, notes=panel_notes,
                          panel_un=str(eq_tag) + ":" + str(panel_tag))

                st.toast(f"""#### :green[Panel {panel_tag}: {panel_descr} added!]""")

            except Exception as e2:
                st.toast(f"""#### :red[Seems, such Panel already exists!]""")
                st.toast(err_handler(e2))
            finally:
                get_all_panels.clear()
                get_filtered_panels.clear()
                get_panel_tags.clear()
                st.button("OK")

        else:
            st.toast(f"""#### :red[Please fill all required (*) fields!]""")

def copy_panel(panel_tag):
    eqip_tag_list = get_eqip_tags()

    # pan_df = df[df.edit.astype('str') == "True"]

    with st.form('add_panel'):
        c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1.5, 0.5, 0.5], gap='medium')
        eq_tag = c1.selectbox('Copy to Equipment *', options=eqip_tag_list)
        panel_tag = c2.text_input('Panel Tag *', value=panel_tag)
        panel_descr = c3.text_input('Panel Description *')
        panel_notes = c4.text_input('Notes')
        nested_blocks = c5.checkbox("Copy nested blocks and terminals")
        c5.text('')
        c5.text('')
        pan_but = c6.form_submit_button("Add", use_container_width=True)

    if pan_but:
        if all([len(eq_tag), len(panel_tag), len(panel_descr)]):
            try:
                with db_session:
                    eq_id = Equip.get(equipment_tag=eq_tag)
                    Panel(eq_id=eq_id, panel_tag=panel_tag, descr=panel_descr, edit=False, notes=panel_notes,
                          panel_un=str(eq_tag) + ":" + str(panel_tag))

                st.toast(f"""#### :green[Panel {panel_tag}: {panel_descr} added!]""")

            except Exception as e2:
                st.toast(f"""#### :red[Seems, such Panel already exists!]""")
                st.toast(err_handler(e2))
            finally:
                get_all_panels.clear()
                get_filtered_panels.clear()
                get_panel_tags.clear()
                st.button("OK")

        else:
            st.toast(f"""#### :red[Please fill all required (*) fields!]""")


def panels_main(act):
    eq_tag_list = list(get_eqip_tags())

    c1, c2 = st.columns([1, 2], gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with c1:
        selected_equip = option_menu('Select the Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon='1-square')

    if selected_equip == 'No equipment available':
        st.stop()

    pan_tag_list = list(get_panel_tags(selected_equip))

    if len(pan_tag_list) == 0:
        pan_tag_list = 'No panels available'
    else:
        if len(pan_tag_list) > 1:
            pan_tag_list.append("ALL")

    with c2:
        selected_panel = option_menu('Select the Panel',
                                     options=pan_tag_list,
                                     icons=['-'] * len(pan_tag_list),
                                     orientation='horizontal', menu_icon='2-square')

    df_to_show = get_panels_by_equip_panel_tag(selected_equip, selected_panel)

    if act == 'Create':
        if selected_equip:
            create_panel(selected_equip)

    if act == 'Copy':
        if selected_equip:
            copy_panel(selected_equip)

    if not isinstance(df_to_show, pd.DataFrame):
        st.write(f"#### :blue[Panels not available...]")
        st.stop()

    edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)

    if act == 'Delete':
        if st.button("Delete Panel"):
            act_with_warning(left_function=delete_panel, left_args=edited_df,
                             header_message="All related terminal blocks and terminals will be deleted!",
                             warning_message='Are you sure?')

    if act == 'Edit':
        if st.button("Edit Selected Panel"):
            edit_panel(edited_df)


