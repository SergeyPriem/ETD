# -*- coding: utf-8 -*-
import streamlit as st
from streamlit_option_menu import option_menu

from inter_db.blocks import blocks_main
from inter_db.cables import cables_main
from inter_db.equipment import equipment_main
from inter_db.panels import panels_main
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

            act = option_menu(None,
                              ['Select acton:', 'Create', 'Copy', 'Edit', 'Delete'],
                              icons=['-', '-', '-', '-', 'exclamation-octagon'],
                              default_index=0, orientation='horizontal')

            st.divider()

            if act != 'Select acton:':
                if prev_sel == 'Equipment':
                    equipment_main(act)
                if prev_sel == 'Panels':
                    panels_main(act)
                if prev_sel == 'Terminal Block':
                    blocks_main(act)
                if prev_sel == 'Cables':
                    cables_main(act)
                if prev_sel == 'Terminals':
                    terminals_main(act)
                if prev_sel == 'Wires':
                    wires_main(act)
            else:
                st.write("Select the option 👆 to proceed")
        else:
            st.write("Select the option 👆 to proceed")
