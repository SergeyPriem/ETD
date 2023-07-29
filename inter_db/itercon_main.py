# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_option_menu import option_menu

from inter_db.blocks import blocks_main
from inter_db.cables import cables_main
from inter_db.equipment import equipment_main
from inter_db.panels import panels_main
from inter_db.read_all_tabs import get_all_equip, get_all_panels, get_all_blocks, get_all_terminals, get_all_cables
from inter_db.terminals import terminals_main
from inter_db.wires import wires_main


def intercon_expander():

    st.title(':orange[Create Interconnection Wiring Diagram - under development...]')

    if st.session_state['user']['access_level'] == "dev" or st.session_state['user']['login'] == 'vyacheslav.shishov':

        preview_list = ["SELECT:", 'Equipment', 'Panels', 'Terminal Block', 'Terminals', 'Cables', 'Wires']

        prev_sel = option_menu(None, preview_list,
                               icons=['-', '-', '-', '-', '-', '-', '-', '-', '-'],
                               orientation="horizontal", default_index=0)

        if prev_sel != "SELECT:":
            # st.data_editor(st.session_state.intercon[prev_sel], use_container_width=False)

            prev_dict = {
                'Equipment': get_all_equip,
                'Panels': get_all_panels,
                'Terminal Block': get_all_blocks,
                'Terminals': get_all_terminals,
                'Cables': get_all_cables,
                # 'Wires': Wire,
            }

            act = option_menu(None,
                              ['Select required:', 'View', 'Create', 'Edit', 'Delete'],
                              icons=['-', '-', '-', '-', '-'], default_index=1, orientation='horizontal')

            if act != 'Select required:':
                if prev_sel == 'Equipment':
                    equipment_main(act, prev_dict, prev_sel)
                if prev_sel == 'Panels':
                    panels_main(act, prev_dict, prev_sel)
                if prev_sel == 'Terminal Block':
                    blocks_main(act)
                if prev_sel == 'Cables':
                    cables_main(act, prev_dict, prev_sel)
                if prev_sel == 'Terminals':
                    terminals_main(act)
                if prev_sel == 'Wires':
                    wires_main(act)
            else:
                st.write("Select the option 👆 to proceed")
        else:
            st.write("Select the option 👆 to proceed")
