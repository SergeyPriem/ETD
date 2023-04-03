# -*- coding: utf-8 -*-

import streamlit as st
import time
from pathlib import Path

positions = ('Trainee', 'III cat.', 'II cat.', 'I cat.', 'Lead', 'Group Head', 'Senior', 'Dep. Head')
departments = ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'Remote')
specialities = ('Architecture', 'Civil', 'HVAC', 'WSS', 'Telecom', 'F&G', 'Instrument', 'Process',
                'Building-Process', 'Cathodic Protection', 'Estimators', 'Thermal')
specialities_rus = ('Архитектура', 'ОВ', 'ВК', 'Связь', 'СПГО', 'КИП', 'Технология',
                    'ЭХЗ', 'Сметчики', 'Теплотехники', 'Строители')
stages = ('Detail Design', 'Basic Design', 'Feed', 'Feasibility Study', 'Adaptation')
sod_statuses = (
    '0%', "Cancelled", '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '99%', "Squad Check", "Issued",
    'Approved by Client')
proj_statuses = ('current', 'perspective', 'completed', 'final stage', 'cancelled', 'suspended')

trans_stat = ("Open", "Closed", "For Info", "Not Enough Data", "In Progress")

trans_types = ('Comments', "Letter", 'Vendor Docs', 'TBE')
@st.cache_data
def appearance_settings():
    hide_menu_style = """
            <style>
            #rMainMenu {visibility: hidden; }
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


if 'delay' not in st.session_state:
    st.session_state.delay = 3

def reporter(text: str, duration=st.session_state.delay) -> None:  #: int = st.session_state.delay
    placeholder = st.empty()
    if isinstance(text, str):
        text_lower = text.lower()

        yellow_list = {'already', 'mistake', 'slow', 'empty', 'warning', 'prohibited', '**prohibited**', 'moved',
                       'no', 'should'}
        yellow_words = set(text_lower.split()) & yellow_list

        red_list = {'error', 'mistake', 'problem', 'wrong', 'failed', 'fail'}
        red_words = set(text_lower.split()) & red_list
    else:
        red_words = True
        yellow_words = False

    if red_words:
        for i in range(duration, 0, -1):
            placeholder.error(text, icon="⚡")
            time.sleep(1)
    elif yellow_words:
        for i in range(duration, 0, -1):
            placeholder.warning(text, icon='⚠️')
            time.sleep(1)
    else:
        for i in range(duration, 0, -1):
            placeholder.success(text, icon="✅")
            time.sleep(1)

    placeholder.empty()

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

