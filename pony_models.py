# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from pony.orm import *
import streamlit as st
db = Database()


class Project(db.Entity):
    short_name = PrimaryKey(str, 30)
    full_name = Optional(str, 30, unique=True)
    client = Optional(str, 50, nullable=True)
    manager = Optional(str, 50, nullable=True)
    responsible_el = Optional('Users')
    status = Optional(str, 30)
    assignment = Optional(str, 250, nullable=True)  # Contract Document
    tech_conditions = Optional(str, 250, nullable=True)
    surveys = Optional(str, 250, nullable=True)
    mdr = Optional(str, 250, nullable=True)  # link to MDR
    notes = Optional(str, 500, nullable=True)
    set_draws = Set('SOD')


class SOD(db.Entity):
    id = PrimaryKey(int, size=8, auto=True)
    project_id = Required(Project)
    set_name = Required(str, 100)
    coord_id = Optional('Users', reverse='sod_coord')
    perf_id = Optional('Users', reverse='sod_perf')
    stage = Optional(str, nullable=True)
    revision = Optional(str, nullable=True)
    start_date = Optional(date, default=lambda: date.today())
    current_status = Optional(str)
    request_date = Optional(str, nullable=True)
    trans_num = Optional(str, nullable=True)
    trans_date = Optional(str, nullable=True)
    notes = Optional(str, 500, nullable=True)
    aux = Optional(str, 200, nullable=True)
    assignments = Set('Assignment')


class Users(db.Entity):
    id = PrimaryKey(str, 50)
    name = Optional(str)
    surname = Optional(str)
    phone = Optional(str)
    telegram = Optional(str)
    vert_menu = Optional(int, size=8)
    delay_set = Optional(int, size=8)
    hashed_pass = Optional(str, 60)
    projects = Set(Project)
    sod_coord = Set(SOD, reverse='coord_id')
    sod_perf = Set(SOD, reverse='perf_id')
    visitlogs = Set('VisitLog')


class ApplUser(db.Entity):
    id = PrimaryKey(str, 50)
    position = Required(str, 50)
    branch = Required(str, 50)
    access_level = Required(str, 20)
    status = Required(str, 20)
    start_date = Optional(date)
    end_date = Optional(date)


class Assignment(db.Entity):
    id = PrimaryKey(int, size=8, auto=True)
    stage = Optional(str,25)
    in_out = Required(str, 10)
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
    set_id = Required(SOD)


class VisitLog(db.Entity):
    id = PrimaryKey(int, size=16, auto=True)
    login_time = Required(datetime)
    users = Required(Users)


class Speciality(db.Entity):
    id = PrimaryKey(str, 20, auto=True)
    descr = Required(str, 30)
    assignments = Set(Assignment)


# db.bind(provider='sqlite', filename='DBB.sqlite', create_db=True)
db.bind(
    provider='mysql',
    host=st.secrets["db_host"],
    user=st.secrets["db_user"],
    passwd=st.secrets["db_password"],
    db=st.secrets["db_database"])

db.generate_mapping(create_tables=True)
