# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_icon=Image.open("images/small_e.jpg"),
                   page_title='ET Department', initial_sidebar_state='auto')

import datetime
import random
from streamlit_option_menu import option_menu
from admin_tools import manage_projects, manage_sets
from tasks_tab import tasks_content
from drawing_sets_tab import drawing_sets
from just_for_fun_tab import just_for_fun, emoji_content
from lesson_learned_tab import lessons_content
from pre_sets import appearance_settings, reporter, positions, departments, mail_to_name, trans_stat
from send_emails import send_mail
from settings_tab import settings_content
from transmittals_tab import transmittals_content
from users import check_user, add_to_log, get_logged_rights, \
    create_appl_user, get_user_data, update_users_in_db, move_to_former, get_settings, \
    update_user_reg_data, get_all_emails, register_user, get_appl_logins, get_logins_for_registered
from projects import confirm_task, get_my_trans, confirm_trans, get_pers_tasks, get_projects_names, \
    trans_status_to_db


def create_states():
    if 'delay' not in st.session_state:
        st.session_state.delay = 2

    if "preview_proj_stat" not in st.session_state:
        st.session_state.preview_proj_stat = False

    if "logged" not in st.session_state:
        st.session_state.logged = False

    if 'rights' not in st.session_state:
        st.session_state.rights = 'basic'

    if 'code_sent' not in st.session_state:
        st.session_state.code_sent = False

    if 'upd_code_sent' not in st.session_state:
        st.session_state.upd_code_sent = False

    if 'vert_menu' not in st.session_state:
        st.session_state.vert_menu = 1

    if 'user' not in st.session_state:
        st.session_state['user'] = None

    if 'task_preview' not in st.session_state:
        st.session_state.task_preview = False

    if 'proj_names' not in st.session_state:
        st.session_state.proj_names = get_projects_names()

    if 'trans_status' not in st.session_state:
        st.session_state.trans_status = None


create_states()
# from streamlit_profiler import Profiler

# pf = Profiler()
# pf.start()


appearance_settings()

if st.session_state.user:
    log_in_out = 'Log Out'
else:
    log_in_out = 'Log In'

if 'registered_logins' not in st.session_state:
    reg_logins = get_logins_for_registered()
    if isinstance(reg_logins, list):
        st.session_state.registered_logins = reg_logins
    else:
        reporter("Can't get users list")
        st.stop()


def update_trans_status(trans_num, trans_col):
    trans_col.subheader(f'Close Transmittal {trans_num}')
    with trans_col.form('confirm_trans'):
        out_num = st.text_input('Number of reply Transmittal')
        out_date = st.date_input('Date of reply Transmittal')
        status = st.radio("Transmittal Status", trans_stat)
        comment = st.text_area('Comments')
        out_note = f"{out_num} by {out_date}: {comment}"
        conf_but = st.form_submit_button('Update')

    if conf_but:
        st.session_state.trans_status = (trans_num, status, out_note)
        st.header(trans_num)
        st.experimental_rerun()

st.header('NO')
if st.session_state.trans_status:
    st.header("YES")
    reply = trans_status_to_db(st.session_state.trans_status)
    reporter(reply, 2)


def home_content():
    st.markdown("""
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

    empty1, content, empty2 = st.columns([5, 3, 5])
    empty21, content2, empty22 = st.columns([1, 20, 1])
    with empty1:
        st.empty()
    with empty2:
        st.empty()
    with content:
        st.title(':orange[Electrical Department]')
        if 'user' not in st.session_state:
            st.header('Welcome!')
        else:
            st.header(f'Welcome, {mail_to_name(st.session_state.user)}!')

        st.text("The Site is designed to help you in everyday routines")
        st.markdown("""
            <style>
                div[data-baseweb="tab-list"]:nth-of-type(1)
                {
                    text-align: center;
                } 
                div[data-baseweb="tab-list"]:nth-of-type(2)
                {
                    text-align: center;
                } 
                div[data-baseweb="tab-list"]:nth-of-type(3)
                {
                    text-align: center;
                } 
            </style>
            """, unsafe_allow_html=True)

        login_tab, reg_tab, change_tab = st.tabs([log_in_out, 'Registration', 'Change Password'])

        with login_tab:
            plaho = st.empty()
            login_col, logout_col = st.columns(2)

            with plaho.container():

                login = st.selectbox("Select Your Login", st.session_state.registered_logins,
                                     disabled=st.session_state.logged)
                st.write("Not in list? Register first 👆")
                password = st.text_input('Password', type='password', disabled=st.session_state.logged)
                login_but = login_col.button('Log In', disabled=st.session_state.logged, use_container_width=True)

            logout_but = logout_col.button('Log Out', disabled=not st.session_state.logged, use_container_width=True)

            if login_but:
                if len(password) < 3:
                    reporter("Password should be at least 3 symbols")
                    st.stop()
                else:

                    login_status = check_user(login, password)

                    if login_status is True:
                        st.session_state.logged = True
                        st.session_state.user = login
                        st.session_state.rights = get_logged_rights(login)
                        reply = add_to_log(login)

                        if 'ERROR' in reply.upper():
                            st.write(f"""Please sent error below to sergey.priemshiy@uzliti-en.com  
                                    or by telegram +998909598030:  
                                    {reply}""")
                            st.stop()
                        else:
                            st.experimental_rerun()
                    else:
                        st.session_state.logged = False
                        st.session_state.rights = 'basic'
                        st.session_state.user = None
                        reporter("Wrong Password")
                        st.stop()
                #
            if logout_but:
                st.session_state.logged = False
                st.session_state.user = None
                reporter("Bye! Bye! Bye! ")
                st.session_state.rights = 'basic'
                st.experimental_rerun()

            if st.session_state.logged:
                plaho.empty()

                with content2:
                    st.markdown("---")

                    ass_col, blank_col, trans_col = st.columns([10, 2, 10])
                    with ass_col:
                        df = get_pers_tasks()

                        if isinstance(df, pd.DataFrame) and len(df) > 0:
                            st.subheader(":orange[New Incoming Tasks]")
                            for ind, row in df.iterrows():
                                name_surname = mail_to_name(row.added_by)
                                st.markdown(f"""<h4>Task: {row.id}</h4>""", unsafe_allow_html=True)

                                st.markdown("""<style>
                                                .nobord td {
                                                        border-style: hidden;
                                                        margin-left: auto;
                                                        margin-right: auto;
                                                        text-align: left;
                                                    }
                                                  </style>
                                                  """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <table class="nobord">
                                <tr>
                                    <td>Project</td>
                                    <td>{row.project}</td>
                                </tr>
                                <tr>
                                    <td>Unit</td>
                                    <td>{row.unit}</td>
                                </tr>
                                <tr>
                                    <td>Speciality</td>
                                    <td>{row.speciality}</td>
                                </tr>
                                <tr>
                                    <td>Stage</td>
                                    <td>{row.stage}</td>
                                </tr>
                                <tr>
                                    <td>Issue Date</td>
                                    <td>{row.date}</td>
                                </tr>
                                <tr>
                                    <td>Description</td>
                                    <td>{row.description}</td>
                                </tr>
                                <tr>
                                    <td>Link</td>
                                    <td>{row.link}</td>
                                </tr>
                                <tr>
                                    <td>Backup Copy</td>
                                    <td>{row.backup_copy}</td>
                                </tr>
                                <tr>
                                    <td>Source</td>
                                    <td>{row.source}</td>
                                </tr>
                                <tr>
                                    <td>Comment</td>
                                    <td>{row.comment}</td>
                                </tr>
                                <tr>
                                    <td>Added By</td>
                                    <td>{name_surname}</td>
                                </tr>
                                </table>
                                <br>
                                """, unsafe_allow_html=True)

                                but_key1 = f"Confirm Task: {row.id}"
                                task_id = row.id
                                if st.button(label=but_key1, key=but_key1, type='primary', on_click=confirm_task, args=(
                                        (row.id,))):
                                    st.info(f"Task {task_id} confirmed!!")
                                st.text("")
                        else:
                            st.text('No New Tasks')

                    with trans_col:
                        df = get_my_trans(st.session_state.user)  # st.session_state.user
                        if isinstance(df, pd.DataFrame) and len(df) > 0:
                            st.subheader(":orange[New Incoming Transmittals]")
                            df = df.loc[df.status != "Closed"]
                            for ind, row in df.iterrows():
                                # name_surname = mail_to_name(row.added_by)
                                st.markdown(f"""<h4>Transmittal: {row.trans_num}</h4>""", unsafe_allow_html=True)

                                st.markdown("""<style>
                                                .nobord {
                                                        border-style: hidden;
                                                        margin-left: auto;
                                                        margin-right: auto;
                                                        text-align: left;
                                                    }
                                                  </style>
                                                  """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <table class="nobord">
                                <tr>
                                    <td>Transmittal Number</td>
                                    <td>{row.trans_num}</td>
                                </tr>
                                <tr>
                                    <td>Project</td>
                                    <td>{row.project}</td>
                                </tr>
                                <tr>
                                    <td>Subject</td>
                                    <td>{row.subject}</td>
                                </tr>

                                <tr>
                                    <td>Transmittal Date</td>
                                    <td>{row.trans_date}</td>
                                </tr>
                                <tr>
                                    <td>Is reply required?</td>
                                    <td>{"Yes" if row.ans_required else "No"}</td>
                                </tr>
                                <tr>
                                    <td>Previous Transmittal</td>
                                    <td>{row.ref_trans}</td>
                                </tr>
                                <tr>
                                    <td>Responsible</td>
                                    <td>{row.responsible}</td>
                                </tr>
                                <tr>
                                    <td>Author</td>
                                    <td>{row.author}</td>
                                </tr>
                                <tr>
                                    <td>Link</td>
                                    <td>{row.link}</td>
                                </tr>
                                <tr>
                                    <td>Type</td>
                                    <td>{row.trans_type}</td>
                                </tr>
                                <tr>
                                    <td>Notes</td>
                                    <td>{row.notes}</td>
                                </tr>
                                <tr>
                                    <td>Added By</td>
                                    <td>{row.added_by}</td>
                                </tr>
                                <tr>
                                    <td>Status</td>
                                    <td>{row.status}</td>
                                </tr>
                                </table>
                                <br>
                                """, unsafe_allow_html=True)

                                but_key1 = f"Confirm receiving: {row.trans_num}"
                                but_key2 = f"Update Status for: {row.trans_num}"

                                if st.session_state.user not in row.received:
                                    st.button(label=but_key1, key=but_key1, type='secondary',
                                              on_click=confirm_trans,
                                              args=(row.trans_num,))

                                st.button(label=but_key2, key=but_key2, type='primary',
                                          on_click=update_trans_status,
                                          args=(row.trans_num, trans_col))
                                st.text("")
                        else:
                            st.text('No New Transmittals')

        with reg_tab:
            if st.session_state.logged:
                st.subheader("You are Registered & Logged In 😎")
            else:
                appl_logins = get_appl_logins()

                if isinstance(appl_logins, list):
                    login = st.selectbox("Select Your Login", appl_logins,
                                         disabled=st.session_state.logged, key='reg_email')
                else:
                    reporter(appl_logins)
                    st.stop()

                if login in st.session_state.registered_logins:
                    st.subheader("You are Registered 😎")
                else:
                    st.write("Not in list? Send the request from your e-mail to sergey.priemshiy@uzliti-en.com")
                    with st.form("Reg_form"):
                        name = st.text_input('Your Name', disabled=st.session_state.logged)
                        surname = st.text_input('Your Surame', disabled=st.session_state.logged)
                        phone = st.text_input('Your personal Phone', disabled=st.session_state.logged)
                        telegram = st.text_input('Your personal Telegram', disabled=st.session_state.logged)
                        reg_pass_1 = st.text_input('Password', type='password', key='reg_pass_1',
                                                   disabled=st.session_state.logged)
                        reg_pass_2 = st.text_input('Repeat Password', type='password', key='reg_pass_2',
                                                   disabled=st.session_state.logged)

                        # data_chb = st.checkbox('Data is Correct', disabled=st.session_state.logged)

                        get_reg_code = st.form_submit_button('Get Confirmation Code')

                    # conf_html = ""
                    if get_reg_code:
                        if login in st.session_state.registered_logins:
                            reporter(f'User {login} is already in DataBase')
                            st.stop()

                        if len(reg_pass_2) < 3 or reg_pass_1 != reg_pass_2:
                            st.warning("""- Password should be at least 3 symbols
                            - Password and Repeat Password should be the same""")
                            st.stop()
                        if len(name) < 2 or len(surname) < 2:
                            st.warning("! Too short Name or Surname")
                            st.stop()

                        if 'conf_num' not in st.session_state:
                            st.session_state.conf_num = "".join(random.sample("123456789", 4))

                        conf_html = f"""
                            <html>
                              <head></head>
                              <body>
                                <h3>
                                  Hello, Colleague!
                                  <hr>
                                </h3>
                                <h5>
                                  You got this message because you want to register on ETD site
                                </h5>
                                <p>
                                    Please confirm your registration by entering the confirmation code 
                                    <b>{st.session_state.conf_num}</b> 
                                    at the <a href="https://design-energo.streamlit.app/">site</a> registration form
                                    <hr>
                                    Best regards, Administration 😎
                                </p>
                              </body>
                            </html>
                        """

                        if not st.session_state.code_sent:
                            user = get_user_data(login)

                            if "@" not in user.email:
                                st.warning("Can't get User's email")
                                st.stop()

                            if send_mail(receiver=user.email, cc_rec="sergey.priemshiy@uzliti-en.com",
                                         html=conf_html, subj="Confirmation of ETD site registration"):
                                st.session_state.code_sent = True
                                st.info("Confirmation Code sent to Your Company Email")
                            else:
                                st.warning("Network problems...Try again later")

                    entered_code = st.text_input("Confirmation Code from Email")

                    if st.button("Register", use_container_width=True):
                        if login in st.session_state.registered_logins:
                            reporter(f'User {login} is already in DataBase')
                            st.stop()

                        if st.session_state.conf_num != entered_code:
                            reporter("Confirmation code is wrong, try again")
                            st.stop()
                        else:
                            reply = register_user(name, surname, phone, telegram, login, reg_pass_2)
                            if 'ERROR' in reply.upper():
                                st.write('Error')
                            else:
                                reporter(reply)
                                st.experimental_rerun()

        with change_tab:
            if not st.session_state.logged:
                st.write('You should Log In first')
            else:
                with st.form("UpData"):
                    # upd_phone = st.text_input('Updated personal Phone', disabled=not st.session_state.logged)
                    # upd_telegram = st.text_input('Updated personal Telegram', disabled=not st.session_state.logged)
                    upd_pass_1 = st.text_input('Updated Password', type='password', key='upd_pass_1',
                                               disabled=not st.session_state.logged)
                    upd_pass_2 = st.text_input('Repeat Updated Password', type='password', key='upd_pass_2',
                                               disabled=not st.session_state.logged)

                    get_conf_code = st.form_submit_button("Get Confirmation Code", use_container_width=True)

                if get_conf_code:
                    if (len(upd_pass_1) < 3) or (upd_pass_1 != upd_pass_2):
                        st.warning("""❗ Password should be at least 3 symbols  
                        ❗ Password and Repeat Password should be the same""")
                        st.stop()

                    if 'upd_conf_num' not in st.session_state:
                        st.session_state.upd_conf_num = "".join(random.sample("123456789", 4))

                    upd_html = f"""
                        <html>
                          <head></head>
                          <body>
                            <h3>
                              Hello, Colleague!
                              <hr>
                            </h3>
                            <h5>
                              You got this message because you want to update your data on ETD site
                            </h5>
                            <p>
                                Please confirm your registration by entering the confirmation code 
                                <b>{st.session_state.upd_conf_num}</b> 
                                at the <a href="https://e-design.streamlit.app/">site</a> Update form
                                <hr>
                                Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """

                    if not st.session_state.upd_code_sent:
                        email_sent = send_mail(receiver=st.session_state.user, cc_rec="sergey.priemshiy@uzliti-en.com",
                                               html=upd_html, subj="Confirmation of Data Update on ETD site")
                        if email_sent is True:
                            st.session_state.upd_code_sent = True
                        else:
                            st.session_state.upd_code_sent = False
                            st.write("Confirmation code is not send. Refresh the page and try again")

                update_pass = None
                if st.session_state.upd_code_sent is True:
                    with st.form('pass_confirm'):
                        entered_upd_code = st.text_input("Confirmation Code from Email")
                        update_pass = st.form_submit_button("Update Password")

                if update_pass:
                    if st.session_state.upd_conf_num != entered_upd_code:
                        reporter("Confirmation code is wrong, try again")
                        st.stop()
                    else:
                        reply = update_user_reg_data(st.session_state.user, upd_pass_2)
                        reporter(reply)
                else:
                    st.write("After pressing 'Get Confirmation Code' you will get Confirmation Code by e-mail")
                    st.write("Enter the Code and press 'Update Password'")


def etap_py():
    phone_1, phone_content, phone_2 = st.columns([1, 9, 1])
    with phone_1:
        st.empty()
    with phone_2:
        st.empty()
    with phone_content:
        st.title(':orange[Create SLD from Load List]')
        # st.text("📞 Find a Colleague Contact")
        # st.text("📞 UNDER DEVELOPMENT")
        # name_col, pos_col, dept_col, email_col = st.columns(4, gap="medium")
        # with name_col:
        #     name = st.text_input("Name or Surname")
        # with pos_col:
        #     position = st.text_input("Position")
        # with dept_col:
        #     dept = st.text_input("Department")
        # with email_col:
        #     email = st.text_input("E-mail")
        # df = get_phones()
        # # df=df.set_index('id')
        # # edited_df = st.experimental_data_editor(df, use_container_width=True)
        # st.write(df)


def manage_users():
    users_1, users_content, users_2 = st.columns([1, 2, 1])
    with users_1:
        st.empty()
    with users_1:
        st.empty()
    with users_content:
        st.title(':orange[Manage Users]')

        users_tab1, users_tab2 = st.tabs(['Add New User', 'Edit User Details'])
        with users_tab1:
            with st.form("Add_new_user"):
                user_email = st.text_input('Email')
                user_position = st.radio('Position', positions, horizontal=True)
                st.markdown("---")
                user_department = st.radio('Department', departments, horizontal=True)
                st.markdown("---")
                user_access_level = st.radio('Access level',
                                             ('performer', 'admin', 'supervisor'), horizontal=True)
                st.markdown("---")
                user_start_date = st.date_input('Start Date', datetime.date.today())
                create_appl_user_but = st.form_submit_button('Create New User', use_container_width=True)

            if create_appl_user_but:
                reply = create_appl_user(
                    user_email, user_position, user_department, user_access_level, "current", user_start_date)
                reporter(reply)

        with users_tab2:
            list_appl_users = get_all_emails()
            employee_to_edit = st.selectbox('Select User', list_appl_users)
            edit_move = st.radio('Action', ('Edit', 'Move to Former Users'), horizontal=True)

            if edit_move == 'Edit':
                with st.form('upd_exist_user'):
                    appl_user = get_user_data(employee_to_edit)

                    try:
                        position_ind = positions.index(appl_user.position)
                    except:
                        position_ind = 0

                    position = st.radio('Position', positions,
                                        key='edit_position', horizontal=True, index=position_ind)
                    st.markdown("---")
                    try:
                        department_ind = departments.index(appl_user.department)
                    except:
                        department_ind = 0

                    department = st.radio('Department', departments,
                                          key='edit_department', horizontal=True, index=department_ind)
                    st.markdown("---")

                    access_tuple = ('performer', 'admin', 'supervisor', 'prohibited')
                    try:
                        access_ind = access_tuple.index(appl_user.access_level)
                    except Exception:
                        access_ind = 0

                    access_level = st.radio('Access level', access_tuple, horizontal=True,
                                            key='edit_access_level', index=access_ind)
                    st.markdown("---")

                    try:
                        date_from_db = appl_user.start_date
                    except:
                        date_from_db = datetime.date.today()

                    start_date = st.date_input('Start Date', date_from_db, key='start_date')

                    upd_user_but = st.form_submit_button("Update in DB", use_container_width=True)

                if upd_user_but:
                    reply = update_users_in_db(employee_to_edit, position, department, start_date, access_level)
                    reporter(reply, 3)

            if edit_move == 'Move to Former Users':
                end_date = st.date_input('End Date', key='end_date')

                if st.button('Confirm', type='primary', use_container_width=True):
                    reply = move_to_former(employee_to_edit, end_date)
                    reporter(reply)


performer_menu = ["Drawing Sets", "Transmittals", "Tasks", 'EtapPy', 'Just for fun',
                  'Lessons Learned', 'Settings']

performer_icons = ['bi bi-file-earmark-spreadsheet-fill', 'bi bi-file-arrow-down',
                   'bi bi-file-check', 'bi bi-diagram-3', 'bi bi-info-circle', 'bi bi-pen', 'bi bi-gear',
                   ]

admin_menu = ["Manage Sets"]
admin_icons = ['bi bi-bar-chart-steps']

super_menu = ["Manage Projects", "Manage Users"]
super_icons = ["bi bi-briefcase", "bi bi-person-lines-fill"]

short_menu = ["Home"]
short_icons = ['house']


def get_menus():
    if st.session_state.rights == "basic":
        menu = [*short_menu]
        icons = [*short_icons]
        return menu, icons

    if st.session_state.rights == "performer":
        menu = [*short_menu, *performer_menu]
        icons = [*short_icons, *performer_icons]
        return menu, icons

    if st.session_state.rights == "admin":
        menu = [*short_menu, *performer_menu, *admin_menu]
        icons = [*short_icons, *performer_icons, *admin_icons]
        return menu, icons

    if st.session_state.rights == "supervisor":
        menu = [*short_menu, *performer_menu, *admin_menu, *super_menu]
        icons = [*short_icons, *performer_icons, *admin_icons, *super_icons]
        return menu, icons


selected = None

if st.session_state.logged:
    st.session_state.vert_menu = int(get_settings(st.session_state.user)[0])
    st.session_state.delay = int(get_settings(st.session_state.user)[1])

    if st.session_state.vert_menu == 1:
        with st.sidebar:
            image = Image.open("images/etd.jpg")
            st.image(image, use_column_width=True)
            selected = option_menu("ET Department", get_menus()[0], icons=get_menus()[1],
                                   menu_icon="bi bi-plug", default_index=0)

            # st.info(st.session_state.rights)

    else:
        selected = option_menu(None, get_menus()[0], icons=get_menus()[1],
                               menu_icon=None, default_index=0, orientation='horizontal')
else:
    home_content()

if selected == "Home":
    home_content()

if selected == "Manage Projects":
    manage_projects()

if selected == "Manage Sets":
    manage_sets()

if selected == "Transmittals":
    transmittals_content()

if selected == "Tasks":
    tasks_content()

if selected == "Drawing Sets":
    drawing_sets()

if selected == "Just for fun":
    just_for_fun()
    emoji_content()

if selected == "EtapPy":
    etap_py()

if selected == "Manage Users":
    manage_users()

if selected == "Lessons Learned":
    lessons_content()

if selected == "Settings":
    settings_content()

# pf.stop()
