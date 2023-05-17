# -*- coding: utf-8 -*-

import streamlit as st
from pathlib import Path
import time
import copy
from streamlit_server_state import server_state, server_state_lock, no_rerun, force_rerun_bound_sessions

positions = ('Trainee', 'III cat.', 'II cat.', 'I cat.', 'Lead', 'Group Head', 'Senior', 'Dep. Head')
departments = ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'Remote')
# specialities = ('Architecture', 'Civil', 'HVAC', 'WSS', 'Telecom', 'F&G', 'Instrument', 'Process', 'Plot Plan',
#                 'Building-Process', 'Cathodic Protection', 'Estimators', 'Thermal', 'ProgMan')
# specialities_rus = ('Архитектура', 'ОВ', 'ВК', 'Связь', 'СПГО', 'КИП', 'Технология',
#                     'ЭХЗ', 'Сметчики', 'Теплотехники', 'Строители')
stages = ('Detail Design', 'Basic Design', 'Feed', 'Feasibility Study', 'Adaptation')
sod_statuses = (
    '0%', "Cancelled", '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '99%', "Squad Check", "Issued",
    'Approved by Client')

sod_revisions = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12',
                 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12')

proj_statuses = ('current', 'perspective', 'final stage', 'completed', 'suspended', 'cancelled')

trans_stat = ("Open", "Closed", "For Info", "Not Enough Data", "In Progress", "Issued Docs")

trans_types = ('Comments', "Letter", 'Vendor Docs', 'TBE', 'FCN', 'Design Docs')


def appearance_settings():
    hide_menu_style = """
            <style>
            #rMainMenu {visibility: hidden; }
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def get_list_index(a_list: list, elem: str) -> int:
    try:
        ind = a_list.index(elem)
        return ind
    except:
        return 0


def center_style():
    return st.markdown("""
        <style>
            div[data-testid="column"]:nth-of-type(1)
            {
                text-align: center;
            } 

            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: center;
            } 

            div[data-testid="column"]:nth-of-type(3)
            {
                text-align: center;
            } 
        </style>
        """, unsafe_allow_html=True)



def get_cur_u_id():
    u_df = st.session_state.adb['users']
    u_id = u_df[u_df.login == st.session_state.login].index.to_numpy()[0]

    return u_id


def mail_to_name(mail):
    try:
        head = mail.split("@")[0]
        if "." in head:
            return (" ".join(head.split('.'))).title()
        else:
            return head
    except AttributeError:
        return "Colleague"


BACKUP_FOLDER: Path = Path('//uz-fs/Uzle/Work/Отдел ЭЛ/Архив заданий/')


def check_global_state():
    st.session_state.temp_log.append('change_global_state')

    # # st.session_state.new_state = {
    # #     "serial": int(server_state.db_changes['serial']) + 1,
    # #     "table": changed_table,
    # #     "login": st.session_state.login,
    # # }
    #
    # st.session_state.temp_log.append(f"new_state = {st.session_state.new_state}")
    # st.session_state.temp_log.append(f"st.session_state.local_marker = {st.session_state.local_marker}")

    if int(st.session_state.local_marker['serial']) != int(st.session_state.new_state['serial']):

        # st.session_state.temp_log.append(
        #     f"INSIDE the condition {int(server_state.db_changes['serial']) != int(new_state['serial'])}"
        # )
        #
        # st.session_state.temp_log.append(
        #     f"INSIDE the condition {int(server_state.db_changes['serial']) != int(new_state['serial'])}"
        # )

        # server_state.db_changes = copy.deepcopy(new_state)
        #
        # st.session_state.temp_log.append(
        #     f"BEFORE WITH server_state.db_changes={server_state.db_changes}"
        # )

        with server_state_lock['db_changes']:
            server_state.db_changes = copy.deepcopy(st.session_state.new_state)


def change_global_number(tab_name: str):
    st.session_state.new_state['serial'] += 1
    st.session_state.new_state['table'] = tab_name
    st.session_state.new_state['login'] = st.session_state.login
    st.experimental_rerun()





