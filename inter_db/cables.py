# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.read_all_tabs import get_all_cables
from models import Cable, Cab_purpose, Cab_types, Cab_wires, Cab_sect, Panel
from utilities import err_handler


@st.cache_data(show_spinner=False)
def get_cab_panels(cab_tag):
    try:
        with db_session:
            cab_tags = select((c.left_pan_id.panel_un, c.right_pan_id.panel_un)
                              for c in Cable if c.cable_tag == cab_tag).first()
        return cab_tags
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_cab_tags():
    try:
        with db_session:
            cab_tags = select(c.cable_tag for c in Cable)[:]
        return cab_tags
    except Exception as e:
        st.toast(err_handler(e))


def delete_cable(df):
    del_cab_df = df[df.edit.astype('str') == "True"]
    if len(del_cab_df):
        try:
            with db_session:
                for ind, row in del_cab_df.iterrows():
                    del_row = Cable[ind]
                    if not del_row:
                        st.toast(f"#### :red[Fail, cable: {row.cable_tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Cable: {row.cable_tag} is deleted]")

        except Exception as e:
            st.toast(f"#### :red[Can't delete {row.cable_tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_cables.clear()
            get_all_cables.clear()
            get_cab_tags.clear()
            get_cab_panels.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Cable to delete in column 'Edit']")


def edit_cable(df):
    cables_df = df[df.edit.astype('str') == "True"]

    if len(cables_df):
        try:
            with db_session:
                for ind, row in cables_df.iterrows():
                    edit_row = Cable[ind]

                    if not edit_row:
                        st.toast(f"#### :red[Fail, Cable: {row.cable_tag} not found]")
                        continue

                    purpose = Cab_purpose.get(circuit_descr=row.purpose)
                    c_type = Cab_types.get(cab_type=row.type)
                    c_wires = Cab_wires.get(wire_num=row.wire)
                    c_sect = Cab_sect.get(section=row.section)
                    left_pan = Panel.get(panel_un=row.left_pan_tag)
                    right_pan = Panel.get(panel_un=row.right_pan_tag)

                    # exist_wires_qty = edit_row.wire_num

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
            st.toast(f"Can't update {row.cable_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_cables.clear()
            get_all_cables.clear()
            get_cab_tags.clear()
            get_cab_panels.clear()
            st.button("OK")
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")


@st.cache_data(show_spinner=False)
def get_filtered_cables(left_eq, left_pan, right_eq, right_pan):
    try:
        with db_session:

            left_pan = select(p for p in Panel if p.panel_tag == left_pan and p.eq_id.equipment_tag == left_eq)[:]
            right_pan = select(p for p in Panel if p.panel_tag == right_pan and p.eq_id.equipment_tag == right_eq)[:]

            if left_pan and right_pan:
                if left_pan.id != right_pan.id:
                    data = select(
                        (c.id, c.cable_tag, c.purpose_id.circuit_descr, c.type_id.cab_type, c.wires_id.wire_num,
                         c.sect_id.section, c.left_pan_id.panel_un, c.right_pan_id.panel_un, c.edit, c.notes,)
                        for c in Cable
                        if (left_pan in c.left_pan_id.panel_un) and (right_pan in c.right_pan_id.panel_un))[:]

                    df = pd.DataFrame(data, columns=['id', 'cable_tag', 'purpose', 'type', 'wire', 'section',
                                                     'left_pan_tag', 'right_pan_tag', 'edit', 'notes', ])

                    return df
                else:
                    st.toast(f"Left and Right Panels should be different")
                    return None

    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False, ttl=600)
def get_cab_params():
    try:
        with db_session:
            purposes = select(cp.circuit_descr for cp in Cab_purpose)[:]
            types = select(ct.cab_type for ct in Cab_types)[:]
            wire_num = select(w.wire_num for w in Cab_wires)[:]
            wire_sect = select(s.section for s in Cab_sect)[:]

        return purposes, types, wire_num, wire_sect
    except Exception as e:
        return err_handler(e)


def create_cable(pan_tag_list):
    cab_purposes, cab_types, wire_numbers, wire_sections = get_cab_params()

    with st.form('add_cab'):
        lc, cc, rc = st.columns(3, gap='medium')
        left_pan_tag = lc.selectbox("Select Left Panel", pan_tag_list)
        cab_tag = cc.text_input("Cable Tag")
        right_pan_tag = rc.selectbox("Select Right Panel", pan_tag_list)

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
        if left_pan_tag == right_pan_tag:
            st.warning("Left and Right panels should be different")
        else:
            try:
                with db_session:
                    left_pan = Panel.get(panel_un=left_pan_tag)
                    right_pan = Panel.get(panel_un=right_pan_tag)
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
                    # new_cab.flush()
                    # for w in range(1, int(wire_number)+1):
                    #     Wire(
                    #         cable_id=new_cab.id,
                    #         wire_num=w,
                    #         edit=False,
                    #         left_term_id=0,
                    #         right_term_id=0,
                    #     )
                st.toast(f"#### :green[Cable {cab_tag} added]")

            except Exception as e:
                st.toast(err_handler(e))
            finally:
                get_filtered_cables.clear()
                get_all_cables.clear()
                get_cab_tags.clear()
                get_cab_panels.clear()
                st.button("OK")


def cables_main(act, prev_dict, prev_sel):

    eq_tag_list = list(get_eqip_tags())

    lc1, lc2 = st.columns([1, 2], gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with lc1:
        selected_left_equip = option_menu('Select the Left Side Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon='1-square')

    if selected_left_equip == 'No equipment available':
        st.stop()

    left_pan_tag_list = list(get_panel_tags(selected_left_equip))

    if len(left_pan_tag_list) == 0:
        left_pan_tag_list = 'No panels available'

    with lc2:
        selected_left_panel = option_menu('Select the Left Side Panel',
                                     options=left_pan_tag_list,
                                     icons=['-'] * len(left_pan_tag_list),
                                     orientation='horizontal', menu_icon='2-square')

    rc1, rc2 = st.columns([1, 2], gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with rc1:
        selected_right_equip = option_menu('Select the Right Side Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon='1-square')

    if selected_right_equip == 'No equipment available':
        st.stop()

    right_pan_tag_list = list(get_panel_tags(selected_right_equip))

    if len(right_pan_tag_list) == 0:
        pan_tag_list = 'No panels available'

    with rc2:
        selected_right_panel = option_menu('Select the Right Side Panel',
                                     options=right_pan_tag_list,
                                     icons=['-'] * len(right_pan_tag_list),
                                     orientation='horizontal', menu_icon='2-square')


    # c1, c2 = st.columns(2, gap='medium')

    # selected_pan_left = c1.text_input('Search Left Panel by part of tag')
    # selected_pan_right = c2.text_input('Select Right Panel  by part of tag')

    # if all([selected_pan_left == 'ALL', selected_pan_right == 'ALL', ]):
    #     df_to_show = prev_dict[prev_sel]()
    # else:
    df_to_show = get_filtered_cables(selected_left_equip, selected_left_panel,
                                     selected_right_equip,selected_right_panel)

    if isinstance(df_to_show, pd.DataFrame):
        cab_purposes, cab_types, wire_numbers, wire_sections = get_cab_params()
        data_to_show = st.data_editor(df_to_show,
                                      column_config={
                                          "id": st.column_config.TextColumn(
                                              "ID",
                                              disabled=True,
                                              width='small'
                                          ),
                                          "cable_tag": st.column_config.TextColumn(
                                              "Cable Tag",
                                              width='medium'
                                          ),
                                          "purpose": st.column_config.SelectboxColumn(
                                              "Cable Purpose",
                                              options=cab_purposes,
                                              width='small'
                                          ),
                                          "type": st.column_config.SelectboxColumn(
                                              "Cable Type",
                                              options=cab_types,
                                              width='medium'
                                          ),
                                          "wire": st.column_config.SelectboxColumn(
                                              "Wires' Number",
                                              options=wire_numbers,
                                              width='small'
                                          ),
                                          "section": st.column_config.SelectboxColumn(
                                              "Wires' Section",
                                              options=wire_sections,
                                              width='small'
                                          ),
                                          "left_pan_tag": st.column_config.SelectboxColumn(
                                              "Left Panel Tag",
                                              options=pan_tag_list,
                                              width='medium'
                                          ),
                                          "right_pan_tag": st.column_config.SelectboxColumn(
                                              "Right Panel Tag",
                                              options=pan_tag_list,
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
                                      },
                                      use_container_width=True, hide_index=True)
    else:
        data_to_show = st.write(f"#### :blue[Panels not available...]")
        # st.stop()

    if act == 'Create':
        data_to_show
        create_cable(pan_tag_list)

    if act == 'View':
        data_to_show

    if act == 'Delete':
        edited_df = data_to_show
        if st.button("Delete Equipment"):
            delete_cable(edited_df)

    if act == 'Edit':
        edited_df = data_to_show
        if st.button("Edit Selected Cables"):
            edit_cable(edited_df)
