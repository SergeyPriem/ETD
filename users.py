# -*- coding: utf-8 -*-
import datetime
import time
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

def move_to_former(employee_to_edit, end_date):
    with db_session:
        try:
            hero = Users[employee_to_edit]
            hero.access_level = 'prohibited'
            hero.status = 'former'
            hero.end_date = end_date
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return f'''**{hero.email}** moved to Former Users
        by date **{end_date}**.
        Access status: **:red[{hero.access_level}]**'''


@st.cache_data(ttl=600)
def get_all_emails():
    with db_session:
        try:
            return select(e.id for e in Users)[:]
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def create_appl_user(email, position, branch, access_level, status, start_date):
    if '@' not in email or len(email) < 12:
        return f'Wrong e-mail {email}'
    if email in get_all_emails():
        return f'User with email {email} already exist in DataBase'
    with db_session:
        try:
            Users(id=email, position=position, branch=branch, access_level=access_level, status=status,
                  start_date=start_date)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
    return f"User {email} is added to Applied Users"


# @ben
def get_appl_emails():
    """
    emails available for registration
    :return: list of emails
    """
    with db_session:
        try:
            # appl_emails = select(u.id for u in ApplUser)[:]  ###
            appl_emails = select(eml.id for eml in Users if len(eml.hashed_pass) == 0)[:]  ###
            return appl_emails
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


@st.cache_data(ttl=1800)
def get_registered_emails():
    with db_session:
        try:
            registered_emails = select(
                eml.id for eml in Users
                if len(eml.hashed_pass) > 0 and eml.status == 'current')[:]

            return list(registered_emails)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

def get_allowed_emails():
    with db_session:
        try:
            registered_emails = select(
                eml.id for eml in Users
                if eml.status == 'current')[:]

            return list(registered_emails)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def create_user(name, surname, phone, telegram, email, password):
    if email in get_appl_emails():
        if email in get_registered_emails():
            return f"User with email {email} already registered!"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
        hashed_password = hashed_password.decode('utf-8')
        with db_session:
            try:
                new_user = Users(
                    id=email,
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


def check_user(email, password):
    try:
        with db_session:
            hero = Users[email]
            hashed_password = hero.hashed_pass
            hashed_password = hashed_password.encode('utf-8')
            valid_pass = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            return valid_pass
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_user_data(email):
    try:
        with db_session:
            return Users[email]
    except Exception as e:
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


def add_to_log(email):
    with db_session:
        try:
            logger = VisitLog(login_time=datetime.datetime.now(), users=email)
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


def update_users_in_db(email, position, department, start_date, access_level):
    with db_session:
        try:
            hero = Users[email]
            hero.position = position
            hero.branch = department
            hero.start_date = start_date
            hero.access_level = access_level
            hero.status = 'current'
            hero.end_date = None
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return f"""Updated Data for Users with e-mail **{hero.email}**  
                   Position: **:blue[{hero.position}]**  
                   Branch: **:blue[{hero.branch}]**  
                   Access level: **:blue[{hero.access_level}]**  
                   Status: **:blue[{hero.status}]**"""


def get_logged_rights(email):
    with db_session:
        try:
            hero = Users[email]
            return hero.access_level
        except Exception as e:
            # return "🔧 Connection to DB is failed"
            return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_settings(email):
    with db_session:
        try:
            u = Users[email]
            # u_set = select((u.vert_menu, u.delay_set) for u in Users if u.id == email).first()
            # return u_set
            return u.vert_menu, u.delay_set
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def update_settings(email, menu, delay):
    with db_session:
        try:
            hero = Users[email]
            hero.vert_menu = menu
            hero.delay_set = delay
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
        return "Settings Updated"


def update_user_reg_data(email, upd_pass_2):
    with db_session:
        try:
            hero = Users[email]
            ha_pa = bcrypt.hashpw(upd_pass_2.encode('utf-8'), bcrypt.gensalt(10))
            ha_pa = ha_pa.decode('utf-8')
            hero.hashed_pass = ha_pa
            return f"Data for {hero.name} is Updated"
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
