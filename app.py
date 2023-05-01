# -*- coding: utf-8 -*-
import time
import pandas as pd
import streamlit as st
from PIL import Image
import datetime
import random
from streamlit_option_menu import option_menu
from admin_tools import manage_projects, get_list_index
from scripts import xl_to_sld
from tasks_tab import tasks_content
from drawing_sets_tab import drawing_sets, manage_units
from just_for_fun_tab import just_for_fun
from lesson_learned_tab import lessons_content
from utilities import appearance_settings, positions, departments, mail_to_name, trans_stat, get_cur_u_id
from send_emails import send_mail
from settings_tab import settings_content
from transmittals_tab import transmittals_content
from users import check_user, add_to_log, create_appl_user, update_users_in_db, move_to_former, register_user, \
    err_handler
from projects import confirm_task, confirm_trans, trans_status_to_db, get_all, get_table
from models import Users, Task, Trans
import openpyxl
st.set_page_config(layout="wide", page_icon=Image.open("images/small_logo.jpg"),
                   page_title='ET Department', initial_sidebar_state='auto')


def home_tasks():
    u_id = get_cur_u_id()
    task_df = st.session_state.adb['task']
    sod_df = st.session_state.adb['sod']
    proj_df = st.session_state.adb['project']
    spec = st.session_state.adb['speciality']

    task_df = task_df.loc[task_df.in_out == "In"]
    task_df.loc[:, 'new_id'] = task_df.index
    task_df = task_df.merge(sod_df[['project_id', 'set_name', 'coord_id', 'perf_id']],
                            how='left', left_on='s_o_d', right_on='id')
    task_df = task_df[(task_df.coord_id == u_id) | (task_df.perf_id == u_id)]
    task_df = task_df.merge(proj_df[['short_name']], how='left', left_on='project_id', right_on='id')
    task_df = task_df.merge(spec['abbrev'], how='left', left_on='speciality', right_on='id')
    task_df.loc[:, 'speciality'] = task_df.abbrev

    df = task_df.loc[
        ((task_df.coord_id == u_id) & (~task_df.coord_log.str.contains('confirmed')) & (
            ~task_df.coord_log.str.contains(st.session_state.login)))
        |
        ((task_df.perf_id == u_id) & (~task_df.perf_log.str.contains('confirmed')) & (
            ~task_df.perf_log.str.contains(st.session_state.login)))
        ]

    df.rename(columns={
        'new_id': 'id',
        'short_name': 'project',
        'set_name': 'unit'
    }, inplace=True)

    return df


def home_trans():
    u_id = get_cur_u_id()
    trans_df = st.session_state.adb['trans']

    proj_df = st.session_state.adb['project']
    u_df = st.session_state.adb['users']

    trans_df = trans_df[
        (trans_df.responsible == u_id)
        & (trans_df.status != "Closed")
        & (trans_df.status != "Issued Docs")]

    trans_df = trans_df.merge(proj_df[['short_name']], how='left', left_on="project", right_on='id')
    trans_df = trans_df.merge(u_df[['login']], how='left', left_on="responsible", right_on='id')
    trans_df = trans_df.merge(u_df[['login']], how='left', left_on="responsible", right_on='id')

    return trans_df


def show_duration():
    u_df = st.session_state.adb['users']

    access_level = u_df.loc[u_df.login == st.session_state.login, 'access_level'].to_numpy()[0]

    st.sidebar.text("")
    st.sidebar.markdown(f"<h4 style='text-align: center; color: #00bbf9;'>Current Mode:</h4>",
                        unsafe_allow_html=True)
    st.sidebar.markdown(f"<h3 style='text-align: center; color: #00bbf9;'>{st.session_state.proj_scope}</h3>",
                        unsafe_allow_html=True)
    st.sidebar.markdown(f"<h5 style='text-align: center; color: #fcf403;'>You can chose another Mode in Settings -> Scope of Load</h5>",
                        unsafe_allow_html=True)

    if access_level == 'supervisor':
        with st.sidebar:
            td = datetime.datetime.now() - st.session_state.r_now
            delta = f"{td.total_seconds()}"


            st.sidebar.markdown(f"<h3 style='text-align: center; color: #00bbf9;'>{delta[:-3]} s.</h3>",
                                unsafe_allow_html=True)
    pass


def get_menus():
    menu = None
    icons = None

    performer_menu = ["Home", "Drawing Sets", "Transmittals", "Tasks", 'Scripts', 'Just for fun',
                      'Lessons Learned', 'Settings', 'Refresh Data']

    performer_icons = ['house', 'bi bi-file-earmark-spreadsheet-fill', 'bi bi-file-arrow-down',
                       'bi bi-file-check', 'bi bi-diagram-3', 'bi bi-info-circle', 'bi bi-pen', 'bi bi-gear',
                       'bi bi-arrow-clockwise']

    admin_menu = ["Manage Units"]
    admin_icons = ['bi bi-folder-plus']

    super_menu = ["Manage Projects", "Manage Users"]
    super_icons = ["bi bi-briefcase", "bi bi-person-lines-fill"]

    if not st.session_state.rights:
        st.warning('Rights not available...')

    if st.session_state.rights == "performer":
        menu = [*performer_menu]
        icons = [*performer_icons]

    if st.session_state.rights == "admin":
        menu = [*performer_menu, *admin_menu]
        icons = [*performer_icons, *admin_icons]

    if st.session_state.rights == "supervisor":
        menu = [*performer_menu, *admin_menu, *super_menu]
        icons = [*performer_icons, *admin_icons, *super_icons]

    return menu, icons


def create_states():
    if 'loads_df' not in st.session_state:
        st.session_state.loads_df = None

    if 'proj_scope' not in st.session_state:
        st.session_state.proj_scope = 'Only Current Projects'

    if 'all' not in st.session_state:
        st.session_state.all = True

    if 'r_now' not in st.session_state:
        st.session_state.r_now = datetime.datetime.now()

    if 'selected' not in st.session_state:
        st.session_state.selected = 'Home'

    if 'adb' not in st.session_state:
        st.session_state.adb = None

    if 'spec' not in st.session_state:
        st.session_state.spec = None

    if 'menu' not in st.session_state:
        st.session_state.menu = None

    if 'icons' not in st.session_state:
        st.session_state.icons = None

    if 'rights' not in st.session_state:
        st.session_state.rights = None

    if 'registered_logins' not in st.session_state:
        st.session_state.registered_logins = None

    if "preview_proj_stat" not in st.session_state:
        st.session_state.preview_proj_stat = False

    if "logged" not in st.session_state:
        st.session_state.logged = False

    if 'code_sent' not in st.session_state:
        st.session_state.code_sent = False

    if 'upd_code_sent' not in st.session_state:
        st.session_state.upd_code_sent = False

    if 'vert_menu' not in st.session_state:
        st.session_state.vert_menu = 1

    if 'login' not in st.session_state:
        st.session_state.login = None

    if 'task_preview' not in st.session_state:
        st.session_state.task_preview = False

    if 'proj_names' not in st.session_state:
        st.session_state.proj_names = None

    if 'trans_status' not in st.session_state:
        st.session_state.trans_status = None

    if 'appl_logins' not in st.session_state:
        st.session_state.appl_logins = None

    if 'disable_add_task' not in st.session_state:
        st.session_state.disable_add_task = True

    if 'conf_num' not in st.session_state:
        st.session_state.conf_num = False


def update_trans_status(trans_num):
    st.session_state.trans_status = trans_num


def form_for_trans():
    empty1, content, empty2 = st.columns([5, 3, 5])
    with content:
        with st.form('confirm_trans', clear_on_submit=True):
            st.subheader(f'Close Transmittal {st.session_state.trans_status}')
            out_num = st.text_input('Number of reply Transmittal')
            out_date = st.date_input('Date of reply Transmittal')
            status = st.radio("Transmittal Status", trans_stat)
            comment = st.text_area('Comments')
            out_note = f"{out_num} by {out_date}: {comment}"
            st.divider()
            conf_but = st.form_submit_button('Update', type='primary', use_container_width=True)

        if conf_but:
            st.session_state.trans_status = (st.session_state.trans_status, status, out_note)
            reply = trans_status_to_db()
            st.info(reply)
            st.session_state.trans_status = None
            st.experimental_rerun()

        if st.button('Escape', use_container_width=True):
            st.session_state.trans_status = None
            st.experimental_rerun()


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

    home_left, home_cont, home_right = st.columns([5, 3, 5])
    empty21, content2, empty22 = st.columns([1, 20, 1])

    with home_cont:
        st.title(':orange[Electrical Department]')

        u_df = st.session_state.adb["users"]
        u_df = u_df.loc[u_df.login == st.session_state.login]
        username = f"{u_df.name.to_numpy()[0]} {u_df.surname.to_numpy()[0]}"
        st.header(f'Welcome, {username}!')

        if st.session_state.logged:
            with content2:
                st.markdown("---")

                ass_col, blank_col, trans_col = st.columns([10, 2, 10])
                with ass_col:

                    df = home_tasks()

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
                            if st.button(label=but_key1, key=but_key1, type='primary', on_click=confirm_task,
                                         args=((row.id,))):
                                st.info(f"Task {task_id} confirmed!!")
                                st.session_state.adb['task'] = get_table(Task)
                                st.experimental_rerun()
                            st.text("")
                    else:
                        st.write('No New Tasks')

                with trans_col:
                    # df = get_my_trans(st.session_state.login)
                    df = home_trans()  # st.session_state.login

                    # st.write(df)

                    if isinstance(df, pd.DataFrame) and len(df) > 0:
                        st.subheader(":orange[New Incoming Transmittals]")
                        # df = df.loc[df.status != "Closed"]
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
                                    <td>{row.short_name}</td>
                                </tr>
                                <tr>
                                    <td>Subject</td>
                                    <td>{row.subj}</td>
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
                                    <td>{row.login_x}</td>
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
                                    <td>{row.login_y}</td>
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

                            if st.session_state.login not in row.received:
                                st.button(label=but_key1, key=but_key1, type='secondary',
                                          on_click=confirm_trans,
                                          args=((row.trans_num,)))

                            st.button(label=but_key2, key=but_key2, type='primary',
                                      on_click=update_trans_status,
                                      args=((row.trans_num,)))
                            st.session_state.adb['trans'] = get_table(Trans)
                            st.experimental_rerun()
                            st.text("")

                    else:
                        st.write('No New Transmittals')




def login_register():
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

    reg_left, log_content, reg_right = st.columns([5, 3, 5])
    with reg_left:
        st.empty()
    with reg_right:
        st.empty()

    with log_content:
        st.title(':orange[Electrical Department]')

        st.header('Welcome, Colleague!')

        st.write("The Site is designed to help you in everyday routines")
        login_tab, reg_tab = st.tabs(["Log In", 'Registration'])

        with login_tab:
            with st.form('log_in'):
                login = st.selectbox("Select Your Login", st.session_state.registered_logins,
                                     disabled=st.session_state.logged)
                st.write("Not in list? Register first 👆")
                password = st.text_input('Password', type='password', disabled=st.session_state.logged)
                login_but = st.form_submit_button('Log In', disabled=st.session_state.logged,
                                                  use_container_width=True)
                if login_but:
                    if len(password) < 3:
                        st.warning("Password should be at least 3 symbols")
                        st.stop()
                    else:
                        if check_user(login, password):
                            st.session_state.logged = True
                            st.session_state.login = login
                            u_df = st.session_state.adb['users']
                            st.session_state.rights = u_df.loc[
                                u_df.login == login, 'access_level'].to_numpy()[0]
                            reply = add_to_log(login)

                            if 'ERROR' in reply.upper():
                                st.write(f"""Please sent error below to sergey.priemshiy@uzliti-en.com
                                            or by telegram +998909598030:
                                            {reply}""")
                                st.stop()
                            else:
                                st.info('Logged In')
                                st.experimental_rerun()

                        else:
                            st.session_state.logged = False
                            st.warning('Wrong Password')
                            st.session_state.rights = None
                            st.session_state.login = None

        with reg_tab:
            appl_logins = st.session_state.appl_logins

            if isinstance(appl_logins, list):
                login = st.selectbox("Select Your Login", appl_logins,
                                     disabled=st.session_state.logged, key='reg_email')
            else:
                st.warning(appl_logins)
                st.stop()

            if login in st.session_state.registered_logins:
                st.subheader("You are Registered 😎")
            else:
                st.write("Not in list? Send the request from your e-mail to sergey.priemshiy@uzliti-en.com")

            with st.form("Reg_form"):
                name = st.text_input('Your Name', disabled=st.session_state.logged)
                surname = st.text_input('Your Surname', disabled=st.session_state.logged)
                phone = st.text_input('Your personal Phone', disabled=st.session_state.logged) \
                    .replace(" ", "").replace("-", "")
                telegram = st.text_input('Your personal Telegram', disabled=st.session_state.logged)
                reg_pass_1 = st.text_input('Password', type='password', key='reg_pass_1',
                                           disabled=st.session_state.logged)
                reg_pass_2 = st.text_input('Repeat Password', type='password', key='reg_pass_2',
                                           disabled=st.session_state.logged)

                get_reg_code = st.form_submit_button('Get Confirmation Code', use_container_width=True)

            # conf_html = ""
            if get_reg_code:
                if login in st.session_state.registered_logins:
                    st.warning(f'User {login} is already in DataBase')
                    st.stop()

                if len(reg_pass_2) < 3 or reg_pass_1 != reg_pass_2:
                    st.warning("""- Password should be at least 3 symbols
                        - Password and Repeat Password should be the same""")
                    st.stop()
                if len(name) < 2 or len(surname) < 2:
                    st.warning("! Too short Name or Surname")
                    st.stop()

                if len(phone) > 13:
                    st.warning("Phone number should be 13 symbols length")
                    st.stop()

                if len(telegram) > 80:
                    st.warning("Telegram length should less than 80 symbols")
                    st.stop()

                st.session_state.conf_num = "".join(random.sample("123456789", 4))  # create confirmation code

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
                                at the <a href="https://e-design.streamlit.app/">site</a> registration form
                                <hr>
                                Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """

                if not st.session_state.code_sent:
                    # user = get_user_data(login)

                    u_df = st.session_state.adb['users']
                    user = u_df.loc[u_df.login == login]

                    if "@" not in user.email.to_numpy()[0]:
                        st.warning("Can't get User's email")
                        st.stop()

                    reply = send_mail(receiver=user.email.to_numpy()[0], cc_rec="sergey.priemshiy@uzliti-en.com",
                                      html=conf_html, subj="Confirmation of ETD site registration")

                    if reply == 200:
                        st.session_state.code_sent = True
                        st.info("Confirmation Code sent to Your Company Email")
                    else:
                        st.warning("Network problems...Try again later")

            entered_code = st.text_input("Confirmation Code from Email").replace(" ", '')

            if st.button("Register", use_container_width=True):
                if login in st.session_state.registered_logins:
                    st.warning(f'User {login} is already Registered')
                    st.stop()

                if st.session_state.conf_num != entered_code:
                    st.warning("Confirmation code is wrong, try again")
                    st.stop()
                else:
                    reply = register_user(name, surname, phone, telegram, login, reg_pass_2)
                    if 'ERROR' in reply.upper():
                        st.write('Error')
                    else:
                        st.warning(reply)
                st.session_state.conf_num = None
                st.session_state.code_sent = None
                st.session_state.adb = get_all()
                st.experimental_rerun()


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
                script_acc_chb_init = st.checkbox('Access to Scripts', key="acc_to_scr", value=0)
                user_start_date = st.date_input('Start Date', datetime.date.today())
                create_appl_user_but = st.form_submit_button('Create New User', use_container_width=True)

            if create_appl_user_but:
                script_acc_init = 1 if script_acc_chb_init else 0
                reply = create_appl_user(
                    user_email, user_position, user_department, user_access_level, "current",
                    user_start_date, script_acc_init)
                st.info(reply)
                st.session_state.adb['users'] = get_table(Users)

        with users_tab2:

            u_df = st.session_state.adb['users']

            list_appl_users = u_df.login.tolist()

            employee_to_edit = st.selectbox('Select User', list_appl_users)
            edit_move = st.radio('Action', ('Edit', 'Move to Former Users'), horizontal=True)

            if edit_move == 'Edit':
                with st.form('upd_exist_user'):

                    u_df = st.session_state.adb['users']

                    appl_user = u_df.loc[u_df.login == employee_to_edit]

                    position = st.radio('Position', positions,
                                        key='edit_position', horizontal=True,
                                        index=get_list_index(positions, appl_user.position.to_numpy()[0]))
                    st.markdown("---")

                    department = st.radio('Department', departments,
                                          key='edit_department', horizontal=True,
                                          index=get_list_index(departments, appl_user.branch.to_numpy()[0]))
                    st.markdown("---")

                    access_tuple = ('performer', 'admin', 'supervisor', 'prohibited')

                    access_level = st.radio('Access level', access_tuple, horizontal=True,
                                            key='edit_access_level',
                                            index=get_list_index(access_tuple, appl_user.access_level.to_numpy()[0]))
                    st.markdown("---")

                    script_acc_chb = st.checkbox('Access to Scripts', value=appl_user.script_acc.to_numpy()[0])
                    st.markdown("---")

                    try:
                        date_from_db = appl_user.start_date.to_numpy()[0]
                    except:
                        date_from_db = datetime.date.today()

                    start_date = st.date_input('Start Date', date_from_db, key='start_date')

                    upd_user_but = st.form_submit_button("Update in DB", use_container_width=True)

                if upd_user_but:
                    script_acc = 1 if script_acc_chb else 0

                    reply = update_users_in_db(employee_to_edit, position, department,
                                               start_date, access_level, script_acc)
                    st.info(reply)
                    st.session_state.adb['users'] = get_table(Users)

            if edit_move == 'Move to Former Users':
                end_date = st.date_input('End Date', key='end_date')

                if st.button('Confirm', type='primary', use_container_width=True):
                    reply = move_to_former(employee_to_edit, end_date)
                    st.info(reply)
                    st.session_state.adb['users'] = get_table(Users)


def fresh_data():
    st.session_state.adb = get_all()

    plaho = st.empty()

    with plaho.container():
        st.header("")
        st.header("")
        st.header("")
        st.markdown("<h1 style='text-align: center; color: #00bbf9;'>Data is Fresh</h1>", unsafe_allow_html=True)

    time.sleep(1)
    plaho.empty()


def home():
    if st.session_state.trans_status:
        form_for_trans()
    else:
        home_content()


def win_selector(selected):
    st.session_state.r_now = datetime.datetime.now()

    if selected != "Refresh Data":
        st.session_state.selected = selected

    tab_dict = {
        "Home": home,
        "Manage Projects": manage_projects,
        "Transmittals": transmittals_content,
        "Tasks": tasks_content,
        "Drawing Sets": drawing_sets,
        "Just for fun": just_for_fun,
        "Scripts": xl_to_sld,
        "Manage Users": manage_users,
        "Lessons Learned": lessons_content,
        "Settings": settings_content,
        "Refresh Data": fresh_data,
        "Manage Units": manage_units,
    }

    tab_dict.get(selected)()

    show_duration()


def show_states():
    st.text('appl_logins')
    st.write(st.session_state.appl_logins)
    st.text('-----------------------')
    st.text('adb')
    st.write(st.session_state.adb)
    st.text('-----------------------')
    st.write('menu')
    st.write(st.session_state.menu)
    st.text('-----------------------')
    st.write('icons')
    st.write(st.session_state.icons)
    st.text('-----------------------')
    st.write('rights')
    st.write(st.session_state.rights)
    st.text('-----------------------')
    st.write('registered_logins')
    st.write(st.session_state.registered_logins)
    st.text('-----------------------')
    st.write("preview_proj_stat")
    st.write(st.session_state.preview_proj_stat)
    st.text('-----------------------')
    st.write("logged")
    st.write(st.session_state.logged)
    st.text('-----------------------')
    st.write('code_sent')
    st.write(st.session_state.code_sent)
    st.text('-----------------------')
    st.write('upd_code_sent')
    st.write(st.session_state.upd_code_sent)
    st.text('-----------------------')
    st.write('vert_menu')
    st.write(st.session_state.vert_menu)
    st.text('-----------------------')
    st.write('user')
    st.write(st.session_state['user'])
    st.text('-----------------------')
    st.write('task_preview')
    st.write(st.session_state.task_preview)
    st.text('-----------------------')
    st.write('proj_names')
    st.write(st.session_state.proj_names)
    st.text('-----------------------')
    st.write('trans_status')
    st.write(st.session_state.trans_status)
    st.text('-----------------------')
    st.write('spec')
    st.write(st.session_state.spec)
    st.text('-----------------------')


def prepare_menus():
    st.session_state.menu = get_menus()[0]

    st.session_state.icons = get_menus()[1]

    if st.session_state.vert_menu == 1:
        with st.sidebar:
            image = Image.open("images/big_logo.jpg")
            st.image(image, use_column_width=True)
            selected = option_menu("ET Department",
                                   options=st.session_state.menu,
                                   default_index=0,
                                   icons=st.session_state.icons,
                                   menu_icon="bi bi-plug")

            if st.session_state.rights == 'supervisor' and st.checkbox("Show states"):
                show_states()
    else:
        selected = option_menu(None,
                               options=st.session_state.menu,
                               default_index=0,
                               icons=st.session_state.icons,
                               menu_icon=None,
                               orientation='horizontal')

    return selected


def initial():
    create_states()
    appearance_settings()

    u_df = None

    if not st.session_state.adb:
        st.session_state.adb = get_all()

    if not isinstance(st.session_state.adb, dict):
        st.warning(st.session_state.adb)
        st.stop()

    try:
        u_df = st.session_state.adb['users']
        if not isinstance(u_df, pd.DataFrame) or len(u_df) == 0:
            st.warning("Can't get Users")
            st.stop()
    except Exception as e:
        st.warning(err_handler(e))
        st.stop()

    try:
        st.session_state.registered_logins = u_df.loc[(u_df.status == 'current') &
                                                      u_df.hashed_pass, 'login'].tolist()

        st.session_state.appl_logins = u_df.loc[u_df.status == 'current', 'login'].tolist()

        if len(st.session_state.registered_logins) == 0:
            st.warning("Can't get Registered Users")
            st.stop()
    except Exception as e:
        st.warning(err_handler(e))
        st.stop()

    try:
        st.session_state.proj_names = st.session_state.adb['project'].short_name.tolist()
        if len(st.session_state.proj_names) == 0:
            st.warning("Can't get Project List")
    except Exception as e:
        st.warning(err_handler(e))

    try:
        st.session_state.spec = st.session_state.adb['speciality'].abbrev.tolist()
        if len(st.session_state.spec) == 0:
            st.warning("Can't get Specialities")
    except Exception as e:
        st.warning(err_handler(e))

    if not st.session_state.logged:
        login_register()

    if st.session_state.logged and st.session_state.login:
        try:
            st.session_state.vert_menu = int(u_df.loc[u_df.login == st.session_state.login, 'vert_menu'].to_numpy()[0])
        except Exception as e:
            st.session_state.vert_menu = 1

            st.sidebar.warning('Something wrong with menu settings')
            st.sidebar.warning(err_handler(e))

        win_selector(prepare_menus())


if __name__ == "__main__":
    initial()
