# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from models import Project, Task, VisitLog, SOD, Users, Trans, Speciality
from pre_sets import proj_statuses
from projects import create_project, get_table, update_projects
from datetime import datetime

from send_emails import send_mail


def get_list_index(a_list: list, elem: str) -> int:
    try:
        ind = a_list.index(elem)
        return ind
    except:
        return 0


def manage_projects():
    empty_proj_1, content_proj, empty_proj_2 = st.columns([1, 12, 1])
    with empty_proj_1:
        st.empty()
    with empty_proj_2:
        st.empty()

    with content_proj:
        st.title(':orange[Manage Projects]')
        proj_tab1, proj_tab2, viewer_tab = st.tabs(['Create Project', 'Edit Existing Project', 'View Tables'])

        with proj_tab1:
            # st.subheader('Add New Project')
            with st.form("create_project", clear_on_submit=False):
                proj_short = st.text_input('Project Name - short')
                proj_full = st.text_area('Project Name - full')
                # responsible_el = st.selectbox('Responsible Person', get_logins_for_current())
                users_df = st.session_state.adb['users']
                responsible_el = st.selectbox('Responsible Person',
                                              users_df.loc[users_df.status == 'current', 'login'].tolist())
                proj_status = st.radio('Project Status', proj_statuses, horizontal=True)
                client = st.text_input('Client')
                proj_tech_ass = st.text_area('Link for Technical Task')
                proj_tech_conditions = st.text_area('Link for Technical Conditions')
                proj_surveys = st.text_area('Link for Technical Surveys')
                proj_mdr = st.text_area('Link for MDR')
                proj_man = st.text_input('Project Manager')
                proj_notes = st.text_area('Notes')
                proj_preview_col, proj_create_col = st.columns([1, 1])
                proj_prev_but = st.form_submit_button('Preview Data')

            with proj_preview_col:
                # preview_checkbox = st.checkbox('Preview Project',
                #                                value=st.session_state.preview_proj_stat)

                if proj_prev_but:
                    st.write(f"""
                    Short Name: **:blue[{proj_short}]**  
                    Full Name: **:blue[{proj_full}]**  
                    Responsible: **:blue[{responsible_el}]**  
                    Status: **:blue[{proj_status}]**  
                    Client: **:blue[{client}]**  
                    Link for Technical Task: **:blue[{proj_tech_ass}]**  
                    Link for Technical Conditions: **:blue[{proj_tech_conditions}]**  
                    Link for Technical Surveys: **:blue[{proj_surveys}]**  
                    Link for MDR: **:blue[{proj_mdr}]**  
                    Project Manager: **:blue[{proj_man}]**  
                    Notes: **:blue[{proj_notes}]**  
                    """)

            if st.button("Create Project"):
                reply = create_project(proj_short, proj_full, client, proj_man, responsible_el,
                                       proj_status, proj_tech_ass, proj_tech_conditions,
                                       proj_surveys, proj_mdr, proj_notes)
                if 'is added to DataBase' in reply:
                    st.info(reply)
                    st.session_state.adb['project'] = get_table(Project)
                else:
                    st.warning(reply)
                    st.stop()

        with proj_tab2:
            proj_to_edit_list = st.multiselect('Select Projects to Edit', st.session_state.proj_names)

            if proj_to_edit_list:
                proj_df = st.session_state.adb['project']

                if not isinstance(proj_df, pd.DataFrame):
                    st.warning(proj_df)
                    st.stop()

                proj_df = proj_df[proj_df.short_name.isin(proj_to_edit_list)]

                u_df = st.session_state.adb['users']

                u_id = proj_df.responsible_el.to_numpy()[0]

                prev_responsible = u_df.loc[u_df.index == u_id, 'login'].to_numpy()[0]

                with st.form('update_project'):
                    short_name = st.text_input('Project Short Name', value=proj_df.short_name.to_numpy()[0],
                                               max_chars=150).strip()
                    full_name = st.text_input('Project Full Name',
                                              value=proj_df.full_name.to_numpy()[0], max_chars=200).strip()
                    client = st.text_input('Client',
                                           value=proj_df.client.to_numpy()[0], max_chars=50).strip()
                    manager = st.text_input('Manager',
                                            value=proj_df.client.to_numpy()[0], max_chars=50).strip()
                    responsible_el = st.selectbox('Responsible Person',
                                                  st.session_state.appl_logins,
                                                  get_list_index(st.session_state.appl_logins,
                                                                 prev_responsible))
                    status = st.selectbox('Status', proj_statuses,
                                          get_list_index(proj_statuses, proj_df.status.to_numpy()[0]))

                    assignment = st.text_area("Assignment location",
                                              proj_df.assignment.to_numpy()[0], max_chars=1000).strip()
                    tech_conditions = st.text_area("Tech. conditions location",
                                                   proj_df.tech_conditions.to_numpy()[0], max_chars=1000).strip()
                    surveys = st.text_area("Surveys location", proj_df.surveys.to_numpy()[0], max_chars=1000).strip()
                    mdr = st.text_area("MDR location", proj_df.mdr.to_numpy()[0], max_chars=250).strip()
                    notes = st.text_area("Notes", proj_df.notes.to_numpy()[0], max_chars=1000).strip()

                    upd_proj_but = st.form_submit_button('Update Project', use_container_width=True)

                if upd_proj_but:
                    # proj_len_edited = len(edited_proj_df[edited_proj_df.edit])
                    if len(short_name) < 3 or len(full_name) < 3:
                        st.write('Too short Name')

                        # reply = update_projects(proj_df.index.to_numpy()[0], short_name, full_name, client,
                        #                         manager, responsible_el, status, assignment, tech_conditions,
                        #                         surveys, mdr, notes)
                    reply = 201
                    if reply == 201:
                        st.success('Updated')

                        html = f"""
                            <html>
                              <head></head>
                              <body>
                                <h3>
                                  Hello, Colleague!
                                  <hr>
                                </h3>
                                <h5>
                                  You got this message because you are involved in the project : 
                                  <b>{proj_df.short_name.to_numpy()[0]}</b>
                                </h5>
                                <p>Some data for the Project were updated</p>
                                <p>Short name: <b>{short_name}</b></p>
                                <p>Full name: <b>{full_name}</b></p>
                                <p>Client: <b>{client}</b></p>
                                <p>Manager: <b>{manager}</b></p>
                                <p>Responsible Person: <b>{responsible_el}</b></p>
                                <p>Project status: <b>{status}</b></p>
                                <p>Assignment: <b>{assignment}</b></p>
                                <p>Technical Conditions: <b>{tech_conditions}</b></p>
                                <p>Surveys: <b>{surveys}</b></p>
                                <p>MDR: <b>{mdr}</b></p>
                                <p>Notes: <b>{notes}</b></p>
                                <p>
                                    <hr>
                                    Best regards, Administration 😎
                                </p>
                              </body>
                            </html>
                        """

                        if prev_responsible == responsible_el:
                            # receivers = [u_df.loc[u_df.login == responsible_el, 'email'].to_numpy()[0]]
                            receivers = ['sergey.priemshiy@uzliti-en.com']

                        else:
                            # receiver_2 = u_df.loc[u_df.login == prev_responsible, 'email'].to_numpy()[0]
                            # receivers = [
                            #     u_df.loc[u_df.login == responsible_el, 'email'].to_numpy()[0],
                            #     receiver_2
                            #     ]
                            receiver_2 = 'sergey.priemshiy@uzliti-en.com'
                            receivers = [
                                'sergey.priemshiy@uzliti-en.com',
                                receiver_2
                            ]
                            html = ""

                        cc_rec = 'sergey.priemshiy@uzliti-en.com'

                        subj = f"Project: {short_name}. Changes"

                        reply2 = send_mail(receivers, cc_rec, subj, html)

                        st.info(reply2)

                    else:
                        st.warning(reply)

        with viewer_tab:
            # tab_list = get_tab_names()
            # tab_name = st.radio("Select the Table for view", (
            #     Task, Project, SOD, Users, VisitLog, Trans, Speciality), horizontal=True)

            col_list = ['project', 'sod', 'task', 'trans', 'users']

            cols = st.columns(len(col_list))

            adb = st.session_state.adb
            for k, v in enumerate(col_list):
                if cols[k].button(v, use_container_width=True):
                    if v == 'users':
                        st.experimental_data_editor(adb[v].drop(columns=['hashed_pass']),
                                                    use_container_width=True, height=1500)
                    else:
                        st.experimental_data_editor(adb[v], use_container_width=True, height=1500)

            # if st.button('Projects'):
            #     st.write(adb['project'])
            #
            # if st.button('Units'):
            #     st.write(adb['sod'])
            #
            # if st.button('Tasks'):
            #     start_time = datetime.now()
            #     st.write(adb['task'])
            #     st.text((datetime.now() - start_time))
            #
            # if st.button('Transmittals'):
            #     start_time = datetime.now()
            #     st.write(adb['trans'])
            #     st.text((datetime.now() - start_time))
            #
            # if st.button('Users'):
            #     st.write(adb['users'].drop(columns=['hashed_pass']))
            #
            # if st.button("Tasks from DB"):
            #     start_time = datetime.now()
            #     tr_df = get_table(Task)
            #     st.write(tr_df)
            #     st.text((datetime.now() - start_time))

            # df = get_table(tab_name)
            # if isinstance(df, pd.DataFrame):
            #     st.info(f'Records Q-ty: {len(df)}')
            #     # st.write(df)
            #     st.experimental_data_editor(df, use_container_width=True)
            # else:
            #     st.warning('No records found')
