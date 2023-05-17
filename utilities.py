# -*- coding: utf-8 -*-

import streamlit as st
from pathlib import Path
import time
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


# if 'delay' not in st.session_state:
#     st.session_state.delay = 3


# def reporter(text: str, duration=int(st.session_state.delay)) -> None:  #: int = st.session_state.delay
#     placeholder = st.empty()
#     if isinstance(text, str):
#         text_lower = text.lower()
#
#         yellow_list = {'already', 'mistake', 'slow', 'empty', 'warning', 'prohibited', '**prohibited**', 'moved',
#                        'no', 'should'}
#         yellow_words = set(text_lower.split()) & yellow_list
#
#         red_list = {'error', 'mistake', 'problem', 'wrong', 'failed', 'fail'}
#         red_words = set(text_lower.split()) & red_list
#     else:
#         red_words = True
#         yellow_words = False
#
#     if red_words:
#         for i in range(duration, 0, -1):
#             placeholder.error(text, icon="⚡")
#             time.sleep(1)
#     elif yellow_words:
#         for i in range(duration, 0, -1):
#             placeholder.warning(text, icon='⚠️')
#             time.sleep(1)
#     else:
#         for i in range(duration, 0, -1):
#             placeholder.success(text, icon="✅")
#             time.sleep(1)
#
#     placeholder.empty()

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


def change_global_state(changed_table: str):

    if st.session_state.login:

        new_state = {
            'server_marker': int(server_state.db_changes['server_marker']) + 1,
            'table': changed_table,
            'login': st.session_state.login
        }

        with server_state_lock["db_changes"]:
            server_state['db_changes'] = new_state
        #

        # server_state.db_changes = new_state



        #

