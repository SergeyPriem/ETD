# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from inter_db.panels import get_panel_tags
from inter_db.read_all_tabs import get_all_cables
from models import Cable, Cab_purpose, Cab_types, Cab_wires, Cab_sect, Panel, Wire
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
    tag_list = df.loc[df.edit.astype('str') == "True", 'cable_tag'].tolist()
    if tag_list:
        try:
            with db_session:
                for tag in tag_list:
                    del_row = Cable.get(cable_tag=tag)
                    if not del_row:
                        st.toast(f"#### :red[Fail, cable: {tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Cable: {tag} is deleted]")

                    wires_to_del = select(w.id for w in Wire if w.cable_id == del_row)[:]

                    for wire_del in wires_to_del:
                        wire_to_del = Wire[wire_del]
                        wire_to_del.delete()
                    st.toast(f"#### :green[{len(wires_to_del)} wires deleted]")

        except Exception as e:
            st.toast(f"#### :red[Can't delete {tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_cables.clear()
            get_all_cables.clear()
            get_cab_tags.clear()
            get_cab_panels.clear()
            st.button("OK", key='cable_deleted')
    else:
        st.toast(f"#### :orange[Select the Cable to delete in column 'Edit']")


def edit_cable(df):
    cables_df = df[df.edit.astype('str') == "True"]

    if len(cables_df):
        try:
            with db_session:
                for ind, row in cables_df.iterrows():
                    edit_row = Cable[row.id] #.get(cable_tag=row.cable_tag)
                    # eq_id = Equip.get(equipment_tag=row.equipment_tag).id
                    if not edit_row:
                        st.toast(f"#### :red[Fail, Cable: {row.cable_tag} not found]")
                        continue

                    purpose = Cab_purpose.get(circuit_descr=row.purpose)
                    c_type = Cab_types.get(cab_type=row.type)
                    c_wires = Cab_wires.get(wire_num=row.wire)
                    c_sect = Cab_sect.get(section=row.section)
                    left_pan = Panel.get(panel_un=row.left_pan_tag)
                    right_pan = Panel.get(panel_un=row.right_pan_tag)

                    exist_wires_qty = edit_row.wire_num

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

                    if exist_wires_qty > c_wires:
                        for w in range (c_wires+1, exist_wires_qty+1):
                            Wire(
                                cable_id=edit_row,
                                wire_num=w,
                                edit=False,
                                left_term_id="",
                                right_term_id="",
                            )

                    if exist_wires_qty < c_wires:
                        for w in range (exist_wires_qty+1, c_wires+1):
                            wire_to_del = select(w for w in Wire if w.cable_id == edit_row and w.wire_num == w).first()

                            wire_to_del.delete()


                    st.toast(f"#### :green[Cable: {row.cable_tag} is updated]")
        except Exception as e:
            st.toast(f"Can't update {row.cable_tag}")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_cables.clear()
            get_all_cables.clear()
            get_cab_tags.clear()
            get_cab_panels.clear()
            st.button("OK", key='cables_updated')
    else:
        st.toast(f"#### :orange[Select the Cables to edit in column 'Edit']")


@st.cache_data(show_spinner=False)
def get_filtered_cables(left_pan, right_pan):
    try:

        with db_session:
            if left_pan and right_pan:
                data = select(
                    (c.id, c.cable_tag, c.purpose_id.circuit_descr, c.type_id.cab_type, c.wires_id.wire_num,
                     c.sect_id.section, c.left_pan_id.panel_un, c.right_pan_id.panel_un, c.edit, c.notes,)
                    for c in Cable
                    if (left_pan in c.left_pan_id.panel_un) and (right_pan in c.right_pan_id.panel_un))[:]
            else:
                data = select(
                    (c.id, c.cable_tag, c.purpose_id.circuit_descr, c.type_id.cab_type, c.wires_id.wire_num,
                     c.sect_id.section, c.left_pan_id.panel_un, c.right_pan_id.panel_un, c.edit, c.notes,)
                    for c in Cable)[:]

            df = pd.DataFrame(data, columns=['id', 'cable_tag', 'purpose', 'type', 'wire', 'section',
                                             'left_pan_tag', 'right_pan_tag', 'edit', 'notes', ])

            return df
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
                    new_cab = Cable(
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
                    new_cab.flush()
                    for w in range(1, int(c_wires)+1):
                        Wire(
                            cable_id=new_cab.id,
                            wire_num=w,
                            edit=False,
                            left_term_id="",
                            right_term_id="",
                        )
                st.toast(f"#### :green[Cable {cab_tag} added]")
                st.toast(f"#### :green[{c_wires} created]")
            except Exception as e:
                st.toast(err_handler(e))
            finally:
                get_filtered_cables.clear()
                get_all_cables.clear()
                get_cab_tags.clear()
                get_cab_panels.clear()
                st.button("OK", key='cable_added')


def cables_main(act, prev_dict, prev_sel):
    pan_tag_list = list(get_panel_tags())

    c1, c2 = st.columns(2, gap='medium')

    selected_pan_left = c1.text_input('Search Left Panel by part of tag')
    selected_pan_right = c2.text_input('Select Right Panel  by part of tag')

    if all([selected_pan_left == 'ALL', selected_pan_right == 'ALL', ]):
        df_to_show = prev_dict[prev_sel]()
    else:
        df_to_show = get_filtered_cables(selected_pan_left, selected_pan_right)

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


