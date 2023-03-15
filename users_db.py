# -*- coding: utf-8 -*-

import datetime
import pandas as pd
import streamlit as st
import bcrypt
from sqlmodel import select, Session
from models import Users, Appl_user, Visit_log, Contact
from database import engine
from time import sleep

from pre_sets import request_sleep


@st.cache_data(ttl=120, show_spinner="Moving to former users...")
def move_to_former(employee_to_edit, end_date):
    sleep(request_sleep)
    with Session(engine) as session:
        statement = select(Appl_user).where(Appl_user.company_email == employee_to_edit)
        results = session.exec(statement)
        hero = results.one()
        hero.access_level = 'prohibited'
        hero.status = 'former'
        hero.end_date = end_date
        session.add(hero)
        session.commit()
        session.refresh(hero)

        return f'''**{hero.company_email}** moved to Former Userss  
        by date **{end_date}**.  
        Access status: **:red[{hero.access_level}]**'''


@st.cache_data(ttl=120, show_spinner="Updating user's in DataBase...")
def update_users_in_db(email, position, department, start_date, access_level):
    sleep(request_sleep)
    with Session(engine) as session:
        statement = select(Appl_user).where(Appl_user.company_email == email)
        results = session.exec(statement)
        hero = results.one()
        hero.position = position
        hero.department = department
        hero.start_date = start_date
        hero.access_level = access_level
        hero.status = 'current'
        hero.end_date = None
        try:
            session.add(hero)
            session.commit()
            session.refresh(hero)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return f"""Updated Data for Users with e-mail **{hero.company_email}**  
                   Position: **:blue[{hero.position}]**  
                   Department: **:blue[{hero.department}]**  
                   Access level: **:blue[{hero.access_level}]**  
                   Status: **:blue[{hero.status}]**"""


# @st.cache_data(ttl=120, show_spinner="Checking user's credentials...")
def check_user(email, password):
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Users.hashed_pass).where(Users.company_email == email)
            hashed_password = session.exec(stmt).one()
            hashed_password = hashed_password.encode('utf-8')
            valid_pass = bcrypt.checkpw(password.encode('utf-8'), hashed_password)
            return valid_pass
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner="Getting applied e-mails")
def get_appl_emails():
    try:
        with Session(engine) as session:
            stmt = select(Appl_user.company_email)
            appl_emails = session.exec(stmt).all()
            return appl_emails
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


def get_registered_emails():
    try:
        with Session(engine) as session:
            stmt = select(Users.company_email)
            registered_emails = session.exec(stmt).all()
            return registered_emails
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner="Getting aplied user data")
def get_appl_user_data(email):
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Appl_user).where(Appl_user.company_email == email)
            appl_user = session.exec(stmt).one()
            return appl_user
    except Exception as e:
        return e


@st.cache_data(ttl=120, show_spinner="Adding to log...")
def add_to_log(email):
    sleep(request_sleep)
    with Session(engine) as session:
        logger = Visit_log(company_email=email, login_time=datetime.datetime.now())
        try:
            session.add(logger)
            session.commit()
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"
        return "OK"

def create_user(name, surname, phone, telegram, company_email, password):
    sleep(request_sleep)
    if company_email in get_appl_emails():
        if company_email in get_registered_emails():
            return "Users already registered!"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10))
        hashed_password = hashed_password.decode('utf-8')
        with Session(engine) as session:
            new_user = Users(
                name=name,
                surname=surname,
                phone=phone,
                telegram=telegram,
                company_email=company_email,
                hashed_pass=hashed_password,
                vert_menu=1,
                delay_set=3,
            )
            try:
                session.add(new_user)
                session.commit()
            except Exception as e:
                return f"{type(e).__name__}{getattr(e, 'args', None)}"
        return "Registered Successfully"
    else:
        return "Failed to create. Ask admin to add you to DataBase"


def create_appl_user(company_email, position, department, access_level, start_date):
    sleep(request_sleep)
    if '@' not in company_email or len(company_email) < 12:
        return f'Wrong e-mail {company_email}'
    if company_email in get_appl_emails():
        return f'{company_email} already exist'
    else:
        print(company_email, position, department, access_level)
        with Session(engine) as session:
            hero = Appl_user(
                company_email=company_email,
                position=position,
                department=department,
                access_level=access_level,
                start_date=start_date,
                end_date=None,
                status='current',
            )
            try:
                session.add(hero)
                session.commit()
                session.refresh(hero)
            except Exception as e:
                return e
        return f'Users with e-mail {hero.company_email} is added to DataBase'


def update_user_data(employee_to_edit, user_tab):
    # get employee data from DB
    sleep(request_sleep)
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


def get_logged_rights(email):
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Appl_user.access_level).where(Appl_user.company_email == email)
            access_level = session.exec(stmt).one()
            return access_level
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"{type(e).__name__}{getattr(e, 'args', None)}"


@st.cache_data(show_spinner="Fetching data from API...")
def get_phones():
    try:
        with engine.connect() as connection:
            stmt = select(Contact)
            return pd.read_sql_query(stmt, connection)
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def get_settings(email):
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Users).where(Users.company_email == email)
            user_settings = session.exec(stmt).one()
            return user_settings.vert_menu, user_settings.delay_set
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def update_settings(email, menu, delay):
    sleep(request_sleep)
    with Session(engine) as session:
        statement = select(Users).where(Users.company_email == email)
        results = session.exec(statement)
        hero = results.one()
        hero.vert_menu = menu
        hero.delay_set = delay
        try:
            session.add(hero)
            session.commit()
            session.refresh(hero)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return "Settings Updated"


def update_user_reg_data(upd_phone, upd_telegram, email, upd_pass_2):
    sleep(request_sleep)
    with Session(engine) as session:
        statement = select(Users).where(Users.company_email == email)
        results = session.exec(statement)
        hero = results.one()
        hero.phone = upd_phone
        hero.telegram = upd_telegram
        hero.hashed_pass = bcrypt.hashpw(upd_pass_2.encode('utf-8'), bcrypt.gensalt())
        try:
            session.add(hero)
            session.commit()
            # session.refresh(hero)
        except Exception as e:
            return f"{type(e).__name__}{getattr(e, 'args', None)}"

        return "Data Updated"
