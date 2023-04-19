# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from PIL import Image
import datetime
import random
from streamlit_option_menu import option_menu
from admin_tools import manage_projects, get_list_index
from tasks_tab import tasks_content
from drawing_sets_tab import drawing_sets, create_new_unit
from just_for_fun_tab import just_for_fun, emoji_content
from lesson_learned_tab import lessons_content
from pre_sets import appearance_settings, reporter, positions, departments, mail_to_name, trans_stat, stages, \
    sod_statuses
from send_emails import send_mail
from settings_tab import settings_content
from transmittals_tab import transmittals_content
from users import check_user, add_to_log, create_appl_user, update_users_in_db, move_to_former, register_user, \
    err_handler
from projects import confirm_task, get_my_trans, confirm_trans, get_pers_tasks, trans_status_to_db, add_sod, \
    get_all, get_table
from models import Task

st.set_page_config(layout="wide", page_icon=Image.open("images/small_logo.jpg"),
                   page_title='ET Department', initial_sidebar_state='auto')


def get_menus():
    menu = None
    icons = None

    performer_menu = ["Home", "Drawing Sets", "Transmittals", "Tasks", 'EtapPy', 'Just for fun',
                      'Lessons Learned', 'Settings']

    performer_icons = ['house', 'bi bi-file-earmark-spreadsheet-fill', 'bi bi-file-arrow-down',
                       'bi bi-file-check', 'bi bi-diagram-3', 'bi bi-info-circle', 'bi bi-pen', 'bi bi-gear',
                       ]

    admin_menu = ["Create new Set / Unit"]
    admin_icons = ['bi bi-bar-chart-steps']

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
        # reg_logins = get_logins_for_registered()

    if 'delay' not in st.session_state:
        st.session_state.delay = 2

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

    if 'user' not in st.session_state:
        st.session_state['user'] = None

    if 'task_preview' not in st.session_state:
        st.session_state.task_preview = False

    if 'proj_names' not in st.session_state:
        st.session_state.proj_names = None

    if 'trans_status' not in st.session_state:
        st.session_state.trans_status = None

    if 'appl_logins' not in st.session_state:
        st.session_state.appl_logins = None

    if 'edit_sod' not in st.session_state:
        st.session_state.edit_sod = {
            'coordinator': None,
            'performer': None,
            'revision': None,
            'status': None,
            'notes': None,
            'project': None,
            'unit': None,
            'unit_id': None,
            'my_all': None,
            'state': False
        }


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
            reporter(reply, 2)
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
        u_df = u_df.loc[u_df.login == st.session_state.user]
        username = f"{u_df.name.values[0]} {u_df.surname.values[0]}"
        st.header(f'Welcome, {username}!')

        if st.session_state.logged:
            with content2:
                st.markdown("---")

                ass_col, blank_col, trans_col = st.columns([10, 2, 10])
                with ass_col:
                    # df = get_pers_tasks()

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
                            if st.button(label=but_key1, key=but_key1, type='primary', on_click=confirm_task,
                                         args=(
                                                 (row.id,))):
                                st.info(f"Task {task_id} confirmed!!")
                            st.text("")
                    else:
                        st.text('No New Tasks')

                with trans_col:
                    df = get_my_trans(st.session_state.user)  # st.session_state.user
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
                                          args=((row.trans_num,)))

                            st.button(label=but_key2, key=but_key2, type='primary',
                                      on_click=update_trans_status,
                                      args=((row.trans_num,)))
                            st.text("")
                    else:
                        st.text('No New Transmittals')


def etap_py():
    from datetime import datetime

    adb = st.session_state.adb
    phone_1, phone_content, phone_2 = st.columns([1, 9, 1])
    with phone_1:
        st.empty()
    with phone_2:
        st.empty()
    with phone_content:
        st.title(':orange[Create SLD from Load List]')

        if st.button('Show Projects'):
            st.write(adb['project'])

        if st.button('Show Units'):
            st.write(adb['sod'])

        if st.button('Show Tasks'):
            start_time = datetime.now()
            st.write(adb['task'])
            st.text((datetime.now() - start_time))

        if st.button('Show Transmittals'):
            start_time = datetime.now()
            st.write(adb['trans'])
            st.text((datetime.now() - start_time))

        if st.button('Show Users'):
            st.write(adb['users'])

        if st.button("Tasks from DB"):
            start_time = datetime.now()
            tr_df = get_table(Task)
            st.write(tr_df)
            st.text((datetime.now() - start_time))


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
                        reporter("Password should be at least 3 symbols")
                        st.stop()
                    else:
                        if check_user(login, password):
                            st.session_state.logged = True
                            st.session_state.user = login
                            users_df = st.session_state.adb['users']
                            st.session_state.rights = users_df.loc[
                                users_df.login == login, 'access_level'].values[0]
                            reply = add_to_log(login)

                            if 'ERROR' in reply.upper():
                                st.write(f"""Please sent error below to sergey.priemshiy@uzliti-en.com
                                            or by telegram +998909598030:
                                            {reply}""")
                                st.stop()
                            else:
                                reporter('Logged In', 1)
                                st.experimental_rerun()

                        else:
                            st.session_state.logged = False
                            st.warning('Wrong Password')
                            st.session_state.rights = None
                            st.session_state.user = None

        with reg_tab:
            appl_logins = st.session_state.appl_logins

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
                surname = st.text_input('Your Surname', disabled=st.session_state.logged)
                phone = st.text_input('Your personal Phone', disabled=st.session_state.logged)
                telegram = st.text_input('Your personal Telegram', disabled=st.session_state.logged)
                reg_pass_1 = st.text_input('Password', type='password', key='reg_pass_1',
                                           disabled=st.session_state.logged)
                reg_pass_2 = st.text_input('Repeat Password', type='password', key='reg_pass_2',
                                           disabled=st.session_state.logged)

                # data_chb = st.checkbox('Data is Correct', disabled=st.session_state.logged)

                get_reg_code = st.form_submit_button('Get Confirmation Code', use_container_width=True)

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
                    # user = get_user_data(login)

                    user_df = st.session_state.adb['user']
                    user = user_df.loc[users_df.login == login]

                    # if "@" not in user.email:
                    if "@" not in user.email.values[0]:
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
                st.experimental_rerun()

        with users_tab2:

            # list_appl_users = get_all_emails()

            users_df = st.session_state.adb['users']

            list_appl_users = users_df.login.tolist()

            employee_to_edit = st.selectbox('Select User', list_appl_users)
            edit_move = st.radio('Action', ('Edit', 'Move to Former Users'), horizontal=True)

            if edit_move == 'Edit':
                with st.form('upd_exist_user'):

                    # appl_user = get_user_data(employee_to_edit)

                    users_df = st.session_state.adb['users']

                    appl_user = users_df.loc[users_df.login == employee_to_edit]

                    position = st.radio('Position', positions,
                                        key='edit_position', horizontal=True,
                                        index=get_list_index(positions, appl_user.position.values[0]))
                    st.markdown("---")
                    # try:
                    #     department_ind = departments.index(appl_user.department)
                    # except:
                    #     department_ind = 0

                    department = st.radio('Department', departments,
                                          key='edit_department', horizontal=True,
                                          index=get_list_index(departments, appl_user.branch.values[0]))
                    st.markdown("---")

                    access_tuple = ('performer', 'admin', 'supervisor', 'prohibited')
                    # try:
                    #     access_ind = access_tuple.index(appl_user.access_level)
                    # except Exception:
                    #     access_ind = 0

                    access_level = st.radio('Access level', access_tuple, horizontal=True,
                                            key='edit_access_level',
                                            index=get_list_index(access_tuple, appl_user.access_level.values[0]))
                    st.markdown("---")

                    try:
                        date_from_db = appl_user.start_date.values[0]
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


def win_selector(selected):
    if selected == "Home":
        if st.session_state.trans_status:
            form_for_trans()
        else:
            home_content()

    if selected == "Manage Projects":
        manage_projects()

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

    if selected == "Create new Set / Unit":
        create_new_unit()


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
    st.write('delay')
    st.write(st.session_state.delay)
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
    st.write('edit_sod')
    st.write(st.session_state.edit_sod)
    st.text('-----------------------')
    st.write('spec')
    st.write(st.session_state.spec)
    st.text('-----------------------')


def prepare_menus(u_df):
    st.session_state.menu = get_menus()[0]

    st.session_state.icons = get_menus()[1]

    st.session_state.vert_menu = u_df.loc[u_df.login == st.session_state.user, 'vert_menu'].values[0]
    st.session_state.delay = u_df.loc[u_df.login == st.session_state.user, 'delay_set'].values[0]

    if st.session_state.vert_menu == 1:
        with st.sidebar:
            image = Image.open("images/big_logo.jpg")
            st.image(image, use_column_width=True)
            selected = option_menu("ET Department", st.session_state.menu, icons=st.session_state.icons,
                                   menu_icon="bi bi-plug", default_index=0)

            if st.session_state.rights == 'supervisor' and st.checkbox("Show states"):
                show_states()
    else:
        selected = option_menu(None, st.session_state.menu, icons=st.session_state.icons,
                               menu_icon=None, default_index=0, orientation='horizontal')
    return selected


def initial():
    create_states()
    appearance_settings()

    st.session_state.adb = get_all()

    users_df = None

    if not isinstance(st.session_state.adb, dict):
        st.warning(st.session_state.adb)
        st.stop()

    try:
        users_df = st.session_state.adb['users']
        if not isinstance(users_df, pd.DataFrame) or len(users_df) == 0:
            st.warning("Can't get Users")
            st.stop()
    except Exception as e:
        st.warning(err_handler(e))
        st.stop()

    try:
        st.session_state.registered_logins = users_df.loc[(users_df.status == 'current') &
                                                          users_df.hashed_pass, 'login'].tolist()

        st.session_state.appl_logins = users_df.loc[users_df.status == 'current', 'login'].tolist()

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

    if st.session_state.logged and st.session_state.user:

        selected = prepare_menus(users_df)
        win_selector(selected)


if __name__ == "__main__":
    initial()
