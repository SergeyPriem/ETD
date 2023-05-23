# -*- coding: utf-8 -*-
import time

import streamlit as st
import json
import os

from projects import get_sod_repeat, get_proj_repeat, get_tasks_repeat, get_trans_repeat

positions = ('Trainee', 'III cat.', 'II cat.', 'I cat.', 'Lead', 'Group Head', 'Senior', 'Dep. Head')
departments = ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'Remote')
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
                "project": {"id": 1, "user": None},
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

            except Exception as e:
                return f"Can't open file{err_handler(e)}"

            data[tab_name]['id'] += 1
            data[tab_name]['user'] = st.session_state.user['login']

            try:
                with open("temp_dxf/state.json", "w", encoding="utf-8") as f:
                    json.dump(data, f)
                return 'Data is updated'
            except Exception as e:
                return f"Can't save file{err_handler(e)}"
        else:
            return "File not found"
    else:
        return "Wrong Data Format"


def err_handler(e):
    return f"{type(e).__name__}{getattr(e, 'args', None)}"


def update_tables():
    st.session_state.new_state = get_state()

    counter = 0

    for table in ('sod', 'task', 'trans', 'project'):
        if st.session_state.local_marker[table]['id'] != st.session_state.new_state[table]['id']:

            counter += 1

            try:
                upd_login = st.session_state.new_state[table]['user']
            except:
                upd_login = None

            reply_dict = {
                'sod': get_sod_repeat,
                'project': get_proj_repeat,
                'task': get_tasks_repeat,
                'trans': get_trans_repeat,
            }

            reply = reply_dict.get(table)()

            if reply['status'] == 200:
                st.session_state.adb[table] = reply[table]
                st.session_state.refresh_status = f'Units Updated by {upd_login}'
                st.session_state.local_marker[table]['id'] = st.session_state.new_state[table]['id']

                if st.session_state.user['vert_menu'] == 1:
                    st.sidebar.success(f"Table {table} was updated by {upd_login}. Data is refreshed")
                    time.sleep(1)
                    return None
                else:
                    return f"Table {table} was updated by {upd_login}. Data is refreshed"

            else:
                st.session_state.refresh_status = f"{reply['status']} by {upd_login}"
                return f"{reply['status']} by {upd_login}"

    if counter:
        st.experimental_rerun()
