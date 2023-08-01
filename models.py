# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from pony.orm import *
import streamlit as st


@st.cache_resource
def db_func():
    db_int = Database()

    set_sql_debug(False)

    class Project(db_int.Entity):
        id = PrimaryKey(int, size=16, auto=True)
        short_name = Required(str, 150)
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

    class SOD(db_int.Entity):
        id = PrimaryKey(int, size=16, auto=True)
        project_id = Required(Project)
        set_name = Required(str, 200)
        coord_id = Optional('Users', reverse='sod_coord')
        perf_id = Optional('Users', reverse='sod_perf')
        stage = Optional(str, 100, nullable=True)
        revision = Optional(str, 10, nullable=True)
        start_date = Optional(date, nullable=True)
        current_status = Optional(str, nullable=True)
        request_date = Optional(date, nullable=True)
        trans_num = Optional(str, 1000, nullable=True)
        trans_date = Optional(date, nullable=True)
        notes = Optional(str, 1500, nullable=True)
        aux = Optional(date, nullable=True)
        assigs = Set('Task')

    class Users(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        login = Required(str, 30)
        email = Required(str, 60)
        name = Optional(str, 30, nullable=True)
        surname = Optional(str, 50, nullable=True)
        patronymic = Optional(str, 50)
        position = Optional(str, 50, nullable=True)
        branch = Optional(str, 50, nullable=True)
        phone = Optional(str, 13, nullable=True)
        telegram = Optional(str, 80, nullable=True)
        vert_menu = Optional(int, size=8)
        refresh_delay = Optional(int, size=16, nullable=True)
        script_acc = Optional(int, size=8)
        hashed_pass = Optional(str, 60)
        projects = Set(Project)
        sod_coord = Set(SOD, reverse='coord_id')
        sod_perf = Set(SOD, reverse='perf_id')
        visitlogs = Set('VisitLog')
        access_level = Required(str, 20)
        status = Required(str, 20)
        start_date = Optional(date, nullable=True)
        end_date = Optional(date, nullable=True)
        tg_id = Optional(str, 15, nullable=True)
        orders = Set('Message')
        transs = Set('Trans', reverse='responsible')
        trans_add = Set('Trans', reverse='users')

    class Task(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        stage = Optional(str, 20)
        in_out = Required(str, 10)
        date = Required(date)
        description = Required(str, 250)
        link = Required(str, 500)
        backup_copy = Optional(str, 250)
        source = Required(str, 2500)
        coord_log = Optional(str, 500, nullable=True)
        perf_log = Optional(str, 500, nullable=True)
        comment = Optional(str, 500)
        added_by = Required(str, 50)
        speciality = Required('Speciality')
        s_o_d = Required(SOD)

    class VisitLog(db_int.Entity):
        id = PrimaryKey(int, size=32, auto=True)
        login_time = Required(datetime)
        users = Required(Users)

    class Speciality(db_int.Entity):
        id = PrimaryKey(int, size=8, auto=True)
        abbrev = Required(str, 40)
        descr = Optional(str, 100)
        tasks = Set(Task)

    class Message(db_int.Entity):
        id = PrimaryKey(int, size=32, auto=True)
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
        last_remind = Optional(date, nullable=True)
        notes = Optional(str, 500)
        archieve = Optional(str, 300)

    class Trans(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        trans_num = Required(str, 50)
        trans_date = Required(date)
        in_out = Required(str, 10)
        ans_required = Required(bool)
        project = Required(Project)
        responsible = Required(Users, reverse='transs')
        author = Required(str, 50)
        ref_trans = Optional(str, 50, nullable=True)
        ref_date = Optional(date, nullable=True)
        subj = Optional(str, nullable=True)
        link = Optional(str, 200, nullable=True)
        t_type = Required(str, 50)
        notes = Optional(str, 500, nullable=True)
        received = Optional(str, 250, nullable=True)
        users = Required(Users, reverse='trans_add')
        status = Optional(str, 50, nullable=True)

    class Condition(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        table_name = Required(str, 20)
        user_login = Required(str, 50)

    class Action(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        user_login = Required(str, 50)
        act = Required(str, 100)
        action_time = Required(datetime)

    # below is interconnection tables

    class Equip(db_int.Entity):
        id = PrimaryKey(int, size=24, auto=True)
        equipment_tag = Required(str, 50, unique=True)
        descr = Required(str, 100)
        edit = Required(bool, default=False)
        notes = Optional(str, 200)
        panels = Set('Panel')

    class Panel(db_int.Entity):
        id = PrimaryKey(int, size=32, auto=True)
        eq_id = Required(Equip)
        panel_tag = Required(str, 50)
        descr = Required(str, 100)
        edit = Required(bool, default=False)
        notes = Optional(str, 200)
        blocks = Set('Block')
        cables_r = Set('Cable', reverse='right_pan_id')
        cables_l = Set('Cable', reverse='left_pan_id')
        composite_key(eq_id, panel_tag)
        panel_un = Optional(str, 100, unique=True)

    class Block(db_int.Entity):
        id = PrimaryKey(int, size=32, auto=True)
        pan_id = Required(Panel)
        block_tag = Required(str, 70, unique=True)
        descr = Optional(str, 100)
        edit = Required(bool, default=False)
        notes = Optional(str, 200)
        terminals = Set('Terminal')
        composite_key(pan_id, block_tag)
        block_un = Optional(str, 170, unique=True)

    class Cable(db_int.Entity):
        id = PrimaryKey(int, size=32, auto=True)
        cable_tag = Required(str, 100, unique=True)
        purpose_id = Required('Cab_purpose')
        type_id = Required('Cab_types')
        wires_id = Required('Cab_wires')
        sect_id = Required('Cab_sect')
        left_pan_id = Required(Panel, reverse='cables_l')
        right_pan_id = Required(Panel, reverse='cables_r')
        edit = Required(bool, default=False)
        notes = Optional(str)
        wires = Set('Wire')

    class Wire(db_int.Entity):
        id = PrimaryKey(int, size=64, auto=True)
        cable_id = Required(Cable)
        notes = Optional(str, 200)
        wire_num = Required(int, size=8)
        edit = Optional(bool, default=False)
        # left_term_id = Optional('Terminal', reverse='wires_l')
        # right_term_id = Optional('Terminal', reverse='wires_r')
        left_term_id = Optional(str, 50)
        right_term_id = Optional(str, 50)
        composite_key(cable_id, wire_num)

    class Cab_purpose(db_int.Entity):
        id = PrimaryKey(int, size=8, auto=True)
        circuit_descr = Required(str, 20)
        cables = Set(Cable)

    class Cab_types(db_int.Entity):
        id = PrimaryKey(int, size=8, auto=True)
        cab_type = Required(str, 50)
        cables = Set(Cable)

    class Cab_sect(db_int.Entity):
        id = PrimaryKey(int, auto=True)
        cables = Set(Cable)
        section = Required(str, 4)

    class Cab_wires(db_int.Entity):
        id = PrimaryKey(int, auto=True)
        wire_num = Required(int, size=8)
        cables = Set(Cable)

    class Terminal(db_int.Entity):
        id = PrimaryKey(int, auto=True)
        block_id = Required(Block)
        terminal_num = Required(str, 10)
        int_circuit = Optional(str, 10)
        int_link = Optional(str, 10)
        edit = Optional(bool, default=False)
        notes = Optional(str, 100)
        terminal_un = Optional(str, 175, unique=True)
        # wires_l = Set(Wire, reverse='left_term_id')
        # wires_r = Set(Wire, reverse='right_term_id')
        composite_key(block_id, terminal_num)

    db_int.bind(
        provider='mysql',
        host=st.secrets["db_host"],
        user=st.secrets["db_user"],
        passwd=st.secrets["db_password"],
        db=st.secrets["db_database"]
    )

    db_int.generate_mapping(create_tables=True)

    return (
        Project, SOD, Users, Task, VisitLog, Speciality, Message, Trans, Condition, Action, Equip, Panel, Block, Cable,
        Wire, Cab_purpose, Cab_types, Cab_sect, Cab_wires, Terminal, db_int
    )


d = db_func()
Project = d[0]
SOD = d[1]
Users = d[2]
Task = d[3]
VisitLog = d[4]
Speciality = d[5]
Message = d[6]
Trans = d[7]
Condition = d[8]
Action = d[9]
Equip = d[10]
Panel = d[11]
Block = d[12]
Cable = d[13]
Wire = d[14]
Cab_purpose = d[15]
Cab_types = d[16]
Cab_sect = d[17]
Cab_wires = d[18]
Terminal = d[19]
db = d[20]
