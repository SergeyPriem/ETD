# -*- coding: utf-8 -*-


import streamlit as st
from models import Project
from utilities import proj_statuses, center_style, get_list_index
from projects import create_project, get_table, update_projects

from send_emails import send_mail


def manage_projects():
    empty_proj_1, content_proj, empty_proj_2 = st.columns([1, 12, 1])
    with empty_proj_1:
        st.empty()
    with empty_proj_2:
        st.empty()

    with content_proj:
        st.title(':orange[Projects]')

        center_style()

        create_proj_tab, edit_proj_tab, viewer_tab = st.tabs(['Create Project', 'Edit Existing Project', 'View Tables'])

        with create_proj_tab:
            # st.subheader('Add New Project')
            with st.form("create_project", clear_on_submit=False):
                lc, rc = st.columns(2, gap='medium')
                proj_short = lc.text_input('Project Name - short', max_chars=150)
                proj_full = rc.text_input('Project Name - full', max_chars=200)
                # responsible_el = st.selectbox('Responsible Person', get_logins_for_current())
                u_df = st.session_state.adb['users']
                responsible_el = lc.selectbox('Responsible Person',
                                              u_df.loc[u_df.status == 'current', 'login'].tolist())
                rc.text('')
                proj_status = rc.radio('Project Status', proj_statuses, horizontal=True)
                client = lc.text_input('Client', max_chars=50)
                proj_man = rc.text_input('Project Manager', max_chars=50)
                proj_tech_ass = lc.text_area('Link for Technical Task', max_chars=1000)
                proj_tech_conditions = rc.text_area('Link for Technical Conditions', max_chars=1000)
                proj_surveys = lc.text_area('Link for Technical Surveys', max_chars=1000)
                proj_mdr = rc.text_area('Link for MDR', max_chars=250)
                proj_notes = lc.text_area('Notes', max_chars=1000)
                rc.text('')
                rc.text('')
                rc.text('')
                proj_prev_but = rc.form_submit_button('Preview Data', use_container_width=True)

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

            if st.button("Create Project", use_container_width=True):
                reply = create_project(proj_short, proj_full, client, proj_man, responsible_el,
                                       proj_status, proj_tech_ass, proj_tech_conditions,
                                       proj_surveys, proj_mdr, proj_notes)

                if 'is added to DataBase' in reply:
                    st.info(reply)
                    st.session_state.adb['project'] = get_table(Project)
                else:
                    st.warning(reply)
                    st.stop()

        with edit_proj_tab:
            proj_to_edit = st.selectbox('Select Projects to Edit', st.session_state.proj_names)

            if proj_to_edit:
                proj_df = st.session_state.adb['project']

                proj_ser = proj_df[proj_df.short_name == proj_to_edit]

                u_df = st.session_state.adb['users']

                u_id = proj_ser.responsible_el.to_numpy()[0]

                prev_responsible = u_df.loc[u_df.index == u_id, 'login'].to_numpy()[0]

                with st.form('update_project'):
                    lc, rc = st.columns(2, gap='medium')
                    short_name = lc.text_input('Project Short Name', value=proj_ser.short_name.to_numpy()[0],
                                               max_chars=150).strip()
                    full_name = rc.text_input('Project Full Name',
                                              value=proj_ser.full_name.to_numpy()[0], max_chars=200).strip()
                    client = lc.text_input('Client',
                                           value=proj_ser.client.to_numpy()[0], max_chars=50).strip()
                    manager = rc.text_input('Manager',
                                            value=proj_ser.manager.to_numpy()[0], max_chars=50).strip()
                    responsible_el = lc.selectbox('Responsible Person',
                                                  st.session_state.appl_logins,
                                                  get_list_index(st.session_state.appl_logins, prev_responsible))

                    rc.text('')
                    status = rc.radio('Status', proj_statuses,
                                      get_list_index(proj_statuses, proj_ser.status.to_numpy()[0]),
                                      horizontal=True)

                    assignment = lc.text_area("Assignment location",
                                              proj_ser.assignment.to_numpy()[0],
                                              height=100,
                                              max_chars=1000).strip()
                    tech_conditions = rc.text_area("Tech. conditions location",
                                                   proj_ser.tech_conditions.to_numpy()[0], max_chars=1000).strip()
                    surveys = lc.text_area("Surveys location", proj_ser.surveys.to_numpy()[0], max_chars=1000).strip()
                    mdr = rc.text_area("MDR location", proj_ser.mdr.to_numpy()[0], max_chars=250).strip()
                    notes = lc.text_area("Notes", proj_ser.notes.to_numpy()[0], max_chars=1000).strip()

                    rc.text('')
                    rc.text('')
                    rc.text('')
                    rc.text('')
                    upd_proj_but = rc.form_submit_button('Update Project', use_container_width=True)

                if upd_proj_but:
                    if len(short_name) < 3 or len(full_name) < 3:
                        st.write('Too short Name. Should be more than 2 symbols')
                        st.stop()

                    reply = update_projects(proj_ser.index.to_numpy()[0], short_name, full_name, client,
                                            manager, responsible_el, status, assignment, tech_conditions,
                                            surveys, mdr, notes)

                    l_rep, r_rep = st.columns(2, gap='medium')
                    if reply['status'] == 201:
                        l_rep.success('Updated')

                        st.session_state.adb['project'] = reply['updated_projects']

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
                                  <b>{proj_ser.short_name.to_numpy()[0]}</b>
                                </h5>
                                <p>Some data for the Project were updated</p>
                                <br>
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
                            receiver = u_df.loc[u_df.login == responsible_el, 'email'].to_numpy()[0]
                            cc_rec = 'sergey.priemshiy@uzliti-en.com'
                        else:
                            receiver = u_df.loc[u_df.login == prev_responsible, 'email'].to_numpy()[0]
                            cc_rec = u_df.loc[u_df.login == responsible_el, 'email'].to_numpy()[0]

                        subj = f"{short_name}. Changes"

                        reply2 = send_mail(receiver, cc_rec, subj, html)

                        if reply2 == 200:
                            r_rep.success(f'Informational e-mail was sent to {receiver}, {cc_rec}')
                        else:
                            r_rep.warning(reply2)

                        st.experimental_rerun()

                    else:
                        st.warning(reply)

        with viewer_tab:
            # col_list = ['project', 'sod', 'task', 'trans', 'users']
            #
            # cols = st.columns(len(col_list))
            #
            # adb = st.session_state.adb
            # for k, v in enumerate(col_list):
            #     if cols[k].button(v, use_container_width=True):
            #         st.subheader(f":blue[Q-ty of Records: {len(adb[v])}]")
            #         if v == 'users':
            #             st.experimental_data_editor(adb[v].drop(columns=['hashed_pass']),
            #                                         use_container_width=True, height=1500)
            #         else:
            #             st.experimental_data_editor(adb[v], use_container_width=True, height=1500)

            proj_df = st.session_state.adb['project']
            sod_df = st.session_state.adb['sod']
            task_df = st.session_state.adb['task']
            u_df = st.session_state.adb['users']

            proj_df = proj_df.merge(u_df.login, how='left', left_on='responsible_el', right_on='id')
            proj_df.responsible_el = proj_df.login
            proj_df.drop(columns=['login'])

            if st.button('Projects'):
                st.experimental_data_editor(proj_df, use_container_width=True, height=1500)

