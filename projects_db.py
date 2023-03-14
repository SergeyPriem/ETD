# -*- coding: utf-8 -*-

import sqlite3
from time import sleep

import pandas as pd
import streamlit as st
from sqlmodel import select, Session, or_

from database import engine
from models import Project, Set_draw, Assignment
from pre_sets import request_sleep


@st.cache_data(ttl=60, show_spinner="Getting Data from DB...")
def get_table(table):
    sleep(request_sleep)
    try:
        with engine.connect() as connection:
            stmt = select(table)
            df = pd.read_sql_query(stmt, connection)
            return df
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=360, show_spinner="Deleting Table Row...")
def delete_table_row(Table, row_id: int):
    sleep(request_sleep)
    with Session(engine) as session:
        del_row = session.get(Table, row_id)
        if not del_row:
            return "Fail, record not found"
        session.delete(del_row)
        session.commit()
        return f"Record with id {row_id} is deleted"


@st.cache_data(ttl=360, show_spinner="Creating Project...")
def create_project(proj_short, proj_full, client, proj_man, responsible_el, proj_status, proj_tech_ass,
                   proj_tech_conditions, proj_surveys, proj_mdr, proj_notes):
    sleep(request_sleep)
    if len(proj_short) < 3:
        return f"Wrong Project's short name: {proj_short}"
    if proj_short in get_projects_names():
        return f'Project {proj_short} is already in DataBase'
    with Session(engine) as session:
        new_project = Project(
            short_name=proj_short,
            full_name=proj_full,
            client=client,
            manager=proj_man,
            responsible_el=responsible_el,
            status=proj_status,
            assignments=proj_tech_ass,
            tech_conditions=proj_tech_conditions,
            surveys=proj_surveys,
            mdr=proj_mdr,
            notes=proj_notes
        )
        try:
            session.add(new_project)
            session.commit()
            session.refresh(new_project)
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"
        return f'New Project {new_project.short_name} is added to DataBase'


@st.cache_data(ttl=360, show_spinner="Creating Drawing Set...")
def create_set(proj_short, set_name, stage, coordinator, performer, status, set_start_date, notes):
    sleep(request_sleep)
    if len(set_name) < 2:
        return f"Wrong Set / Unit name: {set_name}"
    if proj_short in get_projects_names() and set_name in get_sets_names(proj_short):
        return f"Set of Drawings '{set_name}' for Project '{proj_short}' is already in DataBase"
    with Session(engine) as session:
        new_sod = Set_draw(
            project=proj_short,
            set_name=set_name,
            stage=stage,
            coordinator=coordinator,
            performer=performer,
            current_status=status,
            start_date=set_start_date,
            notes=notes
            )
        try:
            session.add(new_sod)
            session.commit()
            session.refresh(new_sod)
        except Exception as e:
            return f"🔧 {set_start_date}"  # f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"
        return f"New Set '{new_sod.set_name}' for Project '{new_sod.project}' is added to DataBase"


@st.cache_data(ttl=360, show_spinner="Getting Projects List...")
def get_projects_names():
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Project.short_name)
            return session.exec(stmt).all()
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets_names(selected_project):
    sleep(request_sleep)
    try:
        with Session(engine) as session:
            stmt = select(Set_draw.set_name).where(Set_draw.project == selected_project)
            # return session.exec(stmt).all()
            return session.exec(stmt).all()
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets_to_edit(selected_project, selected_set):
    sleep(request_sleep)
    try:
        with engine.connect() as connection:
            stmt = select(Set_draw).where(Set_draw.project == selected_project, Set_draw.set_name == selected_set)
            return pd.read_sql_query(stmt, connection)
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Updating Projects...')
def update_projects(edited_proj_df):
    sleep(request_sleep)
    for ind, row in edited_proj_df.iterrows():
        if row.edit:
            if row.to_del:
                delete_table_row(Project, ind)
                continue
            with Session(engine) as session:

                statement = select(Project).where(Project.short_name == row.short_name)
                results = session.exec(statement)
                upd_project = results.one()

                upd_project.full_name = row.full_name
                upd_project.client = row.client
                upd_project.manager = row.manager
                upd_project.responsible_el = row.responsible_el
                upd_project.status = row.status
                upd_project.assignments = row.assignments
                upd_project.tech_conditions = row.tech_conditions
                upd_project.surveys = row.surveys
                upd_project.mdr = row.mdr
                upd_project.notes = row.notes
                try:
                    session.add(upd_project)
                    session.commit()
                    # session.refresh(upd_project)  # if saved in DB is required
                except Exception as e:
                    return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"
    return "Updated Successfully"


@st.cache_data(ttl=120, show_spinner='Updating Sets / Units Data...')
def update_sets(edited_set_df):
    sleep(request_sleep)
    for ind, row in edited_set_df.iterrows():
        if row.edit:
            if row.to_del:
                delete_table_row(Set_draw, ind)
                continue
            if (not ('@' in row.coordinator)) or (not ('@' in row.performer)):
                return f"Wrong email for Coordinator or Performer"
            with Session(engine) as session:

                statement = select(Set_draw).where(Set_draw.project == row.project, Set_draw.set_name == row.set_name)
                results = session.exec(statement)
                upd_set = results.one()

                upd_set.stage = row.stage
                upd_set.coordinator = row.coordinator
                upd_set.performer = row.performer
                upd_set.start_date = row.start_date
                upd_set.notes = row.notes
                upd_set.current_status = row.current_status
                try:
                    session.add(upd_set)
                    session.commit()
                    # session.refresh(upd_set)   # if saved in DB is required
                except Exception as e:
                    return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"
    return "Updated Successfully"


@st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets(email):
    sleep(request_sleep)
    try:
        with engine.connect() as connection:
            if email:
                stmt = select(Set_draw).where(or_(Set_draw.coordinator == email, Set_draw.performer == email))
            else:
                stmt = select(Set_draw)
            return pd.read_sql_query(stmt, connection)
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_own_tasks(proj_set):
    try:
        with engine.connect() as connection:
            stmt = select(Assignment).where(Assignment.project == proj_set[0], Assignment.set_draw == proj_set[1])
            return pd.read_sql_query(stmt, connection)
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def get_sets_for_project(project):
    try:
        with Session(engine) as session:
            stmt = select(Set_draw).where(Set_draw.project == project)
            return session.exec(stmt).all()
    except Exception as e:
        # return "🔧 Connection to DB is failed"
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"
