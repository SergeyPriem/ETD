# -*- coding: utf-8 -*-

from pony.orm import *
from models import Project, SOD, Task, Users, Speciality, Trans
import pandas as pd
from datetime import date, datetime
import streamlit as st
from utilities import BACKUP_FOLDER
from users import err_handler

set_sql_debug(False)


def delete_table_row(table, row_id):
    with db_session:
        try:
            del_row = table[row_id]
            if not del_row:
                return "Fail, record not found"
            del_row.delete()
            return f"Record with id {row_id} is deleted"
        except Exception as e:
            return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def create_backup_string(source_link, backup_folder, task_num):
    if not source_link.endswith('\\'):
        source_link += '\\'
    if source_link != "Non-Task":
        head = "xcopy /e /r /f /-y "
        tail = f'"{source_link}*.*" "{backup_folder}\\{task_num}\\"'.replace("/\\", "\\").replace("/", "\\")
        backup_string = f'{head} {tail}'
        return str(f'{backup_folder}\\{task_num}\\'.replace("/\\", "\\")).replace("/", "\\"), backup_string
    else:
        return "Non-assignment", "Non-assignment"


def tab_to_df(tab):
    t_dict = [t.to_dict() for t in tab]
    t_df = pd.DataFrame(t_dict)
    if 'id' in list(t_df.columns):
        t_df = t_df.set_index('id')
    if len(t_df) > 0:
        return t_df
    else:
        return "Empty Table"


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


def get_projects_names():
    try:
        with db_session:
            prog_name_list = select(p.short_name for p in Project)
            return list(prog_name_list)
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def get_sets_for_project(proj):
    try:
        with db_session:
            sets_list = select(sod.set_name for sod in SOD if sod.project_id == Project.get(short_name=proj))
            return list(sets_list)
    except Exception as e:
        return f"🔧 {type(e).__name__} {getattr(e, 'args', None)}"


def get_table(table_name):
    with db_session:
        try:
            table = select(u for u in table_name)[:]
            return tab_to_df(table)
        except Exception as e:
            return err_handler(e)


# def get_proj_table():
#     with db_session:
#         try:
#             if st.session_state.proj_scope == "All Projects":
#                 proj = select(u for u in Project)[:]
#             if st.session_state.proj_scope == "Only Current Projects":
#                 proj = select(u for u in Project if u.status in ['current', 'perspective', 'final stage'])[:]
#             if st.session_state.proj_scope == "All excluding cancelled and suspended":
#                 proj = select(u for u in Project if u.status not in ['suspended', 'cancelled'])[:]
#             return tab_to_df(proj)
#         except Exception as e:
#             return err_handler(e)


@st.cache_data(ttl=300, show_spinner='Getting Data from DB...')
def get_tasks(user=None):
    # print(email)
    with db_session:
        try:
            if user:
                db_user = Users.get(login=user)

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
                    )
                    for t in Task
                    for s in t.s_o_d
                    if s.coord_id == db_user or s.perf_id == db_user)[:]

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


def get_pers_tasks() -> pd.DataFrame:
    """
    Returns coordinator's or performer's tasks which is not confirmed
    :return: DataFrame
    """
    login = st.session_state.login

    with db_session:
        try:
            data = left_join(
                (
                    t.id,
                    s.project_id.short_name,
                    s.set_name,
                    spec.abbrev,
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
                for s in t.s_o_d
                for spec in t.speciality
                if
                (s.coord_id == Users.get(login=login) and (login not in t.coord_log) and "confirmed" not in t.coord_log)
                or ((s.perf_id == Users.get(login=login)) and (
                        login not in t.perf_log) and "confirmed" not in t.perf_log))[:]

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
        return {
            'status': 400,
            'sod': None,
            'err_descr': f"Unit name: {set_name} should be at least 3 symbols length",
        }

    if proj_short in get_projects_names() and set_name in get_sets_names(proj_short):
        return {
            'status': 400,
            'sod': None,
            'err_descr': f"Set of Drawings '{set_name}' for Project '{proj_short}' is already in DataBase",
            }


    with db_session:
        try:
            last_id = max(s.id for s in SOD)
            SOD(
                id=last_id + 1,
                project_id=Project.get(short_name=proj_short),
                set_name=set_name,
                stage=stage,
                revision='R1',
                coord_id=Users.get(login=coordinator).id,
                perf_id=Users.get(login=performer).id,
                current_status=status,
                start_date=set_start_date,
                notes=notes,
                aux=f"<{st.session_state.login}*{str(datetime.now())[:-10]}>"

            )

            if st.session_state.proj_scope == "All Projects":
                sod = (select(u for u in SOD)[:])

            if st.session_state.proj_scope == "Only Current Projects":
                sod = select(u for u in SOD if u.project_id.status in ['current', 'perspective', 'final stage'])[:]

            if st.session_state.proj_scope == "All excluding cancelled and suspended":
                sod = select(u for u in SOD if u.project_id.status not in ['suspended', 'cancelled'])[:]

            return {
                'status': 201,
                'sod': tab_to_df(sod),
                'err_descr': None,
            }

        except Exception as e:
            return {'status': 404,
                    'sod': None,
                    'err_descr': err_handler(e),
                    }



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


def add_in_to_db(proj_name, sod_name, stage, in_out, speciality, issue_date, description, link, source, comment):
    with db_session:
        try:
            last_id = max(t.id for t in Task)
            set_draw = select(sod for sod in SOD).filter(project_id=Project.get(short_name=proj_name).id,
                                                         set_name=sod_name).first()
            new_ass = Task(
                id=int(last_id) + 1,
                s_o_d=set_draw.id,  # should be an instance of SOD
                stage=stage,
                in_out=in_out,
                speciality=Speciality.get(abbrev=speciality),
                date=issue_date,
                description=description,
                link=link,
                backup_copy='NA',
                source=source,
                coord_log=f"<{st.session_state.login}*{str(datetime.now())[:-10]}>",
                perf_log=f"<{st.session_state.login}*{str(datetime.now())[:-10]}>",
                comment=comment,
                added_by=f"<{str(st.session_state.login)}*{str(datetime.now())[:-10]}>"
            )

            new_ass_id = max(n.id for n in Task)

            result = create_backup_string(link, BACKUP_FOLDER, new_ass_id)
            new_ass.backup_copy = result[0]

            return f"""
            New Task #{int(new_ass_id) + 1} for {new_ass.s_o_d.project_id.short_name}: {new_ass.s_o_d.set_name} is added to DataBase  
            
            Copy backup string 👇 to Clipboard<*>
            {result[1]}
            """
        except Exception as e:
            return err_handler(e)


def add_out_to_db(proj_name, sod_name, stage, in_out, speciality, issue_date, description, link, source, comment):
    with db_session:

        try:
            last_id = max(t.id for t in Task)
            set_draw = select(sod for sod in SOD).filter(project_id=Project.get(short_name=proj_name).id,
                                                         set_name=sod_name).first()
            Task(
                id=int(last_id) + 1,
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
                added_by=st.session_state.login
            )
            return f"""
            New Task #{int(last_id) + 1} for {sod_name} -> {speciality} is added to DataBase  
            """
        except Exception as e:
            return err_handler(e)


def update_projects(proj_id, short_name, full_name, client, manager, responsible_el, status,
                    assignment, tech_conditions, surveys, mdr, notes):
    with db_session:
        resp_id = Users.get(login=responsible_el)
        try:
            proj_for_upd = Project[proj_id]
            proj_for_upd.short_name = short_name
            proj_for_upd.full_name = full_name
            proj_for_upd.client = client
            proj_for_upd.manager = manager
            proj_for_upd.responsible_el = resp_id
            proj_for_upd.status = status
            proj_for_upd.assignment = assignment
            proj_for_upd.tech_conditions = tech_conditions
            proj_for_upd.surveys = surveys
            proj_for_upd.mdr = mdr
            proj_for_upd.notes = notes

            if st.session_state.proj_scope == "All Projects":
                proj = select(u for u in Project)[:]
            if st.session_state.proj_scope == "Only Current Projects":
                proj = select(u for u in Project if u.status in ['current', 'perspective', 'final stage'])[:]
            if st.session_state.proj_scope == "All excluding cancelled and suspended":
                proj = select(u for u in Project if u.status not in ['suspended', 'cancelled'])[:]

            return {"status": 201,
                    "updated_projects": tab_to_df(proj),
                    "err_descr": None
                    }
        except Exception as e:
            return {"status": 404,
                    "updated_projects": None,
                    "err_descr": err_handler(e)
                    }


def update_sod(s_o_d, coord, perf, rev, status, trans_num, notes, upd_trans_chb):
    with db_session:
        try:
            unit = SOD[s_o_d]

            if (Users.get(login=st.session_state.login) in (unit.coord_id, unit.perf_id)) \
                    or Users.get(login=st.session_state.login).access_level in ["super", "dev"]:
                unit.coord_id = Users.get(login=coord)
                unit.perf_id = Users.get(login=perf)
                unit.revision = rev
                unit.current_status = status

                if upd_trans_chb and trans_num != "Not required":
                    unit.trans_num += f"<{str(trans_num)}>"

                unit.notes = notes

                if st.session_state.proj_scope == "All Projects":
                    sod = (select(u for u in SOD)[:])

                if st.session_state.proj_scope == "Only Current Projects":
                    sod = select(u for u in SOD if u.project_id.status in ['current', 'perspective', 'final stage'])[:]

                if st.session_state.proj_scope == "All excluding cancelled and suspended":
                    sod = select(u for u in SOD if u.project_id.status not in ['suspended', 'cancelled'])[:]

                return {
                    'status': 201,
                    'sod': tab_to_df(sod),
                    'err_descr': None,
                    'coord_email': unit.coord_id.email,
                    'perf_email': unit.perf_id.email,
                }

            else:
                return {'status': 403,
                        'sod': None,
                        'err_descr': "You haven't right to change Status of the Unit",
                        }

        except Exception as e:
            return {'status': 404,
                    'sod': None,
                    'err_descr': err_handler(e),
                    }


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


def confirm_task(task_id):
    user = st.session_state.login
    with db_session:
        try:

            sod = Task[task_id].s_o_d
            coord, perform = sod.coord_id, sod.perf_id

            if user == coord.login:
                if Task[task_id].coord_log:
                    Task[
                        task_id].coord_log = f"{Task[task_id].coord_log.replace('None', '')}<{user}*{str(datetime.now())[:-10]}>"
                else:
                    Task[task_id].coord_log = f"<{user}*{str(datetime.now())[:-10]}>"

            if user == perform.login:
                if Task[task_id].perf_log:
                    Task[
                        task_id].perf_log = f"{Task[task_id].perf_log.replace('None', '')}<{user}*{str(datetime.now())[:-10]}>"
                else:
                    Task[task_id].perf_log = f"<{user}*{str(datetime.now())[:-10]}>"

        except Exception as e:
            with st.sidebar:
                st.text(err_handler(e))
            return err_handler(e)

    # st.info(f"Task with ID {id} confirmed By user {user}")
    # print(f"Task with ID {id} confirmed By user {user}")


def confirm_trans(trans_num):
    user = st.session_state.login
    with db_session:
        try:
            tr = Trans.get(trans_num=trans_num)
            prev_record = tr.received.replace('-', '')
            tr.received = f"{prev_record}<{user}*{str(datetime.now())[:-10]}>"
        except Exception as e:
            return err_handler(e)


def trans_status_to_db():
    trans_num, status, out_note = st.session_state.trans_status
    with db_session:
        try:
            trans = Trans.get(trans_num=trans_num)

            prev_notes = trans.notes

            if prev_notes:
                new_notes = prev_notes + "<" + str(out_note) + ">"
            else:
                new_notes = " >>" + str(out_note)

            if st.session_state.login not in trans.received:
                trans.received = f"{trans.received.replace('-', '')}<{st.session_state.login}*{str(datetime.now())[:-10]}>"

            trans.notes = new_notes
            trans.status = status
            return 'Status Updated'
        except Exception as e:
            return err_handler(e)


def get_my_trans(login):
    with db_session:
        try:
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
                if t.responsible == Users.get(login=login) and
                t.status != "Closed" and t.status != "Issued Docs")[:]

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


def get_trans_for_preview(login=None):
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


def add_new_trans(project, trans_num, out_trans, t_type, subj, link, trans_date, ans_required, out_date, author,
                  responsible, notes, status, in_out):
    with db_session:
        try:
            if trans_num in select(p.trans_num for p in Trans)[:]:
                return f"""Transmittal {trans_num} already in DataBase"""

            Trans(
                project=Project.get(short_name=project),
                trans_num=trans_num,
                ref_trans=out_trans,
                t_type=t_type,
                subj=subj,
                link=link,
                trans_date=trans_date,
                ans_required=ans_required,
                ref_date=out_date,
                author=author,
                responsible=Users.get(login=responsible),
                notes=notes,
                received="-",
                users=Users.get(login=st.session_state.login),
                status=status,
                in_out=in_out
            )
            return f"""
            New Transmittal {trans_num} is added to DataBase  
            """

        except Exception as e:
            return err_handler(e)


def get_trans_nums(proj_short):
    with db_session:
        try:
            proj_short = list(
                select(
                    tr.trans_num for tr in Trans if tr.project == Project.get(short_name=proj_short)
                )
            )
            return proj_short
        except Exception as e:
            return err_handler(e)


def get_all():
    with db_session:
        try:
            if st.session_state.proj_scope == "All Projects":
                proj = (select(u for u in Project)[:])
                sod = (select(u for u in SOD)[:])
                task = (select(u for u in Task)[:])
                trans = (select(u for u in Trans)[:])

            if st.session_state.proj_scope == "Only Current Projects":
                proj = select(u for u in Project if u.status in ['current', 'perspective', 'final stage'])[:]
                sod = select(u for u in SOD if u.project_id.status in ['current', 'perspective', 'final stage'])[:]
                task = select(
                    u for u in Task if u.s_o_d.project_id.status in ['current', 'perspective', 'final stage'])[:]

                trans = select(u for u in Trans if u.project.status in ['current', 'perspective', 'final stage'])[:]

            if st.session_state.proj_scope == "All excluding cancelled and suspended":
                proj = select(u for u in Project if u.status not in ['suspended', 'cancelled'])[:]
                sod = select(u for u in SOD if u.project_id.status not in ['suspended', 'cancelled'])[:]
                task = select(u for u in Task if u.s_o_d.project_id.status not in ['suspended', 'cancelled'])[:]
                trans = select(u for u in Trans if u.project.status not in ['suspended', 'cancelled'])[:]

            users = (select(u for u in Users)[:])
            spec = (select(s for s in Speciality)[:])

            return {
                'project': tab_to_df(proj),
                'sod': tab_to_df(sod),
                'task': tab_to_df(task),
                'trans': tab_to_df(trans),
                'users': tab_to_df(users),
                'speciality': tab_to_df(spec)
            }

        except Exception as e:
            return err_handler(e)




def update_unit_name_stage(unit_id, new_name, new_stage):
    with db_session:
        try:
            unit = SOD[unit_id]
            unit.set_name = new_name
            unit.stage = new_stage

            if st.session_state.proj_scope == "All Projects":
                sod = (select(u for u in SOD)[:])

            if st.session_state.proj_scope == "Only Current Projects":
                sod = select(u for u in SOD if u.project_id.status in ['current', 'perspective', 'final stage'])[:]

            if st.session_state.proj_scope == "All excluding cancelled and suspended":
                sod = select(u for u in SOD if u.project_id.status not in ['suspended', 'cancelled'])[:]

            return {
                'status': 201,
                'sod': tab_to_df(sod),
                'err_descr': None,
            }

        except Exception as e:
            return {'status': 404,
                    'sod': None,
                    'err_descr': err_handler(e),
                    }
