# -*- coding: utf-8 -*-
import datetime
import streamlit as st
import bcrypt
from models import Users, VisitLog
from pony.orm import *

from pre_sets import mail_to_name

set_sql_debug(True)


# def ben(func):
#   def wrapper(*args):
#     start = time.time()
#     func(*args)
#     end = time.time()
#     print(f'Time spent: {round(end - start, 4)} s.')
#   return wrapper

def move_to_former(u_name, end_date):
    with db_session:
        try:
            hero = Users[u_name]
            hero.access_level = 'prohibited'
            hero.status = 'former'
            hero.end_date = end_date
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return f'''**{u_name}** moved to Former Users
        by date **{end_date}**.
        Access status: **:red[{hero.access_level}]**'''


@st.cache_data(ttl=600)
def get_all_names():
    with db_session:
        try:
            return select(e.id for e in Users)[:]
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def create_appl_user(email, position, branch, access_level, status, start_date):
    if '@' not in email or len(email) < 12:
        return f'Wrong e-mail {email}'
    u_name, u_tail = email.split("@")
    if u_name in get_all_names():
        return f'User with name {u_name} already exist in DataBase'
    with db_session:
        try:
            Users(id=u_name, tail=u_tail, position=position, branch=branch, access_level=access_level, status=status,
                  start_date=start_date)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
    return f"User {email} is added to Applied Users"


# @ben
# def get_appl_emails():
#     """
#     emails available for registration
#     :return: list of emails
#     """
#     with db_session:
#         try:
#             # appl_emails = select(u.id for u in ApplUser)[:]  ###
#             appl_emails = select(eml.id for eml in Users if len(eml.hashed_pass) == 0)[:]  ###
#             return appl_emails
#         except Exception as e:
#             return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_appl_names():
    """
    u_names available for registration
    :return: list of u_names
    """
    with db_session:
        try:
            appl_names = select(eml.id for eml in Users if len(eml.hashed_pass) == 0)[:]  ###
            return appl_names
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


# @st.cache_data(ttl=1800)
# def get_registered_emails():
#     with db_session:
#         try:
#             registered_emails = select(
#                 eml.id for eml in Users
#                 if len(eml.hashed_pass) > 0 and eml.status == 'current')[:]
#
#             return list(registered_emails)
#         except Exception as e:
#             return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_registered_names():
    with db_session:
        try:
            registered_names = select(
                eml.id for eml in Users
                if len(eml.hashed_pass) > 0 and eml.status == 'current')[:]

            # registered_names = [e.split("@")[0] for e in registered_emails]

            return registered_names
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


# def get_allowed_emails():
#     with db_session:
#         try:
#             registered_emails = select(
#                 eml.id for eml in Users
#                 if eml.status == 'current')[:]
#
#             return list(registered_emails)
#         except Exception as e:
#             return f"{type(e).__name__}{getattr(e, 'args', None)}"
#

def get_allowed_names():
    with db_session:
        try:
            allowed_names = select(
                u.id for u in Users
                if u.status == 'current')[:]

            return allowed_names
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def create_user(name, surname, phone, telegram, email, password):
    u_name, u_tail = email.split("@")
    if u_name in get_appl_names():
        if u_name in get_registered_names():
            return f"User with email {u_name} already registered!"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
        hashed_password = hashed_password.decode('utf-8')
        with db_session:
            try:
                new_user = Users(
                    id=u_name,
                    tail=u_tail,
                    name=name,
                    surname=surname,
                    phone=phone,
                    telegram=telegram,
                    hashed_pass=hashed_password,
                    vert_menu=1,
                    delay_set=1,
                )
            except Exception as e:
                return f"{type(e).__name__}{getattr(e, 'args', None)}"
        return f"New User {new_user.name} {new_user.surname} Registered Successfully"
    else:
        return "Failed to create. Ask admin to add you to DataBase"


def register_user(name, surname, phone, telegram, u_name, password):
    if u_name in get_registered_names():
        return f"User with email {u_name} already registered!"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
    hashed_password = hashed_password.decode('utf-8')
    with db_session:
        try:
            user_to_reg = Users[u_name]
            user_to_reg.name = name
            user_to_reg.surname = surname
            user_to_reg.phone = phone
            user_to_reg.telegram = telegram
            user_to_reg.hashed_pass = hashed_password
            user_to_reg.vert_menu = 1
            user_to_reg.delay_set = 1
            return f"New User {user_to_reg.name} {user_to_reg.surname} Registered Successfully"
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def check_user(u_name, password):
    try:
        with db_session:
            hero = Users[u_name]
            hashed_password = hero.hashed_pass
            hashed_password = hashed_password.encode('utf-8')
            valid_pass = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            return valid_pass
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_user_data(u_name):
    try:
        with db_session:
            return Users[u_name]
    except Exception as e:
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


def add_to_log(u_name):
    with db_session:
        try:
            logger = VisitLog(login_time=datetime.datetime.now(), users=u_name)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
    return f"Hello, {mail_to_name(logger.users.id)}. Do your best and forget the rest 😎"


def update_user_data(employee_to_edit, user_tab):
    with user_tab:
        st.write(employee_to_edit)
        with st.form('Edit Users Data', clear_on_submit=False):
            position = st.radio('Position', ('Senior', 'Lead', 'I cat.', 'II cat.', 'III cat.', 'Trainee'),
                                horizontal=True)

            department = st.radio('Department', ('UzLITI Engineering', 'En-Solut', 'En-Concept', 'En-Smart', 'Remote'),
                                  horizontal=True)

            access_level = st.radio('Access level',
                                    ('performer', 'admin', 'superuser', 'former'), horizontal=True)

            start_date = st.date_input('Start Date', key='start_date')
            end_date = st.date_input('End Date', key='end_date')

            st.form_submit_button("Update2", key="update_user_button",
                                  on_click=update_users_in_db,
                                  args=(employee_to_edit, position, department, start_date, end_date, access_level))


def update_users_in_db(u_name, position, branch, start_date, access_level):
    with db_session:
        try:
            hero = Users[u_name]
            hero.position = position
            hero.branch = branch
            hero.start_date = start_date
            hero.access_level = access_level
            hero.status = 'current'
            hero.end_date = None
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return f"""Updated Data for Users with e-mail **{u_name}**  
                   Position: **:blue[{position}]**  
                   Branch: **:blue[{branch}]**  
                   Access level: **:blue[{access_level}]**  
                   Status: **:blue[{hero.status}]**"""


def get_logged_rights(u_name):
    with db_session:
        try:
            hero = Users[u_name]
            return hero.access_level
        except Exception as e:
            # return "🔧 Connection to DB is failed"
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_settings(u_name):
    with db_session:
        try:
            u = Users[u_name]
            return u.vert_menu, u.delay_set
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def update_settings(u_name, menu, delay):
    with db_session:
        try:
            hero = Users[u_name]
            hero.vert_menu = menu
            hero.delay_set = delay
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
        return "Settings Updated"


def update_user_reg_data(u_name, upd_pass_2):
    with db_session:
        try:
            hero = Users[u_name]
            ha_pa = bcrypt.hashpw(upd_pass_2.encode('utf-8'), bcrypt.gensalt(10))
            ha_pa = ha_pa.decode('utf-8')
            hero.hashed_pass = ha_pa
            return f"Data for {hero.name} is Updated"
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


