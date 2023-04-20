# -*- coding: utf-8 -*-

import streamlit as st
from projects import add_in_to_db, add_out_to_db
from send_emails import send_mail


def tasks_content():
    st.markdown("""
        <style>
            div[data-testid="column"]:nth-of-type(1)
            {
                text-align: center;
            } 

            div[data-testid="column"]:nth-of-type(2)
            {
                text-align: center;
            } 

            div[data-testid="column"]:nth-of-type(3)
            {
                text-align: center;
            } 
        </style>
        """, unsafe_allow_html=True)

    task_l, task_cont, task_r = st.columns([1, 15, 1])
    with task_l:
        st.empty()
    with task_r:
        st.empty()
    with task_cont:
        st.title(':orange[Tasks]')

        task_tab1, task_tab2 = st.tabs(['Add New Task', 'View Existing Tasks'])

        with task_tab1:
            add_task(task_tab1)

        with task_tab2:
            my_all = st.radio('Select', ("My", "All"), horizontal=True, label_visibility='collapsed')
            view_tasks(task_tab2, my_all)


def add_task(task_content):
    u_df = st.session_state.adb['users']
    sod_df = st.session_state.adb['sod']
    proj_df = st.session_state.adb['project']

    with task_content:
        project = st.selectbox('Select the Project', st.session_state.proj_names)

        proj_id = proj_df[proj_df.short_name == project].index.to_numpy()[0]

        sod_list = sod_df[sod_df.project_id == proj_id].set_name.tolist()

        with st.form(key="add_task"):
            units = st.multiselect('Select the Set Of Drawings / Unit',
                                   options=sod_list)  # get_sets_for_project(project))

            left_col2, right_col2 = st.columns(2)
            specialities = left_col2.multiselect("Speciality", st.session_state.spec)
            description = right_col2.text_input('Description of Task', max_chars=249)

            col_31, col_32, col_33, col_34 = st.columns([1, 1, 1, 3])
            direction = col_31.radio('Direction', ('In', 'Out'), horizontal=True)
            col_32.write('')
            col_32.write('')
            date = col_33.date_input('Date')
            non_task = col_32.checkbox('Non-Task')
            stage = col_34.radio('Stage', ('Detail Design', 'Basic Design', 'Feasibility Study',
                                           'Adaptation', 'As-built'), horizontal=True)

            left_col3, right_col3 = st.columns(2)
            link = left_col3.text_input('Link', max_chars=499)
            comments = left_col3.text_input('Comments', max_chars=249)
            source = right_col3.text_area('Received by:', value='Received by paper', height=127, max_chars=2499)

            task_preview = st.form_submit_button("Preview Task", use_container_width=True)

        # pr_l, pr_c, pr_r = st.columns([1, 4, 1])
        if task_preview:

            # proj_df = st.session_state.adb['project']
            # sod_df = st.session_state.adb['sod']

            if non_task:
                description = "Non-task"
                link = "Non-task"
                comments = "Non-task"

            st.session_state.task_preview = True

            form_dict = {
                'Unit': units,
                'Speciality': specialities,
                'Description': description,
                'Link': link,
            }

            for field_name, field_value in form_dict.items():
                if len(field_value) == 0:
                    st.warning(f"Empty field: {field_name}")
                    st.session_state.task_preview = False

            if st.session_state.task_preview:
                st.write("")

                st.markdown("""<style>
                                .task_preview table, tr {
                                        border-style: hidden;
                                        margin: auto;
                                    }
    
                                .task_preview td {
                                        border-style: hidden;
                                        text-align: left;
                                    }
                                  </style>
                                  """, unsafe_allow_html=True)

                st.markdown(f"""
                <table class="task_preview">
                    <tr>
                        <td>Project:</td><td style="color: #00bbf9;"><b>{project}</b></td>
                    </tr>
                    <tr>
                        <td>Unit:</td><td style="color: #00bbf9;"><b>{units}</b></td>
                    </tr>
                    <tr>
                        <td>Speciality:</td><td style="color: #00bbf9;"><b>{specialities}</b></td>
                    </tr>
                    <tr>
                        <td>Stage:</td><td style="color: #00bbf9;"><b>{stage}</b></td>
                    </tr>
                    <tr>
                        <td>In or Out:</td><td style="color: #00bbf9;"><b>{direction}</b></td>
                    </tr>
                    <tr>
                        <td>Date:</td><td style="color: #00bbf9;"><b>{date}</b></td>
                    </tr>
                    <tr>
                        <td>Description:</td><td style="color: #00bbf9;"><b>{description}</b></td>
                    </tr>
                    <tr>
                        <td>Link:</td><td style="color: #00bbf9;"><b>{link}</b></td>
                    </tr>
                    <tr>
                        <td>Received by:</td><td style="color: #00bbf9;"><b>{source}</b></td>
                    </tr>
                    <tr>
                        <td>Non-Task:</td><td style="color: #00bbf9;"><b>{non_task}</b></td>
                    </tr>
                    <tr>
                        <td>Comments:</td><td style="color: #00bbf9;"><b>{comments}</b></td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

                st.text('')

        if st.session_state.task_preview:
            if st.button('Add Task', type='primary', use_container_width=True):
                if direction == "In":
                    for unit in units:
                        for spec in specialities:

                            reply = "111 <*> 222" ###
                            # reply = add_in_to_db(project, unit, stage, direction, spec, date,
                            #                      description.strip(),
                            #                      link.strip(), source.strip(), comments.strip())

                            if '<*>' in reply:
                                rep1, rep2 = reply.split('<*>')
                                st.write(rep1)
                                st.code(rep2, language="python")

                                try:
                                    coord_id = sod_df[(sod_df.set_name == unit)
                                                      & (sod_df.project_id == proj_id)].coord_id.to_numpy()[0]

                                    coord_email = u_df[(u_df.index == coord_id)
                                                       & (sod_df.project_id == proj_id)].email.to_numpy()[0]

                                except:
                                    coord_email = 'sergey.priemshiy@uzliti-en.com'

                                try:
                                    perf_id = sod_df[sod_df.set_name == unit].perf_id.to_numpy()[0]
                                    perf_email = u_df[u_df.index == perf_id].email.to_numpy()[0]
                                except:
                                    perf_email = 'sergey.priemshiy@uzliti-en.com'

                                st.write(perf_email)

                                subj = f"Incoming Task  | Входящее задание:  {project}: {unit}"

                                info_html = f"""
                                        <html>
                                          <head></head>
                                          <body>
                                            <h3>
                                              Hello, Colleagues!
                                              <hr>
                                            </h3>
                                            <h5>
                                              You got this message because you are working on the project:
                                            </h5>
                                            <h5>
                                              Вы получили это письмо, потому что Вы работаете над проектом:
                                            </h5>
                                            <h4>
                                              {project}: {unit}
                                            </h4>
                                            <br>
                                            <p>
                                                Task's details at the site | Детали задания на сайте:
                                                <a href="https://e-design.streamlit.app/">e-design.streamlit.app</a>
                                                <hr>
                                                Best regards, Administration 😎
                                            </p>
                                          </body>
                                        </html>
                                    """
                                if perf_email == coord_email:
                                    coord_email = 'sergey.priemshiy@uzliti-en.com'
                                reply =200 ###
                                # reply = send_mail(perf_email, coord_email, subj, info_html)

                                if reply == 200:
                                    st.write(f"Notifications sent by emails: {perf_email}, {coord_email}")
                                    st.divider()
                                else:
                                    st.warning(reply)
                            else:
                                st.warning(reply)

                else:  # Outgoing Tasks
                    for unit in units:
                        for spec in specialities:
                            reply = add_out_to_db(project, unit, stage, direction, spec, date,
                                                  description.strip(),
                                                  link.strip(), source.strip(), comments.strip())

                            if 'ERROR' in reply.upper():
                                st.warning(reply)
                            else:
                                st.info(reply)
                            st.divider()
                st.session_state.task_preview = False


def view_tasks(ass_tab2, my_all):
    with ass_tab2:

        df = st.session_state.adb['task']
        sod_df = st.session_state.adb['sod']
        proj_df = st.session_state.adb['project']
        spec_df = st.session_state.adb['speciality']

        df['task_id'] = df.index
        df = df.set_index('s_o_d').join(sod_df[['project_id', 'set_name', 'coord_id', 'perf_id']])
        df = df.set_index('project_id').join(proj_df[['short_name']])
        df = df.set_index('speciality').join(spec_df[['abbrev']])
        df.rename(columns={'abbrev': 'speciality', 'short_name': 'project', 'set_name': 'unit'}, inplace=True)
        df.set_index('task_id', inplace=True)

        df = df[['project', 'unit', 'stage', 'in_out', 'date', 'speciality', 'description', 'link',
                 'backup_copy', 'source', 'coord_log', 'perf_log', 'comment', 'added_by', 'coord_id', 'perf_id']]

        users_df = st.session_state.adb['users']
        user_id = users_df[users_df.login == st.session_state.user].index.to_numpy()[0]

        if my_all == 'My':
            df = df[(df.coord_id == user_id) | (df.perf_id == user_id)]

        df_orig = df.copy()

        df.project = df.project.str.upper()
        df.unit = df.unit.str.upper()

        id_col, proj_col, set_col, dir_col, check_col, spec_col = st.columns([2, 3, 4, 4, 3, 4], gap='medium')

        real_spec = set(df.speciality)

        if 'spec_disable' not in st.session_state:
            st.session_state.spec_disable = False

        with check_col:
            st.text('')
            st.text('')
            check_val = st.checkbox('All Specialities', value=True)

        if check_val:
            st.session_state.spec_disable = True
        else:
            st.session_state.spec_disable = False

        id_val = id_col.text_input('ID')
        proj_val = proj_col.text_input('Project')
        set_val = set_col.text_input('Set of Drawings / Unit')
        spec_val = spec_col.selectbox("Speciality", real_spec, disabled=st.session_state.spec_disable)

        dir_val = dir_col.radio("In-Out", ('In', 'Out'), horizontal=True)
        df_orig = df_orig[df_orig.in_out == dir_val]

        df_temp = df_orig.copy()
        df_temp.project = df_temp.project.str.upper()
        df_temp.unit = df_temp.unit.str.upper()

        if len(id_val):
            df_orig = df_orig[df_orig.index == int(id_val)]
        else:
            if not st.session_state.spec_disable:
                df_orig = df_orig.loc[df_orig.speciality == spec_val]
            if proj_val:
                df_orig = df_orig.loc[df_temp.project.str.contains(proj_val.upper())]
            if set_val:
                df_orig = df_orig.loc[df_temp.unit.str.contains(set_val.upper())]

        st.write(f"{len(df_orig)} records found")
        st.experimental_data_editor(df_orig, use_container_width=True)
