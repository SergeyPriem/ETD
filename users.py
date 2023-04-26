# -*- coding: utf-8 -*-
import datetime
import streamlit as st
import bcrypt
from models import Users, VisitLog
from pony.orm import *

from pre_sets import mail_to_name

set_sql_debug(False)


def err_handler(e):
    return f"{type(e).__name__}{getattr(e, 'args', None)}"


def move_to_former(email, end_date):
    with db_session:
        try:
            hero = Users[email]
            hero.access_level = 'prohibited'
            hero.status = 'former'
            hero.end_date = end_date
        except Exception as e:
            return err_handler(e)

        return f'''**{email}** moved to Former Users
        by date **{end_date}**.
        Access status: **:red[{hero.access_level}]**'''


### GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET GET #################
def get_all_emails():
    with db_session:
        try:
            return select(e.email for e in Users)[:]
        except Exception as e:
            return err_handler(e)


def get_all_logins():
    with db_session:
        try:
            return list(select(u.login for u in Users))
        except Exception as e:
            return err_handler(e)


def get_appl_logins():
    """
    logins available for registration
    :return: list of logins
    """
    with db_session:
        try:
            # appl_emails = select(u.id for u in ApplUser)[:]  ###
            appl_logins = select(
                u.login for u in Users
                if len(u.hashed_pass) == 0)[:]  ###
            return list(appl_logins)
        except Exception as e:
            return err_handler(e)


def get_logins_for_registered():
    with db_session:
        try:
            exist_logins = select(
                u.login for u in Users
                if len(u.hashed_pass) > 0 and u.status == 'current')[:]
            return list(exist_logins)
        except Exception as e:
            return err_handler(e)


def get_logins_for_current():
    with db_session:
        try:
            registered_logins = select(
                eml.login for eml in Users
                if eml.status == 'current')[:]

            return list(registered_logins)
        except Exception as e:
            return err_handler(e)


# def create_user(name, surname, phone, telegram, email, password):
#     if email in get_appl_emails():
#         if email in get_registered_emails():
#             return f"User with email {email} already registered!"
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
#         hashed_password = hashed_password.decode('utf-8')
#         with db_session:
#             try:
#                 new_user = Users(
#                     id=email,
#                     name=name,
#                     surname=surname,
#                     phone=phone,
#                     telegram=telegram,
#                     hashed_pass=hashed_password,
#                     vert_menu=1,
#                     delay_set=1,
#                 )
#             except Exception as e:
#                 return err_handler(e)
#         return f"New User {new_user.name} {new_user.surname} Registered Successfully"
#     else:
#         return "Failed to create. Ask admin to add you to DataBase"

def get_user_data(login):
    try:
        with db_session:
            return Users.get(login=login)
    except Exception as e:
        return err_handler(e)


def get_logged_rights(login):
    with db_session:
        try:
            hero = Users.get(login=login)
            return hero.access_level
        except Exception as e:
            # return "🔧 Connection to DB is failed"
            return err_handler(e)


def get_settings(login):
    with db_session:
        try:
            u = Users.get(login=login)
            # u_set = select((u.vert_menu, u.delay_set) for u in Users if u.id == email).first()
            # return u_set
            return u.vert_menu, u.delay_set
        except Exception as e:
            return err_handler(e)


##### CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE CREATE #################
def create_appl_user(email, position, branch, access_level, status, start_date):
    if '@' not in email or len(email) < 12:
        return f'Wrong e-mail {email}'
    if email in get_all_emails():
        return f'User with email {email} already exist in DataBase'
    with db_session:
        try:
            Users(email=email, login=email.split("@")[0], position=position, branch=branch,
                  access_level=access_level, status=status, start_date=start_date)
            return f"User {email} is added to Applied Users"
        except Exception as e:
            return err_handler(e)


def register_user(name, surname, phone, telegram, login, password):
    if login in st.session_state.registered_logins:
        return f"User with email {login} already registered!"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
    hashed_password = hashed_password.decode('utf-8')
    with db_session:
        try:
            user_to_reg = Users.get(login=login)  # Users[login]
            user_to_reg.name = name
            user_to_reg.surname = surname
            user_to_reg.phone = phone
            user_to_reg.telegram = telegram
            user_to_reg.hashed_pass = hashed_password
            user_to_reg.vert_menu = 1
            user_to_reg.delay_set = 1
            return f"New User {user_to_reg.name} {user_to_reg.surname} Registered Successfully"
        except Exception as e:
            return err_handler(e)


def check_user(login, password):
    try:
        with db_session:
            hero = Users.get(login=login)
            hashed_password = hero.hashed_pass
            hashed_password = hashed_password.encode('utf-8')
            valid_pass = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            return valid_pass
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return err_handler(e)


def add_to_log(login):
    with db_session:
        try:
            logger = VisitLog(login_time=datetime.datetime.now(), users=Users.get(login=login))
        except Exception as e:
            return err_handler(e)
    return f"Hello, {mail_to_name(logger.users.id)}. Do your best and forget the rest 😎"


#### UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE UPDATE ###############
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


def update_users_in_db(login, position, branch, start_date, access_level):
    with db_session:
        try:
            hero = Users.get(login=login)
            hero.position = position
            hero.branch = branch
            hero.start_date = start_date
            hero.access_level = access_level
            hero.status = 'current'
            hero.end_date = None
            return f"""Updated Data for Users with Login **{login}**  
                       Position: **:blue[{position}]**  
                       Branch: **:blue[{branch}]**  
                       Access level: **:blue[{access_level}]**  
                       Status: **:blue[{hero.status}]**"""

        except Exception as e:
            return err_handler(e)



def update_settings(login, menu):
    with db_session:
        try:
            hero = Users.get(login=login)
            hero.vert_menu = menu
            # hero.delay_set = delay
        except Exception as e:
            return err_handler(e)
        return "Settings Updated"


def update_user_reg_data(login, upd_pass_2):
    with db_session:
        try:
            hero = Users.get(login=login)
            ha_pa = bcrypt.hashpw(upd_pass_2.encode('utf-8'), bcrypt.gensalt(10))
            ha_pa = ha_pa.decode('utf-8')
            hero.hashed_pass = ha_pa
            return f"Data for {login} is Updated"
        except Exception as e:
            return err_handler(e)

# def get_registered_logins():
#     return None
