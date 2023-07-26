﻿# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from inter_db.panels import get_eqip_tags, get_filtered_panels, get_panel_tags
from inter_db.read_all_tabs import get_all_cables
from models import Cable, Cab_purpose, Cab_types, Cab_wires, Cab_sect, Panel
from utilities import err_handler, tab_to_df


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
        except Exception as e:
            st.toast(f"#### :red[Can't delete {tag}]")
            st.toast(f"##### {err_handler(e)}")
        finally:
            get_filtered_cables.clear()
            get_all_cables.clear()
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
                get_filtered_cables.clear()
                get_all_cables.clear()
                st.button("OK", key='cable_added')


def cables_main(act, prev_dict, prev_sel):
    pan_tag_list = list(get_panel_tags())
    # pan_tag_list.insert(0, 'ALL')

    if act != 'Select required:':
        c1, c2 = st.columns(2, gap='medium')
        # selected_pan_left = c1.selectbox('Select Left Panel', pan_tag_list)
        # selected_pan_right = c2.selectbox('Select Right Panel', pan_tag_list)

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

    else:
        st.write("Select the option 👆 to proceed")

# def delete_cable(cab_to_del_list):
#     st.session_state.intercon['cable'] = \
#         st.session_state.intercon['cable'][~st.session_state.intercon['cable'].cab_tag.isin(cab_to_del_list)]
#     st.experimental_rerun()


# def save_cables(df, full_pan_tag_left, full_pan_tag_right):
#     temp_df = st.session_state.intercon['cable'].copy(deep=True)
#     temp_df = temp_df[(temp_df.full_pan_tag_left != full_pan_tag_left) & (
#             temp_df.full_pan_tag_right != full_pan_tag_right)]
#     st.session_state.intercon['cable'] = pd.concat([temp_df, df])
#     st.session_state.intercon['cable'].reset_index(drop=True, inplace=True)
#     st.write("#### :green[Cables saved successfully]")
#     st.button("OK", key='cables_saved')
#
#
# def check_cables(df):
#     check_list = df.loc[df.cab_tag.duplicated(), 'cab_tag'].tolist()
#     if len(check_list):
#         st.write(f"#### :red[Duplicated Cable Tags {check_list}. Please fix and save]")
#         st.button('OK', key='duplicated_cables')
#         st.stop()


# def edit_cab_con():
#     lc1, lc2, rc1, rc2 = st.columns(4, gap='medium')
#     eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
#     if len(eq_list):
#         left_eq = lc1.selectbox("Select the Left Equipment", eq_list)
#         right_eq = rc1.selectbox("Select the Right Equipment", eq_list)
#
#         panels = st.session_state.intercon['panel']
#         left_pan_list = panels.loc[panels.eq_tag == left_eq, 'full_pan_tag'].tolist()
#         right_pan_list = panels.loc[panels.eq_tag == right_eq, 'full_pan_tag'].tolist()
#
#         if len(left_pan_list) and len(right_pan_list):
#             left_pan = lc2.selectbox("Select the Left Panel", left_pan_list)
#             right_pan = rc2.selectbox("Select the Right Panel", right_pan_list)
#
#             cab = st.session_state.intercon['cab_descr']
#             cab_purposes = cab['cab_purpose'].tolist()
#             cab_types = cab['cab_type'].tolist()
#             cab_sects = cab['cab_sect'].tolist()
#             cab_wire_qtys = cab['wire_quant'].tolist()
#             cab_tags = st.session_state.intercon['cable']['cab_tag'].tolist()
#
#             lc, cc, rc = st.columns(3, gap='medium')
#             cab_tag = lc.text_input("Cable Tag")
#
#             cc.text('')
#             cc.text('')
#             rc.text('')
#             rc.text('')
#
#             # cab_purpose = lc2.selectbox("Select Cable Purpose", cab_purposes)
#             # cab_type = rc1.selectbox("Select Cable Type", cab_types)
#             # cab_sect = rc2.selectbox("Select Wire Section", cab_sects)
#
#             if cc.button("Create Cable Connection", use_container_width=True):
#
#                 if left_pan == right_pan:
#                     st.write("#### :red[Select different left and right panels]")
#                     st.button("OK", key='select_different')
#                     st.stop()
#
#                 if cab_tag:
#                     if cab_tag in cab_tags:
#                         st.button(f"❗ Cable with Tag {cab_tag} already exist...CLOSE and try again")
#                         st.stop()
#
#                     df2 = pd.DataFrame.from_dict([
#                         {
#                             'full_pan_tag_left': left_pan,
#                             'full_pan_tag_right': right_pan,
#                             'cab_tag': cab_tag,
#                             # 'cab_purpose': cab_purpose,
#                             # 'cab_type': cab_type,
#                             # 'cab_sect': cab_sect,
#                             'wire_quant': 0,
#                             'cab_to_del': False
#                         }
#                     ])
#
#                     df1 = st.session_state.intercon['cable'].copy(deep=True)
#                     st.session_state.intercon['cable'] = pd.concat([df1, df2],
#                                                                    ignore_index=True)
#                     st.experimental_rerun()
#                 else:
#                     st.button("❗ Enter the Cable Tag")
#
#             cab_df = st.session_state.intercon['cable']
#             cab_to_edit_df = cab_df[(cab_df.full_pan_tag_left == left_pan) & (cab_df.full_pan_tag_right == right_pan)]
#
#             if len(cab_to_edit_df):
#                 edited_cab_df = st.data_editor(
#                     cab_to_edit_df,
#                     column_config={
#                         "full_pan_tag_left": st.column_config.TextColumn(
#                             "Left Panel Tag",
#                             width="small",
#                             disabled=True
#                         ),
#                         "cab_tag": st.column_config.TextColumn(
#                             "Cable Tag",
#                             width="medium",
#                             disabled=True
#                         ),
#                         "full_pan_tag_right": st.column_config.TextColumn(
#                             "Right Panel Tag",
#                             width="small",
#                             disabled=True
#                         ),
#                         "cab_purpose": st.column_config.SelectboxColumn(
#                             "Cable Purpose",
#                             options=cab_purposes,
#                             width='small',
#                         ),
#                         "cab_type": st.column_config.SelectboxColumn(
#                             "Cable Type",
#                             options=cab_types,
#                             width='small',
#                         ),
#                         "cab_sect": st.column_config.SelectboxColumn(
#                             "Wire Section",
#                             options=cab_sects,
#                             width='small',
#                         ),
#                         "wire_quant": st.column_config.SelectboxColumn(
#                             "Wires Quantity",
#                             options=cab_wire_qtys,
#                             width='small',
#                         ),
#                         "cab_to_del": st.column_config.CheckboxColumn(
#                             "Cable to delete",
#                             default=False
#                         )
#                     },
#                     use_container_width=True, hide_index=True
#                 )
#                 cab_to_del_list = edited_cab_df.loc[edited_cab_df.cab_to_del.astype('str') == "True", "cab_tag"].tolist()
#                 if rc.button(f'Delete selected {cab_to_del_list}', use_container_width=True):
#                     delete_cable(cab_to_del_list)
#                 if st.button("SAVE CABLES", use_container_width=True):
#                     check_cables(edited_cab_df)
#                     save_cables(edited_cab_df, left_pan, right_pan)
#             else:
#                 st.write("#### :blue[No cables between selected panels]")
#         else:
#             st.warning('Some Panels not available...')
#     else:
#         st.warning('Equipment not available...')
