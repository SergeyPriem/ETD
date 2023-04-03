# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from pony.orm import *
import streamlit as st

db = Database()


class Project(db.Entity):
    short_name = PrimaryKey(str, 150)
    full_name = Optional(str, 200, unique=True)
    client = Optional(str, 50, nullable=True)
    manager = Optional(str, 50, nullable=True)
    responsible_el = Optional('Users')
    status = Optional(str, 30, nullable=True)
    assignment = Optional(str, 1000, nullable=True)  # Contract Document
    tech_conditions = Optional(str, 1000, nullable=True)
    surveys = Optional(str, 1000, nullable=True)
    mdr = Optional(str, 250, nullable=True)  # link to MDR
    notes = Optional(str, 1000, nullable=True)
    set_draws = Set('SOD')
    orders = Set('Message')
    transs = Set('Trans')


class SOD(db.Entity):
    id = PrimaryKey(int, size=16, auto=True)
    project_id = Required(Project)
    set_name = Required(str, 200)
    coord_id = Optional('Users', reverse='sod_coord')
    perf_id = Optional('Users', reverse='sod_perf')
    stage = Optional(str, 100, nullable=True)
    revision = Optional(str, 10, nullable=True)
    start_date = Optional(date, default=lambda: date.today())
    current_status = Optional(str, nullable=True)
    request_date = Optional(date, nullable=True)
    trans_num = Optional(str, 250, nullable=True)
    trans_date = Optional(date)
    notes = Optional(str, 1500, nullable=True)
    aux = Optional(str, 200, nullable=True)
    assigs = Set('Task')


class Users(db.Entity):
    id = PrimaryKey(str, 50)
    name = Optional(str, 30, nullable=True)
    surname = Optional(str, 50, nullable=True)
    position = Optional(str, 50, nullable=True)
    branch = Optional(str, 50, nullable=True)
    phone = Optional(str, 13, nullable=True)
    telegram = Optional(str, 13, nullable=True)
    vert_menu = Optional(int, size=8)
    delay_set = Optional(int, size=8)
    hashed_pass = Optional(str, 60)
    projects = Set(Project)
    sod_coord = Set(SOD, reverse='coord_id')
    sod_perf = Set(SOD, reverse='perf_id')
    visitlogs = Set('VisitLog')
    access_level = Required(str, 20)
    status = Required(str, 20)
    start_date = Optional(date)
    end_date = Optional(date)
    tg_id = Optional(str, 15, nullable=True)
    orders = Set('Message')
    transs = Set('Trans', reverse='responsible')
    trans_add = Set('Trans', reverse='users')


class Task(db.Entity):
    id = PrimaryKey(int, size=24, auto=True)
    stage = Optional(str, 15)
    in_out = Required(str, 3)
    date = Required(date)
    description = Required(str, 250)
    link = Required(str, 250)
    backup_copy = Optional(str, 250)
    source = Required(str, 250)
    coord_log = Optional(datetime)
    perf_log = Optional(datetime)
    comment = Optional(str, 500)
    added_by = Required(str, 50)
    speciality = Required('Speciality')
    s_o_d = Required(SOD)


class VisitLog(db.Entity):
    id = PrimaryKey(int, size=32, auto=True)
    login_time = Required(datetime)
    users = Required(Users)


class Speciality(db.Entity):
    id = PrimaryKey(str, 20, auto=True)
    descr = Required(str, 50)
    tasks = Set(Task)


class Message(db.Entity):
    id = PrimaryKey(int, auto=True)
    start_date = Required(date)
    end_date = Optional(date)
    users = Required(Users)
    urgency = Required(str, 20)
    project = Required(Project)
    descr = Required(str, 500)
    source = Optional(str, 500)
    link = Optional(str, 300)
    status = Optional(str, 30)
    reminder = Optional(bool)
    last_remind = Optional(date)
    notes = Optional(str, 500)
    archieve = Optional(str, 300)


class Trans(db.Entity):
    in_trans = PrimaryKey(str, 50, auto=True)
    in_date = Required(date)
    ans_required = Required(bool)
    project = Required(Project)
    responsible = Required(Users, reverse='transs')
    author = Required(str, 50)
    out_date = Optional(date)
    out_trans = Optional(str, 50, nullable=True)
    subj = Optional(str, nullable=True)
    link = Optional(str, 200, nullable=True)
    t_type = Required(str, 50)
    notes = Optional(str, 500, nullable=True)
    received = Optional(str, 250, nullable=True)
    users = Required(Users, reverse='trans_add')
    status = Optional(str, 50, nullable=True)


set_sql_debug(True)

# db.bind(provider='sqlite', filename='DBB.sqlite', create_db=True)

db.bind(
    provider='mysql',
    host=st.secrets["db_host"],
    user=st.secrets["db_user"],
    passwd=st.secrets["db_password"],
    db=st.secrets["db_database"]
)

db.generate_mapping(create_tables=True)
