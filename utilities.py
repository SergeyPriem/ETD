# -*- coding: utf-8 -*-

import streamlit as st
from pathlib import Path
import json
import os

# import time
# import copy
# from streamlit_server_state import server_state, server_state_lock, no_rerun, force_rerun_bound_sessions


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


def get_state():
    if os.path.exists("temp_dxf/state.json"):
        print('file exists')
        try:
            with open("temp_dxf/state.json", "r", encoding="utf-8") as f:
                state_json = f.read()
            cur_state = json.loads(state_json)
            return cur_state
        except Exception as e:
            return err_handler(e)
    else:
        return "File does not exist"


def set_init_state(data=None):
    if isinstance(data, dict):
        if os.path.exists("temp_dxf/state.json"):
            try:
                with open("temp_dxf/state.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)
                return 'Data is set'
            except Exception as e:
                return err_handler(e)
        else:
            data = {
                "sod": {"id": 1, "user": None},
                "trans": {"id": 1, "user": None},
                "proj": {"id": 1, "user": None},
                "task": {"id": 1, "user": None},
            }
            try:
                with open("temp_dxf/state.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)
                return "File Created"
            except Exception as e:
                return err_handler(e)
    else:
        return "Wrong Data Format"


def update_state(tab_name: str):
    if isinstance(tab_name, str):
        if os.path.exists("temp_dxf/state.json"):
            try:
                with open("temp_dxf/state.json", "r", encoding="utf-8") as f:
                    state_json = f.read()
                    data = json.loads(state_json)
                # new_id = int(data['id']) + 1

            except Exception as e:
                # st.title(f"Can't open file{err_handler(e)}")
                return f"Can't open file{err_handler(e)}"

            # new_data = {
            #     'id': new_id,
            #     'table': tab_name,
            #     'user': st.session_state.user['login'],
            # }

            # new_data = {
            #     "sod": {"id": 1, "user": "sergey.priemshiy"},
            #     "trans": {"id": 1, "user": "sergey.priemshiy"},
            #     "proj": {"id": 1, "user": "sergey.priemshiy"},
            #     "units": {"id": 1, "user": "sergey.priemshiy"},
            # }
            #
            #
            data[tab_name]['id'] += 1
            data[tab_name]['user'] = st.session_state.user['login']


            try:
                with open("temp_dxf/state.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)
                # st.title('Data is updated')
                return 'Data is updated'
            except Exception as e:
                # st.title(f"Can't save file{err_handler(e)}")
                return f"Can't save file{err_handler(e)}"
        else:
            # st.title("File not found")
            return "File not found"
    else:
        # st.title("Wrong Data Format")
        return "Wrong Data Format"


def err_handler(e):
    return f"{type(e).__name__}{getattr(e, 'args', None)}"
