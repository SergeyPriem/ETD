# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_icon=Image.open("images/small_e.jpg"),
                   page_title='ET Department', initial_sidebar_state='auto')
import datetime
import random
import pony.orm.core
from streamlit_option_menu import option_menu
from admin_tools import manage_projects, manage_sets
from assignments_tab import assignments_content
from drawing_sets_tab import drawing_sets
from just_for_fun_tab import just_for_fun, emoji_content
from lesson_learned_tab import lessons_content
from pre_sets import appearance_settings, reporter, positions, departments
from send_emails import send_mail
from settings_tab import settings_content
from transmittals_tab import transmittals_content
from users import get_appl_emails, check_user, create_user, add_to_log, get_logged_rights, \
    create_appl_user, get_appl_user_data, update_users_in_db, move_to_former, get_registered_emails, get_settings, \
    update_user_reg_data
from pony.orm import *
from projects import get_assignments, confirm_ass, get_trans, confirm_trans

# from streamlit_profiler import Profiler

# pf = Profiler()
# pf.start()


appearance_settings()

registered_emails = get_registered_emails()

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

if st.session_state.user:
    log_in_out = 'Log Out'
else:
    log_in_out = 'Log In'

# st.cache_data(ttl=600)

def mail_to_name(mail):
    head = mail.split("@")[0]
    if "." in head:
        return (" ".join(head.split('.'))).title()
    else:
        return head
def home_content():
    empty1, content, empty2 = st.columns([2, 2, 2])
    empty21, content2, empty22 = st.columns([1, 20, 1])
    with empty1:
        st.empty()
    with empty2:
        st.empty()
    with content:
        st.title(':orange[Electrical Department]')
        st.header('Welcome!')
        st.text("The Site is designed to help you in everyday routines")

        login_tab, reg_tab, change_tab = st.tabs([log_in_out, 'Registration', 'Change Password'])
        with login_tab:
            plaho = st.empty()
            login_col, logout_col = st.columns(2)

            with plaho.container():
                if isinstance(registered_emails, list):
                    email = st.selectbox("Company Email", registered_emails, disabled=st.session_state.logged)
                else:
                    reporter("Can't get users list")
                    st.stop()
                st.write("Not in list? Register first 👆")
                password = st.text_input('Password', type='password', disabled=st.session_state.logged)
                login_but = login_col.button('Log In', disabled=st.session_state.logged, use_container_width=True)

            logout_but = logout_col.button('Log Out', disabled=not st.session_state.logged, use_container_width=True)

            if login_but:
                if len(password) < 3:
                    reporter("Password should be at least 3 symbols")
                    st.stop()
                else:

                    login_status = check_user(email, password)

                    if login_status is True:
                        st.session_state.logged = True
                        st.session_state.user = email
                        st.session_state.rights = get_logged_rights(email)
                        reply = add_to_log(email)
                        if reply == "OK":
                            reporter(f"Welcome on board! Now You can use SideBar")
                        else:
                            reporter(reply)

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

                # if len(get_pending_ass(st.session_state.user)):
                #     st.markdown("---")
                #     st.subheader(":orange[Pending Assignments]")
                with content2:
                    st.markdown("---")

                    ass_col, blank_col, trans_col = st.columns([10,2,10])
                    with ass_col:
                        st.subheader(":orange[New Incoming Assignments]")
                        df = get_assignments() #st.session_state.user
                        css = """table {border-collapse: collapse;}"""
                        if isinstance(df, pd.DataFrame):
                            for ind, row in df.iterrows():
                                name_surname = mail_to_name(row.added_by)
                                st.markdown(f"""<h4>Assignment: {row.id}</h4>""",unsafe_allow_html=True)

                                st.markdown("""<style> .nobord table, tr, td, ths {
                                        border-style: hidden;
                                  </style> """, unsafe_allow_html=True)

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
                                but_key = f"Confirm Assignment: {row.id}"
                                st.button(label=but_key, key=but_key, type='primary', on_click=confirm_ass, args=(row.id, st.session_state.user))
                                st.text("")
                        else:
                            st.info('No New Assignments')

                    with trans_col:
                        st.subheader(":orange[New Transmittals]")
                        df = get_trans(st.session_state.user)  # st.session_state.user
                        df = df[df.status != "Closed"]
                        if isinstance(df, pd.DataFrame):
                            for ind, row in df.iterrows():
                                name_surname = mail_to_name(row.added_by)
                                st.markdown(f"""<h4>New Transmittal: {row.in_trans}</h4>""",unsafe_allow_html=True)

                                st.markdown("""<style> .nobord table, tr, td, ths {
                                        border-style: hidden;
                                  </style> """, unsafe_allow_html=True)

                                st.markdown(f"""
                                <table class="nobord">
                                <tr>
                                    <td>Transmittal Number</td>
                                    <td>{row.in_trans}</td>
                                </tr>
                                <tr>
                                    <td>Project</td>
                                    <td>{row.project}</td>
                                </tr>
                                <tr>
                                    <td>Subject</td>
                                    <td>{row.subj}</td>
                                </tr>

                                <tr>
                                    <td>Transmittal Date</td>
                                    <td>{row.in_date}</td>
                                </tr>
                                <tr>
                                    <td>Is reply required?</td>
                                    <td>{"Yes" if row.ans_required else "No"}</td>
                                </tr>
                                <tr>
                                    <td>Previous Transmittal</td>
                                    <td>{row.out_trans}</td>
                                </tr>
                                <tr>
                                    <td>Responsible</td>
                                    <td>{row.users}</td>
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
                                    <td>{row.t_type}</td>
                                </tr>
                                <tr>
                                    <td>Notes</td>
                                    <td>{row.notes}</td>
                                </tr>
                                <tr>
                                    <td>Added By</td>
                                    <td>{name_surname}</td>
                                </tr>
                                </table>
                                <br>
                                """, unsafe_allow_html=True)


                                but_key = f"Add Reply for: {row.in_trans}"
                                st.button(label=but_key, key=but_key, type='primary', on_click=confirm_trans,
                                          args=(row.in_trans, st.session_state.user))
                                st.text("")
                                st.markdown("""
                                """)
                        else:
                            st.info('No New Transmittals')

        with reg_tab:
            if st.session_state.logged:
                st.subheader("You are Registered & Logged In 😎")
            else:
                appl_emails = get_appl_emails()

                if isinstance(appl_emails, pony.orm.core.QueryResult):
                    company_email = st.selectbox("Select Your Company Email", appl_emails,
                                                 disabled=st.session_state.logged, key='reg_email')
                else:
                    reporter(appl_emails)
                    st.stop()

                if company_email in registered_emails:
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

                        reg_button = st.form_submit_button('Register')

                    # conf_html = ""
                    if reg_button:
                        if company_email in registered_emails:
                            reporter(f'User {company_email} is already in DataBase')
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
                            if send_mail(receiver=company_email, cc_rec="sergey.priemshiy@uzliti-en.com",
                                      html=conf_html, subj="Confirmation of ETD site registration"):
                                st.session_state.code_sent = True
                                st.info("Confirmation Code sent to Your Company Email")
                            else:
                                st.warning("Network problems...Try again later")


                    entered_code = st.text_input("Confirmation Code from Email")

                    if st.button("Confirm Code"):
                        if company_email in registered_emails:
                            reporter(f'User {company_email} is already in DataBase')
                            st.stop()

                        if st.session_state.conf_num != entered_code:
                            reporter("Confirmation code is wrong, try again")
                            st.stop()
                        else:
                            reply = create_user(name, surname, phone, telegram, company_email, reg_pass_2)
                            reporter(reply)

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

                    get_conf_code = st.form_submit_button("Get Confirmation Code")

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

st.cache_data(ttl=600)
def phone_directory():
    phone_1, phone_content, phone_2 = st.columns([1, 9, 1])
    with phone_1:
        st.empty()
    with phone_2:
        st.empty()
    with phone_content:
        st.title(':orange[Phone Directory]')
        st.text("📞 Find a Colleague Contact")
        st.text("📞 UNDER DEVELOPMENT")
        name_col, pos_col, dept_col, email_col = st.columns(4, gap="medium")
        with name_col:
            name = st.text_input("Name or Surname")
        with pos_col:
            position = st.text_input("Position")
        with dept_col:
            dept = st.text_input("Department")
        with email_col:
            email = st.text_input("E-mail")
        # df = get_phones()
        # # df=df.set_index('id')
        # # edited_df = st.experimental_data_editor(df, use_container_width=True)
        # st.write(df)


st.cache_data(ttl=600)


def manage_users():
    users_1, users_content, users_2 = st.columns([1, 2, 1])
    with users_1:
        st.empty()
    with users_1:
        st.empty()
    with users_content:
        st.title(':orange[Manage Users]')

        users_tab1, users_tab2 = st.tabs(['Add Applied User', 'Edit User Details'])
        with users_tab1:
            with st.form("Add_appl_user"):
                user_email = st.text_input('Email')
                st.markdown("---")
                user_position = st.radio('Position', positions, horizontal=True)
                st.markdown("---")
                user_department = st.radio('Department', departments, horizontal=True)
                st.markdown("---")
                user_access_level = st.radio('Access level',
                                             ('performer', 'admin', 'supervisor'), horizontal=True)
                st.markdown("---")
                user_start_date = st.date_input('Start Date', datetime.date.today())
                st.markdown("---")
                create_appl_user_but = st.form_submit_button('Create New User', use_container_width=True)

            if create_appl_user_but:
                reply = create_appl_user(
                    user_email, user_position, user_department, user_access_level, "current", user_start_date)
                reporter(reply)

        with users_tab2:
            list_appl_users = get_appl_emails()
            employee_to_edit = st.selectbox('Select User', list_appl_users)
            st.markdown("---")
            edit_move = st.radio('Action', ('Edit', 'Move to Former Users'), horizontal=True)
            st.markdown("---")

            if edit_move == 'Edit':
                appl_user = get_appl_user_data(employee_to_edit)

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
                st.markdown("---")
                if st.button("Update in DB", use_container_width=True):
                    reply = update_users_in_db(employee_to_edit, position, department,
                                               start_date, access_level)
                    reporter(reply)

            if edit_move == 'Move to Former Users':
                end_date = st.date_input('End Date', key='end_date')

                if st.button('Confirm', type='primary', use_container_width=True):
                    reply = move_to_former(employee_to_edit, end_date)
                    reporter(reply)


performer_menu = ["Drawing Sets", "Transmittals", "Assignments", 'Phone Directory', 'Just for fun',
                  'Lessons Learned', 'Settings']

performer_icons = ['bi bi-file-earmark-spreadsheet-fill', 'bi bi-file-arrow-down',
                   'bi bi-file-check', 'bi bi-telephone', 'bi bi-info-circle', 'bi bi-pen', 'bi bi-gear',
                   ]

admin_menu = ["Manage Sets"]
admin_icons = ['bi bi-kanban']

super_menu = ["Manage Projects", "Manage Users"]
super_icons = ["bi bi-briefcase", "bi bi-person-lines-fill"]

short_menu = ["Home"]
short_icons = ['house']

st.cache_data(ttl=600)


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

if selected == "Assignments":
    assignments_content()

if selected == "Drawing Sets":
    drawing_sets()

if selected == "Just for fun":
    just_for_fun()
    emoji_content()

if selected == "Phone Directory":
    phone_directory()

if selected == "Manage Users":
    manage_users()

if selected == "Lessons Learned":
    lessons_content()

if selected == "Settings":
    settings_content()

# pf.stop()
