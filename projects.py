# -*- coding: utf-8 -*-

from pony.orm import *
from models import Project, SOD, Task, Users, Speciality, Trans
import pandas as pd
from datetime import date, datetime
import streamlit as st
from pre_sets import BACKUP_FOLDER
from users import err_handler

set_sql_debug(True)


@st.cache_data(ttl=360, show_spinner="Deleting Table Row...")
def delete_table_row(Table, row_id):
    with db_session:
        try:
            del_row = Table[row_id]
            if not del_row:
                return "Fail, record not found"
            del_row.delete()
            return f"Record with id {row_id} is deleted"
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Creating Backup String...')
def create_backup_string(source_link, backup_folder, task_num):
    if source_link != "Non-assignment":
        head = "xcopy /e /r /f /-y "
        tail = f'"{source_link}\\*.*" "{backup_folder}\\{task_num}"'.replace("/\\", "\\").replace("/", "\\")
        backup_string = f'{head} {tail}'
        return str(f'{backup_folder}\\{task_num}'.replace("/\\", "\\")).replace("/", "\\"), backup_string
    else:
        return "Non-assignment", "Non-assignment"


def tab_to_df(tab):
    users_dict = [u.to_dict() for u in tab]
    users_df = pd.DataFrame(users_dict)
    if 'id' in list(users_df.columns):
        users_df = users_df.set_index('id')
    if len(users_df) > 0:
        return users_df
    else:
        return "Empty Table"


@st.cache_data(ttl=360, show_spinner="Creating Project...")
def create_project(proj_short, proj_full, client, proj_man, responsible_el, proj_status, proj_tech_ass,
                   proj_tech_conditions, proj_surveys, proj_mdr, proj_notes):
    if len(proj_short) < 3:
        return f"Wrong Project's short name: {proj_short}"
    if proj_short in get_projects_names():
        return f'Project {proj_short} is already in DataBase'
    with db_session:
        try:
            Project(
                short_name=proj_short,
                full_name=proj_full,
                client=client,
                manager=proj_man,
                responsible_el=Users.get(login=responsible_el),
                status=proj_status,
                assignment=proj_tech_ass,
                tech_conditions=proj_tech_conditions,
                surveys=proj_surveys,
                mdr=proj_mdr,
                notes=proj_notes
            )
            return f'New Project {proj_short} is added to DataBase'
        except Exception as e:
            return err_handler(e)


# @st.cache_data(ttl=120, show_spinner='Getting Projects...')
def get_projects_names():
    try:
        with db_session:
            prog_name_list = select(p.short_name for p in Project)
            return list(prog_name_list)
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


# @st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets_for_project(proj):
    try:
        with db_session:
            sets_list = select(sod.set_name for sod in SOD if sod.project_id == Project.get(short_name=proj))
            return list(sets_list)
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


# @st.cache_data(ttl=60, show_spinner="Getting Data from DB...")
def get_table(table_name):
    with db_session:
        try:
            table = select(u for u in table_name)[:]
            return tab_to_df(table)
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


# @st.cache_data(ttl=60, show_spinner='Getting Assignments...')
def get_tasks(user=None):
    # print(email)
    with db_session:
        try:
            if user:
                db_user = Users.get(login=user)
                pers_sets_list = select(
                    sod.id for sod in SOD if (sod.coord_id == db_user) or (sod.perf_id == db_user))[:]
                data = select(
                    (
                        t.id,
                        t.s_o_d.project_id.short_name,
                        t.s_o_d.set_name,
                        t.speciality.abbrev,
                        t.stage,
                        t.in_out,
                        t.date,
                        t.description,
                        t.link,
                        t.backup_copy,
                        t.source,
                        t.coord_log,
                        t.perf_log,
                        t.comment,
                        t.added_by
                    ) for t in Task if t.id in pers_sets_list)[:]

            else:
                data = select(
                    (
                        t.id,
                        t.s_o_d.project_id.short_name,
                        t.s_o_d.set_name,
                        t.speciality.abbrev,
                        t.stage,
                        t.in_out,
                        t.date,
                        t.description,
                        t.link,
                        t.backup_copy,
                        t.source,
                        t.coord_log,
                        t.perf_log,
                        t.comment,
                        t.added_by
                    ) for t in Task)[:]

            df = pd.DataFrame(data, columns=[
                "id",
                "project",
                "unit",
                "speciality",
                "stage",
                "in_out",
                "date",
                "description",
                "link",
                "backup_copy",
                "source",
                "coord_log",
                "perf_log",
                "comment",
                "added_by"
            ])
            return df
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def get_pers_tasks(email: str) -> pd.DataFrame:
    """
    Returns coordinator's or performer's tasks which is not confirmed
    :param email
    :return: DataFrame
    """

    with db_session:
        try:
            data = left_join(
                (
                    t.id,
                    s.project_id.short_name,
                    s.set_name,
                    t.speciality.id,
                    t.stage,
                    t.in_out,
                    t.date,
                    t.description,
                    t.link,
                    t.backup_copy,
                    t.source,
                    t.coord_log,
                    t.perf_log,
                    t.comment,
                    t.added_by,
                )
                for t in Task
                for s in t.set_id
                if ((s.coord_id == Users[email] and email not in t.coord_log)
                    or s.perf_id == Users[email]) and email not in t.perf_log)[:]

            df = pd.DataFrame(data, columns=[
                "id",
                "project",
                "unit",
                "speciality",
                "stage",
                "in_out",
                "date",
                "description",
                "link",
                "backup_copy",
                "source",
                "coord_log",
                "perf_log",
                "comment",
                "added_by"
            ])
            return df
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


@st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets_names(selected_project):
    with db_session:
        try:
            sets_name_list = select(
                s.set_name for s in SOD
                if s.project_id == Project.get(short_name=selected_project)
            )
            return list(sets_name_list)
        except Exception as e:
            return err_handler(e)


def add_sod(proj_short: str, set_name: str, stage: str, status: str, set_start_date: date, coordinator=None,
            performer=None, notes=None) -> str:
    """
    :param proj_short:
    :param set_name:
    :param stage: stages = ('Detail Design', 'Basic Design', 'Feed', 'Feasibility Study', 'Adaptation')
    :param status: sod_statuses = (
    '0%', "Cancelled", '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '99%', "Squad Check", "Issued",
    'Approved by Client')
    :param set_start_date:
    :param coordinator:
    :param performer:
    :param notes:
    :return:
    """
    if len(set_name) < 2:
        return f"Wrong Set / Unit name: {set_name}"
    if proj_short in get_projects_names() and set_name in get_sets_names(proj_short):
        return f"Set of Drawings '{set_name}' for Project '{proj_short}' is already in DataBase"

    with db_session:
        try:
            SOD(
                project_id=Project.get(short_name=proj_short),
                set_name=set_name,
                stage=stage,
                revision='R1',
                coord_id=Users.get(login=coordinator).id,
                perf_id=Users.get(login=performer).id,
                current_status=status,
                start_date=set_start_date,
                notes=notes
            )
            return f"New Set '{set_name}' for Project '{proj_short}' is added to DataBase"
        except Exception as e:
            return err_handler(e)


def get_set_to_edit(selected_project, selected_set):
    with db_session:
        try:
            data = select(
                (
                    s.id,
                    s.project_id,
                    s.coord_id.login,
                    s.perf_id.login,
                    s.stage,
                    s.revision,
                    s.current_status,
                    s.request_date,
                    s.trans_num,
                    s.trans_date,
                    s.notes,
                )
                for s in SOD
                if (s.project_id == Project.get(short_name=selected_project) and s.set_name == selected_set)
            ).first()
            return data
        except Exception as e:
            return err_handler(e)

    # try:
    #     with db_session:
    #         table = select(
    #             e for e in SOD
    #             if (e.project_id == Project.get(short_name=selected_project) and e.set_name == selected_set))
    #         return tab_to_df(table)
    # except Exception as e:
    #     return err_handler(e)


def add_in_to_db(proj_name, sod_name, stage, in_out, speciality, issue_date, description, link, source, comment):
    with db_session:
        try:
            set_draw = select(sod for sod in SOD).filter(project_id=Project.get(short_name=proj_name).id,
                                                         set_name=sod_name).first()
            new_ass = Task(
                s_o_d=set_draw.id,  # should be an instance of SOD
                stage=stage,
                in_out=in_out,
                speciality=Speciality.get(abbrev=speciality),
                date=issue_date,
                description=description,
                link=link,
                backup_copy='NA',
                source=source,
                comment=comment,
                added_by=st.session_state.user,
            )

            new_ass_id = max(n.id for n in Task)

            if SOD[set_draw.id].coord_id.login == st.session_state.user:
                Task[new_ass_id].coord_log = str(
                    Task[new_ass_id].coord_log).replace('None', '') + \
                                             f"*{st.session_state.user}*{str(datetime.now())[:-10]}* "

            if SOD[set_draw.id].perf_id.login == st.session_state.user:
                Task[new_ass_id].perf_log = str(
                    Task[new_ass_id].perf_log).replace('None', '') + \
                                            f"*{st.session_state.user}*{str(datetime.now())[:-10]}* "

            result = create_backup_string(link, BACKUP_FOLDER, new_ass_id)
            new_ass.backup_copy = result[0]

            return f"""
            New Task for {new_ass.s_o_d.project_id.short_name}: {new_ass.s_o_d.set_name} is added to DataBase  
            Backup string:<*>
            {result[1]}
            """
        except Exception as e:
            return err_handler(e)


def add_out_to_db(proj_name, sod_name, stage, in_out, speciality, issue_date, description, link, source, comment):
    with db_session:
        try:
            set_draw = select(sod for sod in SOD).filter(project_id=Project.get(short_name=proj_name).id,
                                                         set_name=sod_name).first()
            Task(
                s_o_d=set_draw.id,  # should be an instance of SOD
                stage=stage,
                in_out=in_out,
                speciality=Speciality.get(abbrev=speciality),
                date=issue_date,
                description=description,
                link=link,
                backup_copy='NA',
                source=source,
                comment=comment,
                added_by=st.session_state.user
            )
            return f"""
            New Task for {sod_name} -> {speciality} is added to DataBase  
            """
        except Exception as e:
            return err_handler(e)

# @st.cache_data(ttl=120, show_spinner='Updating Projects...')
def update_projects(edited_proj_df):
    for ind, row in edited_proj_df.iterrows():
        if row.edit:
            if row.to_del:
                delete_table_row(Project, ind)
                continue
            with db_session:
                try:
                    proj_for_upd = Project[row.short_name]
                    proj_for_upd.full_name = row.full_name
                    proj_for_upd.client = row.client
                    proj_for_upd.manager = row.manager
                    proj_for_upd.responsible_el = row.responsible_el
                    proj_for_upd.status = row.status
                    proj_for_upd.assignment = row.assignment
                    proj_for_upd.tech_conditions = row.tech_conditions
                    proj_for_upd.surveys = row.surveys
                    proj_for_upd.mdr = row.mdr
                    proj_for_upd.notes = row.notes
                except Exception as e:
                    return err_handler(e)
    return "Updated Successfully"


# @st.cache_data(ttl=120, show_spinner='Updating Sets / Units Data...')
def update_sets(edited_set_df):
    for ind, row in edited_set_df.iterrows():
        if row.edit:
            if row.to_del:
                delete_table_row(SOD, ind)
                continue
            if (not ('@' in row.coord_id)) or (not ('@' in row.perf_id)):
                return f"Wrong email for Coordinator or Performer"
            with db_session:
                try:
                    set_to_edit = select(s for s in SOD if (s.project_id == Project[row.project_id]
                                                            and s.set_name == row.set_name)).first()
                    set_to_edit.stage = row.stage
                    set_to_edit.coord_id = Users[row.coord_id]
                    set_to_edit.perf_id = Users[row.perf_id]
                    set_to_edit.revision = row.revision
                    set_to_edit.start_date = row.start_date
                    if isinstance(row.notes, str):
                        set_to_edit.notes += "->" + row.notes
                    set_to_edit.current_status = row.current_status
                except Exception as e:
                    return err_handler(e)
    return "Updated Successfully"


# @st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_sets(login):
    with db_session:
        try:
            if login:
                sods = select(
                    (
                        s.id,
                        s.project_id.short_name,
                        s.set_name,
                        s.coord_id.login,
                        s.perf_id.login,
                        s.stage,
                        s.revision,
                        s.start_date,
                        s.current_status,
                        s.trans_num,
                        s.trans_date,
                        s.notes
                    )
                    for s in SOD
                    if (s.coord_id == Users.get(login=login) or s.perf_id == Users.get(login=login)))[:]
            else:
                sods = select(
                    (
                        s.id,
                        s.project_id.short_name,
                        s.set_name,
                        s.coord_id.login,
                        s.perf_id.login,
                        s.stage,
                        s.revision,
                        s.start_date,
                        s.current_status,
                        s.trans_num,
                        s.trans_date,
                        s.notes
                    )
                    for s in SOD)[:]

            df = pd.DataFrame(sods, columns=[
                "id",
                "project",
                "unit",
                "coordinator",
                "performer",
                "stage",
                "revision",
                "start_date",
                "status",
                "transmittal",
                "trans_date",
                "notes"
            ])

            return df
        except Exception as e:
            return err_handler(e)


# @st.cache_data(ttl=120, show_spinner='Getting Sets / Units Data...')
def get_own_tasks(set_id):
    try:
        with db_session:

            tasks = select(
                (
                    t.id,
                    t.stage,
                    t.speciality.abbrev,
                    t.in_out,
                    t.date,
                    t.description,
                    t.link,
                    t.source,
                    t.backup_copy,
                    t.coord_log,
                    t.perf_log,
                    t.comment,
                    t.added_by,
                    t.s_o_d,
                )
                for t in Task
                if t.s_o_d == SOD[set_id])[:]

            df = pd.DataFrame(tasks, columns=[
                "id",
                "stage",
                "speciality",
                "in_out",
                "date",
                "description",
                "link",
                "source",
                "backup_copy",
                "coord_log",
                "perf_log",
                "comment",
                "added_by",
                "s_o_d",

            ])

            return df

    except Exception as e:
        return err_handler(e)



def confirm_task(task_id, user, proj, sod):
    with db_session:
        try:
            heroes = select(
                (p.coord_id, p.perf_id)
                for p in SOD
                if (p.project_id == Project[proj] and p.set_name == sod)
            ).first()
            if user == heroes[0].id:
                Task[task_id].coord_log = str(
                    Task[task_id].coord_log).replace('None', '') + f"*{user}*{str(datetime.now())[:-10]}* "

            if user == heroes[1].id:
                Task[task_id].perf_log = str(
                    Task[task_id].perf_log).replace('None', '') + f"*{user}*{str(datetime.now())[:-10]}* "

        except Exception as e:
            return err_handler(e)

    # st.info(f"Task with ID {id} confirmed By user {user}")
    # print(f"Task with ID {id} confirmed By user {user}")


def confirm_trans(id, user):
    pass
    # #st.write(f"Transmittal with ID {id} is replied {user}")
    # print(f"Transmittal with ID {id} is replied {user}")


def get_trans(login=None):
    with db_session:
        try:
            if login:
                trans = select(
                    (t.id,
                     t.trans_num,
                     t.trans_date,
                     t.in_out,
                     t.ans_required,
                     t.project.short_name,
                     t.responsible.login,
                     t.author,
                     t.ref_trans,
                     t.ref_date,
                     t.subj,
                     t.link,
                     t.t_type,
                     t.notes,
                     t.received,
                     t.users.login,
                     t.status
                     )
                    for t in Trans
                    if t.responsible == Users.get(login=login))[:]
            else:
                trans = select(
                    (t.id,
                     t.trans_num,
                     t.trans_date,
                     t.in_out,
                     t.ans_required,
                     t.project.short_name,
                     t.responsible.login,
                     t.author,
                     t.ref_trans,
                     t.ref_date,
                     t.subj,
                     t.link,
                     t.t_type,
                     t.notes,
                     t.received,
                     t.users.login,
                     t.status
                     )
                    for t in Trans)[:]

            df = pd.DataFrame(trans, columns=[
                "id",
                "trans_num",
                "trans_date",
                "in_out",
                "ans_required",
                "project",
                "responsible",
                "author",
                "ref_trans",
                "ref_date",
                "subject",
                "link",
                "trans_type",
                "notes",
                "received",
                "added_by",
                "status",
            ])
            return df
        except Exception as e:
            return err_handler(e)


@st.cache_data(ttl=1800)
def get_proj_list():
    with db_session:
        try:
            proj_list = select(p.short_name for p in Project)[:]
            return proj_list
        except Exception as e:
            return err_handler(e)


def add_new_trans(project, in_trans, out_trans, t_type, subj, link, trans_date, ans_required, out_date, author,
                  responsible, notes):
    with db_session:
        try:
            if in_trans in select(p.in_trans for p in Trans)[:]:
                return f"""Transmittal {in_trans} already in DataBase"""

            Trans(
                project=Project.get(short_name=project),
                trans_num=in_trans,
                ref_trans=out_trans,
                t_type=t_type,
                subj=subj,
                link=link,
                trans_date=trans_date,
                ans_required=ans_required,
                ref_date=out_date,
                author=author,
                users=Users.get(login=responsible),
                notes=notes,
                received="",
                added_by=st.session_state.user
            )
            return f"""
            New Transmittal {in_trans} is added to DataBase  
            """

        except Exception as e:
            return err_handler(e)
