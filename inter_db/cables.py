# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu
from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.utils import get_cab_params, get_filtered_cables
from models import Cable, Cab_purpose, Cab_types, Cab_wires, Cab_sect, Panel
from utilities import err_handler


def delete_cable(df):
    del_cab_df = df[df.edit.astype('str') == "True"]
    if len(del_cab_df):
        try:
            with db_session:
                for ind, row in del_cab_df.iterrows():
                    del_row = Cable[row.id]
                    if not del_row:
                        st.toast(f"#### :red[Fail, cable: {row.cable_tag}  not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Cable: {row.cable_tag} is deleted]")

        except Exception as e:
            st.toast(f"#### :red[Can't delete {row.cable_tag} ]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            st.cache_data.clear()
            st.button('OK')
    else:
        st.toast(f"#### :orange[Select the Cable to delete in column 'Edit']")


def edit_cable(selected_left_equip, selected_left_panel, selected_right_equip, selected_right_panel, df):
    cables_df = df[df.edit.astype('str') == "True"]

    if len(cables_df):
        try:
            with db_session:
                left_pan = select(p for p in Panel
                                  if p.panel_tag == selected_left_panel and
                                  p.eq_id.equipment_tag == selected_left_equip).first()
                right_pan = select(p for p in Panel
                                   if p.panel_tag == selected_right_panel and
                                   p.eq_id.equipment_tag == selected_right_equip).first()

                for ind, row in cables_df.iterrows():
                    edit_row = Cable[row.id]

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Cable: {row.cable_tag}  not found]")
                        continue

                    purpose = Cab_purpose.get(circuit_descr=row.purpose)
                    c_type = Cab_types.get(cab_type=row.type)
                    c_wires = Cab_wires.get(wire_num=row.wire)
                    c_sect = Cab_sect.get(section=row.section)

                    edit_row.set(
                        cable_tag=row.cable_tag,
                        purpose_id=purpose,
                        type_id=c_type,
                        wires_id=c_wires,
                        sect_id=c_sect,
                        left_pan_id=left_pan,
                        right_pan_id=right_pan,
                        edit=False,
                        notes=row.notes,
                    )

                    st.toast(f"#### :green[Cable: {row.cable_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.cable_tag} ")
            st.toast(f"##### {err_handler(e)}")
        finally:
            st.cache_data.clear()
            st.button('OK')
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")


def copy_cable():
    ...

def create_cable(left_eq_tag, left_pan_tag, right_eq_tag, right_pan_tag):
    cab_purposes, cab_types, wire_numbers, wire_sections = get_cab_params()

    with st.form('add_cab'):
        lc, cc, rc = st.columns(3, gap='medium')
        cab_tag = cc.text_input("Cable Tag")

        c1, c2, c3, c4 = st.columns(4, gap='medium')

        cab_purpose = c1.selectbox('Cable Purpose', cab_purposes)
        cab_type = c2.selectbox('Cable Type', cab_types)
        wire_number = c3.selectbox('Wires Quantity', wire_numbers)
        wire_section = c4.selectbox('Wires Quantity', wire_sections)
        bl, bc = st.columns(2, gap='medium')
        notes = bl.text_input("Notes")
        bc.text('')
        bc.text('')
        add_cab_but = bc.form_submit_button("Add Cable", use_container_width=True)

    if add_cab_but:
        try:
            with db_session:
                left_pan = select(
                    p for p in Panel
                    if p.panel_tag == left_pan_tag and p.eq_id.equipment_tag == left_eq_tag).first()
                right_pan = select(
                    p for p in Panel
                    if p.panel_tag == right_pan_tag and p.eq_id.equipment_tag == right_eq_tag).first()

                purpose = Cab_purpose.get(circuit_descr=cab_purpose)
                c_type = Cab_types.get(cab_type=cab_type)
                c_wires = Cab_wires.get(wire_num=wire_number)
                c_sect = Cab_sect.get(section=wire_section)
                Cable(
                    cable_tag=cab_tag,
                    purpose_id=purpose,
                    type_id=c_type,
                    wires_id=c_wires,
                    sect_id=c_sect,
                    left_pan_id=left_pan,
                    right_pan_id=right_pan,
                    edit=False,
                    notes=notes,
                )
            st.toast(f"#### :green[Cable {cab_tag} added]")

        except Exception as e:
            st.toast(err_handler(e))
        finally:
            st.cache_data.clear()
            st.button('OK')


def cables_main(act):
    eq_tag_list = list(get_eqip_tags())

    lc, rc = st.columns(2, gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    with lc:
        selected_left_equip = option_menu('Select the Left Side Equipment',
                                          options=eq_tag_list,
                                          icons=['-'] * len(eq_tag_list),
                                          orientation='horizontal',
                                          menu_icon='1-square')


    left_pan_tag_list = list(get_panel_tags(selected_left_equip))

    if len(left_pan_tag_list) == 0:
        left_pan_tag_list = ['No panels available']

    with lc:
        selected_left_panel = option_menu('Select the Left Side Panel',
                                          options=left_pan_tag_list,
                                          icons=['-'] * len(left_pan_tag_list),
                                          orientation='horizontal', menu_icon='2-square')

    rc1, rc2 = st.columns([1, 2], gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    with rc:
        selected_right_equip = option_menu('Select the Right Side Equipment',
                                           options=eq_tag_list,
                                           icons=['-'] * len(eq_tag_list),
                                           orientation='horizontal',
                                           menu_icon='3-square')

    right_pan_tag_list = list(get_panel_tags(selected_right_equip))

    if len(right_pan_tag_list) == 0:
        right_pan_tag_list = ['No panels available']

    with rc:
        selected_right_panel = option_menu('Select the Right Side Panel',
                                           options=right_pan_tag_list,
                                           icons=['-'] * len(right_pan_tag_list),
                                           orientation='horizontal', menu_icon='4-square')

    if selected_left_panel == selected_right_panel and selected_left_equip == selected_right_equip:
        st.toast(f"##### :red[Left and Right Panels should be different]")
        st.stop()
    else:
        df_to_show = get_filtered_cables(selected_left_equip, selected_left_panel,
                                         selected_right_equip, selected_right_panel)

    if not isinstance(df_to_show, pd.DataFrame) or len(df_to_show) == 0:
        st.write("##### :blue[Please, create Equipment]")
        st.stop()
    else:
        edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)

        if act == 'Create':
            create_cable(selected_left_equip, selected_left_panel, selected_right_equip, selected_right_panel)

        if act == 'Copy':
            copy_cable()

        if act == 'Delete':
            st.subheader(f":warning: :red[All nested wires will be deleted!]")
            if st.button("Delete Selected Cable(s)"):
                delete_cable(edited_df)

        if act == 'Edit':
            if st.button("Edit Selected Cables"):
                edit_cable(selected_left_equip, selected_left_panel, selected_right_equip, selected_right_panel,
                           edited_df)
