# -*- coding: utf-8 -*-

import streamlit as st
import time

positions = ('Trainee', 'III cat.', 'II cat.', 'I cat.', 'Lead', 'Group Head', 'Senior')
departments = ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'Remote')
specialities = ('Architecture', 'Civil', 'HVAC', 'WSS', 'Telecom', 'F&G', 'Instrument', 'Process',
                'Building-Process', 'Cathodic Protection', 'Estimators', 'Thermal')
specialities_rus = ('Архитектура', 'ОВ', 'ВК', 'Связь', 'СПГО', 'КИП', 'Технология',
                'ЭХЗ', 'Сметчики', 'Теплотехники', 'Строители')
stages = ('Detail Design', 'Basic Design', 'Feed', 'Feasibility Study', 'Adaptation')
sod_statuses = (
'0%', "Cancelled", '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '99%', "Squad Check", "Issued",
'Approved by Client')
proj_statuses = ('current', 'perspective', 'complete', 'final stage', 'cancelled', 'suspended')

connect_sleep = 0.8 #0.75
request_sleep = 0.6  #0.6


def appearance_settings():

    hide_menu_style = """
            <style>
            #rMainMenu {visibility: hidden; }
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def reporter(text: str, duration = st.session_state.delay) -> None:
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


# @st.cache_data
# def add_logo():
#     st.markdown(
#         """
#         <style>
#             [data-testid="stSidebarNav"] {
#                 background-image: url(http://placekitten.com/200/200);
#                 background-repeat: no-repeat;
#                 padding-top: 120px;
#                 background-position: 70px 20px;
#             }
#             [data-testid="stSidebarNav"]::before {
#                 content: "ETD";
#                 margin-left: 20px;
#                 margin-top: 20px;
#                 font-size: 30px;
#                 position: relative;
#                 top: 100px;
#             }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )
