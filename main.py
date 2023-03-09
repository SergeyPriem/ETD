# -*- coding: utf-8 -*-

import datetime
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
from admin_tools import manage_projects, manage_sets
from assignments_tab import assignments_content
from drawing_sets_tab import drawing_sets
from just_for_fun_tab import just_for_fun, emoji_content
from pre_sets import appearance_settings, reporter, positions, departments
from transmittals_tab import transmittals_content
from users_db import get_appl_emails, check_user, create_user, add_to_log, get_logged_rights, get_phones, \
    create_appl_user, get_appl_user_data, update_users_in_db, move_to_former, get_registered_emails

st.set_page_config(layout="wide", page_icon=':coffee:', page_title='ET Department', initial_sidebar_state='auto')

# from streamlit_profiler import Profiler
#
# pf = Profiler()
# pf.start()

appearance_settings()

registered_emails = get_registered_emails()

if "preview_proj_stat" not in st.session_state:
    st.session_state.preview_proj_stat = False

if "logged" not in st.session_state:
    st.session_state.logged = False

if 'rights' not in st.session_state:
    st.session_state.rights = 'basic'

with st.sidebar.container():
    image = Image.open("images/lamp.jpg")
    st.image(image, use_column_width=True)


def home_content():
    # st.write(get_registered_emails())
    # # st.write([i['company_email'] for i in get_registered_emails().data])
    empty1, content, empty2 = st.columns([3, 2, 3])
    with empty1:
        st.empty()
    with empty2:
        st.empty()
    with content:
        st.title(':orange[Electrical Department]')
        st.header('Welcome!')
        st.text("The Site is attended to help you in everyday routines")

        login_tab, reg_tab = st.tabs(['Log in', 'Registration'])
        with login_tab:

            email = st.selectbox("Company Email", registered_emails, disabled=st.session_state.logged)
            st.write("Not in list? Register first 👆")
            password = st.text_input('Password', type='password', disabled=st.session_state.logged)
            login_col, logout_col = st.columns(2)

            login_but = login_col.button('Log In', disabled=st.session_state.logged, use_container_width=True)
            logout_but = logout_col.button('Log Out', disabled=not st.session_state.logged, use_container_width=True)

            if login_but:
                if len(password) < 3:
                    reporter("Password should be at least 3 symbols", 3)
                    st.stop()
                else:
                    login_status = check_user(email, password)
                    if login_status is True:
                        st.session_state.logged = True
                        st.session_state.user = email
                        st.session_state.rights = get_logged_rights(email)
                        reply = add_to_log(email)
                        if reply == "OK":
                            reporter(f"Welcome on board! Now You can use SideBar", 2)
                        else:
                            reporter(reply, 3)
                        st.experimental_rerun()
                    else:
                        st.session_state.logged = False
                        st.session_state.rights = 'basic'
                        st.session_state.user = None
                        reporter("Wrong Password", 2)
                        st.stop()
                #
            if logout_but:
                st.session_state.logged = False
                reporter("Bye! Bye! Bye! ", 1)
                st.session_state.rights = 'basic'
                st.experimental_rerun()

        with reg_tab:
            company_email = st.selectbox("Select Your Company Email", get_appl_emails(),
                                         disabled=st.session_state.logged, key='reg_email')
            st.write("Not in list? Send the request from your company e-mail to sergey.priemshiy@uzliti-en.com")
            name = st.text_input('Your Name', disabled=st.session_state.logged)
            surname = st.text_input('Your Surame', disabled=st.session_state.logged)
            phone = st.text_input('Your personal Phone', disabled=st.session_state.logged)
            telegram = st.text_input('Your personal Telegram', disabled=st.session_state.logged)
            reg_pass_1 = st.text_input('Password', type='password', key='reg_pass_1',
                                       disabled=st.session_state.logged)
            reg_pass_2 = st.text_input('Repeat Password', type='password', key='reg_pass_2',
                                       disabled=st.session_state.logged)
            if st.button('Register', disabled=st.session_state.logged):
                if len(reg_pass_2) < 3 or reg_pass_1 != reg_pass_2:
                    st.warning("""- Password should be at least 3 symbols
                    - Password and Repeat Password should be the same""")
                    st.stop()
                if len(name) < 2 or len(surname) < 2:
                    st.warning("exclamation-triangle-fill Too short Name or Surname")
                    st.stop()
                reply = create_user(name, surname, phone, telegram, company_email, reg_pass_2)
                reporter(reply, 10)


def phone_directory():
    phone_1, phone_content, phone_2 = st.columns([1, 9, 1])
    with phone_1:
        st.empty()
    with phone_2:
        st.empty()
    with phone_content:
        st.title(':orange[Phone Directory]')
        # st.header('Welcome!')
        st.text("📞 Find a Colleague Contact")
        name_col, surmname_col, dept_col, email_col = st.columns(4, gap="medium")
        with name_col:
            name = st.text_input("Name")
        with surmname_col:
            surname = st.text_input("Surame")
        with dept_col:
            dept = st.text_input("Department")
        with email_col:
            email = st.text_input("E-mail")
        df = get_phones()
        edited_df = st.experimental_data_editor(df, use_container_width=True)


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
            user_email = st.text_input('Email')
            user_position = st.radio('Engineer', positions, horizontal=True)
            user_department = st.radio('Department', departments, horizontal=True)
            user_access_level = st.radio('Access level',
                                         ('performer', 'admin', 'supervisor'), horizontal=True)
            user_start_date = st.date_input('Start Date', datetime.date.today())

            if st.button('Create New User', use_container_width=True):
                reply = create_appl_user(
                    user_email, user_position, user_department, user_access_level, user_start_date)

                reporter(reply, 3)

        with users_tab2:
            list_appl_users = get_appl_emails()
            employee_to_edit = st.selectbox('Select User', list_appl_users)

            edit_move = st.radio('What to do?', ('Edit', 'Move to Former Users'), horizontal=True,
                                 label_visibility="collapsed")

            if edit_move == 'Edit':
                appl_user = get_appl_user_data(employee_to_edit)

                try:
                    position_ind = positions.index(appl_user.position)
                except:
                    position_ind = 0
                position = st.radio('Position', positions,
                                    key='edit_position', horizontal=True, index=position_ind)

                try:
                    department_ind = departments.index(appl_user.department)
                except:
                    department_ind = 0
                department = st.radio('Department', departments,
                                      key='edit_department', horizontal=True, index=department_ind)

                access_tuple = ('performer', 'admin', 'supervisor', 'prohibited')
                try:
                    access_ind = access_tuple.index(appl_user.access_level)
                except Exception:
                    access_ind = 0

                access_level = st.radio('Access level', access_tuple, horizontal=True,
                                        key='edit_access_level', index=access_ind)
                try:
                    date_from_db = appl_user.start_date
                except:
                    date_from_db = datetime.date.today()

                start_date = st.date_input('Start Date', date_from_db, key='start_date')

                if st.button("Update in DB", use_container_width=True):
                    reply = update_users_in_db(employee_to_edit, position, department,
                                               start_date, access_level)
                    reporter(reply, 3)

            if edit_move == 'Move to Former Users':
                end_date = st.date_input('End Date', key='end_date')

                if st.button('Confirm', type='primary', use_container_width=True):
                    reply = move_to_former(employee_to_edit, end_date)
                    reporter(reply, 3)


performer_menu = ["Drawing Sets", "Transmittals", "Assignments", 'Phones', 'Just for fun',
                  'Settings']

performer_icons = ['bi bi-file-earmark-spreadsheet-fill', 'bi bi-file-arrow-down',
                   'bi bi-file-check', 'bi bi-telephone', 'bi bi-info-circle', 'bi bi-gear',
                   ]

admin_menu = ["Manage Sets"]
admin_icons = ['bi bi-kanban']

super_menu = ["Manage Projects", "Manage Users"]
super_icons = ["bi bi-briefcase", "bi bi-person-lines-fill"]

short_menu = ["Welcome"]
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


with st.sidebar:
    selected = option_menu("ET Department", get_menus()[0], icons=get_menus()[1],
                           menu_icon="bi bi-plug", default_index=0)

if selected == "Welcome":
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

if selected == "Phones":
    phone_directory()

if selected == "Manage Users":
    manage_users()

# pf.stop()
