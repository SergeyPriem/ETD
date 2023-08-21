# -*- coding: utf-8 -*-
import base64
import time

import pandas as pd
import streamlit as st
import json
import os
import ezdxf
from streamlit_option_menu import option_menu

POSITIONS = ('Trainee', 'III cat.', 'II cat.', 'I cat.', 'Lead', 'Group Head', 'Senior', 'Dep. Head')
DEPARTMENTS = ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'En-Design', 'Remote')
STAGES = ('Detail Design', 'Basic Design', 'Feed', 'Feasibility Study', 'Adaptation')
COMPLETION = ('0%', "Cancelled", '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '99%',
              "Squad Check", "Issued", 'Approved by Client')

REVISIONS = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12',
             'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12')

PROJECT_STATUSES = ('current', 'perspective', 'final stage', 'completed', 'suspended', 'cancelled')

TRANS_STATUSES = ("Open", "Closed", "For Info", "Not Enough Data", "In Progress", "Issued Docs")

TRANS_TYPES = ('Comments', "Letter", 'Vendor Docs', 'TBE', 'FCN', 'Design Docs')


def err_handler(e):
    return f"{type(e).__name__}{getattr(e, 'args', None)}"


def tab_to_df(tab, keep_id=False):
    t_dict = [t.to_dict() for t in tab]
    t_df = pd.DataFrame(t_dict)
    if not keep_id:
        if 'id' in list(t_df.columns):
            t_df = t_df.set_index('id')
    if len(t_df) > 0:
        return t_df
    else:
        return "Empty Table"


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


def left_style():
    return st.markdown("""
        <style>
            div[data-testid="column"]:nth-of-type(1)
            {
                text-align: left;
            } 

            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: left;
            } 

            div[data-testid="column"]:nth-of-type(3)
            {
                text-align: left;
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


def open_dxf_file(path):
    try:
        doc = ezdxf.readfile(path)
        return doc
    except IOError as e:
        st.warning(f"Not a DXF file or a generic I/O error.")
        st.write(err_handler(e))
        return err_handler(e)
    except ezdxf.DXFStructureError as e:
        st.warning(f"Invalid or corrupted DXF file.")
        st.write(err_handler(e))
        return err_handler(e)
    except Exception as e:
        st.write('!!!')
        st.warning(err_handler(e))
        return err_handler(e)


def check_df(df):
    if isinstance(df, pd.DataFrame):
        if len(df):
            return True
        else:
            return False
    else:
        return False


def title_with_help(title, help_content, ratio=24, divider=True):
    # h_content = """
    #    <p style="text-align: justify; color: #249ded;">На вкладке <b>Home</b> отображаются новые
    #    <b>Задания</b> от смежных отделов (если их внесли в базу не Вы) и <b>Трансмитталы</b>.
    #    Чтобы скрыть Задания и  Трансмитталы, нажмите кнопку под соответствующим блоком.</p>
    #    <hr>
    #    <p style="text-align: justify; color: #249ded;">The <b>Home</b> tab displays new
    #    <b>Assignments</b> from related departments (if they were not entered into the database by you)
    #    and <b>Transmittals</b>. To hide Tasks and Transmittals, click the button under
    #    the corresponding block.</p>
    #    """

    lc, cc, rc = st.columns([1, ratio, 1])

    if title:
        cc.title(f':orange[{title}]')

    if rc.button('❔', key=f'{title}_help', use_container_width=True):
        cc.markdown(help_content, unsafe_allow_html=True)
        rc.button('❌️', key=f'{title}_help_close', use_container_width=True)

    # rc.text('', help=help_content)

    if divider:
        st.divider()


credentials = {
    "type": "service_account",
    "project_id": "termination-bgpp",
    "private_key_id": st.secrets['sak']['private_key_id'],
    "private_key": st.secrets['sak']['private_key'],
    "client_email": st.secrets['sak']['client_email'],
    "client_id": st.secrets['sak']['client_id'],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": st.secrets['sak']['client_x509_cert_url'],
    "universe_domain": "googleapis.com"
}


@st.cache_data(show_spinner=False)
def convert_txt_to_list(txt):
    if len(txt):
        if "." in txt and "," in txt:
            return "!!! dot and comma in the text, please use one of them"
        final_list = []
        if "." in txt:
            txt_spl = txt.split('.')
        elif "," in txt:
            txt_spl = txt.split(',')
        else:
            txt_spl = [txt]

        for i in txt_spl:
            if "-" in i:
                i_spl = i.split('-')

                i_start = int((i_spl[0]))
                i_end = int((i_spl[1]))
                if i_start > i_end:
                    print(f"Я переставил местами {i_start} и {i_end}")
                    i_start, i_end = i_end, i_start
                k = list(range(i_start, i_end + 1))
                # print(k)
                if isinstance(k, list):
                    final_list += k
            else:
                try:
                    final_list.append(int(i))
                except Exception as e:
                    st.toast(err_handler(e))
                    return
        final_list.sort()
        final_list = list(set(final_list))
        return final_list
    else:
        return []


def act_with_warning(left_function=None, left_args=None, right_function=None, right_args=None,
                     option_message="Are you sure?", left_button="YES", right_button="NO",
                     header_message=None, header_color="red", warning_message="Warning", waiting_time=7,
                     use_buttons=True):
    """
    :param left_function: function, related to left button
    :param left_args: args for 'left' function
    :param right_function: function, related to right button
    :param right_args: args for 'right' function
    :param option_message: left side inline message
    :param left_button: text of left button
    :param right_button: text of right button
    :param header_message: warning header above the buttons
    :param header_color: warning header color. Supported colors: blue, green, orange, red, violet. Default - red
    :param warning_message: white warning message above the buttons
    :param waiting_time: time of buttons presence
    :param use_buttons: if True, st.buttons will be used, else - option menu
    :return: None
    """
    if use_buttons:
        st.subheader(f"⚠️ :{header_color}[Warning! {header_message}]")
        st.subheader(f"{warning_message}")

        c1, c2, c3, c4 = st.columns([5, 1, 1, 5])

        if c2.button(left_button, use_container_width=True):
            if left_function:
                left_function(left_args)

        if c3.button(right_button, use_container_width=True):
            if right_function:
                right_function(right_args)

    else:
        c1, c2, c3 = st.columns(3)
        with c2:
            c2.subheader(f":{header_color}[{header_message}]")

            yes_no = option_menu(warning_message, options=[option_message, left_button, right_button],
                                 menu_icon='exclamation-triangle', icons=['-', '-', '-'],
                                 default_index=0, orientation='horizontal')

        if yes_no == left_button:
            if left_function:
                left_function(left_args)

        if yes_no == right_button:
            if right_function:
                right_function(right_args)

    st.write(":blue[Waiting for your decision...]")
    time.sleep(waiting_time)
    st.experimental_rerun()


def ben(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        end = time.time()
        print(f'Time spent: {round(end - start, 2)} s.')

    return wrapper


def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("temp_dxf", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    except Exception as e:
        st.warning(f"Can't save file to temp. folder: {err_handler(e)}")
        st.stop()


def add_local_background_image(image):
    with open(image, "rb") as image:
        encoded_string = base64.b64encode(image.read())
    st.markdown(
        f"""
            <style>
                .stApp {{
                    background-image: url(data:files/{"jpg"};base64,{encoded_string.decode()});
                    background-size: cover
                }}
            </style>
        """, unsafe_allow_html=True)


def hide_buttons():
    st.markdown(
        """
            <style>
                button {
                    background: none!important;
                    padding: 0!important;
                    color: white !important;
                    text-decoration: none;
                    cursor: pointer;
                    border-color: red;
                }
                button:hover {
                    text-decoration: none;
                    color: red !important;
                }
                button:focus {
                    outline: none !important;
                    box-shadow: none !important;
                    color: #249ded !important;
                }
            </style>
        """,
        unsafe_allow_html=True,
    )
    # st.markdown(
    #     """
    #         <style>
    #             button {
    #                 background: none!important;
    #                 border: none;
    #                 padding: 0!important;
    #                 color: white !important;
    #                 text-decoration: none;
    #                 cursor: pointer;
    #                 border: none !important;
    #             }
    #             button:hover {
    #                 text-decoration: none;
    #                 color: red !important;
    #             }
    #             button:focus {
    #                 outline: none !important;
    #                 box-shadow: none !important;
    #                 color: #249ded !important;
    #             }
    #         </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
