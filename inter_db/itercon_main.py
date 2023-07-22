# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_option_menu import option_menu

from inter_db.equipment import create_equipment
from inter_db.read_all_tabs import get_all_equip, get_all_panels, get_all_blocks, get_all_terminals, get_all_cables

def intercon_expander():
    with st.expander('CREATE INTERCONNECTION WIRING DIAGRAM'):
        st.title(':orange[Create Interconnection Wiring Diagram - under development...]')

        if st.session_state['user']['access_level'] == "dev":
            l_col, c_col, r_col = st.columns(3)
            # l_col.markdown('Select the Operation Mode', unsafe_allow_html=False,
            #                help="!!! If switched without save - data will be lost")
            # with c_col:
                # local_remote = option_menu(None, ['LOCAL', 'REMOTE', 'DB'],
                #                            icons=['-', '-', '-', ], orientation="horizontal",
                #                            default_index=2)
            # if local_remote != 'DB':
            #     if local_remote == "LOCAL":
            #         if st.session_state.intercon['doc'] is None:
            #             cr_l, cr_r = st.columns(2, gap='medium')
            #             cr_l.text('')
            #             cr_l.text('')
            #             cr_l.info('Add the File of Interconnection 👉')
            #             st.session_state.intercon['doc'] = cr_r.file_uploader('INTERCONNECTION FILE', 'xlsx')
            #
            #         else:
            #             open_inercon_doc()
            #             work, close_b = st.columns([12, 2], gap="medium")
            #             work.info(f"#### You are working with document :blue[{st.session_state.intercon['doc'].name}]")
            #             close_b.button('Save', use_container_width=True)
            #
            #     if local_remote == "REMOTE":
            #
            #         if st.session_state.intercon['doc'] is None:
            #             gc = gspread.service_account_from_dict(credentials)
            #             s_sh = gc.open('termination BGPP')
            #             st.session_state.intercon['doc'] = s_sh
            #             open_intercon_google()
            #         else:
            #             work, close_b = st.columns([12, 2], gap="medium")
            #             work.info(f"#### You are working with CLOUD document :blue[termination BGPP]")
            #             if close_b.button('Save to G-sheet', use_container_width=True):
            #                 save_to_gsheet()
            #             # if close_b.button('Download and Close', use_container_width=True):
            #             #     close_intercon_doc()
            #             #     st.experimental_rerun()
            #             if st.session_state['user']['access_level'] == "dev":
            #                 close_b.write(
            #                     "[Open file](https://docs.google.com/spreadsheets/d/1AV3RGFBL-ZiR8AIlR0WW7aJvnFYnHtY78xrMRZ3UavQ/edit#gid=1924125475)")
            #
            #     st.divider()
            #
            #     if st.session_state.intercon['doc']:
            #
            #         preview_list = ["VIEW:", 'equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']
            #
            #         prev_sel = option_menu(None, preview_list,
            #                                icons=['search', '-', '-', '-', '-', '-', '-', '-', '-'],
            #                                orientation="horizontal", default_index=0)
            #
            #         if prev_sel != "VIEW:":
            #             st.data_editor(st.session_state.intercon[prev_sel], use_container_width=False)
            #
            #         else:
            #             st.write("Here you can preview Connections related Tables")
            #         st.divider()
            #
            #         action = option_menu(None, ['EDIT:', 'Equipment', 'Panel', 'Terminal Block', 'Cable',
            #                                     'Cable Wires'],
            #                              icons=['pencil-square', '1-circle', '2-circle', '3-circle', '4-circle',
            #                                     '5-circle', ],
            #                              orientation="horizontal")
            #         if action == 'EDIT:':
            #             st.write("Here you can edit Connections related Tables")
            #
            #         if action == 'Equipment':
            #             edit_equipment()
            #
            #         if action == 'Panel':
            #             edit_panel()
            #
            #         if action == 'Terminal Block':
            #             edit_block()
            #
            #         if action == 'Cable':
            #             edit_cab_con()
            #
            #         if action == 'Cable Wires':
            #             edit_wires()

            preview_list = ["VIEW:", 'Equipment', 'Panels', 'Terminal block', 'Terminals', 'Cables', 'Wires']

            prev_sel = option_menu(None, preview_list,
                                   icons=['search', '-', '-', '-', '-', '-', '-', '-', '-'],
                                   orientation="horizontal", default_index=0)

            if prev_sel != "VIEW:":
                # st.data_editor(st.session_state.intercon[prev_sel], use_container_width=False)

                prev_dict = {
                    'Equipment': [get_all_equip, st.session_state.inter_stat['equipment']],
                    'Panels': [get_all_panels, st.session_state.inter_stat['panel']],
                    'Terminal block': [get_all_blocks, st.session_state.inter_stat['block']],
                    'Terminals': [get_all_terminals, st.session_state.inter_stat['terminal']],
                    'Cables': [get_all_cables, st.session_state.inter_stat['cable']]
                    # 'Wires': Wire,
                }

                # st.write(get_all_data(prev_dict.get(prev_sel)))


                act = option_menu(None,
                                  ['Select required:', 'View', 'Create', 'Update', 'Delete'],
                                  icons=['-', '-', '-', '-', '-'], default_index=0, orientation='horizontal')

                if act == 'View' and prev_sel == 'Equipment':
                    st.write(prev_dict[prev_sel][0](prev_dict[prev_sel][1]))

                if act == 'Create' and prev_sel == 'Equipment':
                    create_equipment()
            else:
                st.write("Here you can preview Connections related Tables")
            st.divider()

