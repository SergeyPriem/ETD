# -*- coding: utf-8 -*-

import streamlit as st
from pre_sets import specialities
from projects import get_sets_for_project, add_in_to_db, add_out_to_db


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
    with task_content:
        project = st.selectbox('Select the Project', st.session_state.proj_names)

        with st.form(key="add_task"):
            set_of_dr = st.multiselect('Select the Set Of Drawings / Unit',
                                       options=get_sets_for_project(project))

            left_col2, right_col2 = st.columns(2)
            speciality = left_col2.multiselect("Speciality", specialities)
            description = right_col2.text_input('Description of Task')

            col_31, col_32, col_33, col_34 = st.columns([1, 1, 1, 3])
            direction = col_31.radio('Direction', ('In', 'Out'), horizontal=True)
            col_32.write('')
            col_32.write('')
            date = col_33.date_input('Date')
            non_task = col_32.checkbox('Non-Task')
            stage = col_34.radio('Stage', ('Detail Design', 'Basic Design', 'Feasibility Study',
                                           'Adaptation', 'As-built'), horizontal=True)

            left_col3, right_col3 = st.columns(2)
            link = left_col3.text_input('Path')
            comments = left_col3.text_input('Comments')
            source = right_col3.text_area('Received by:', value='Received by paper', height=127)

            task_preview = st.form_submit_button("Preview Task", use_container_width=True)

        pr_l, pr_c, pr_r = st.columns([1, 2, 1])

        if task_preview:
            st.session_state.task_preview = True

            st.write("")

            with pr_c:
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
                        <td>Project:</td><td style="color: #1569C7;"><b>{project}</b></td>
                    </tr>
                    <tr>
                        <td>Unit:</td><td style="color: #1569C7;"><b>{set_of_dr}</b></td>
                    </tr>
                    <tr>
                        <td>Speciality:</td><td style="color: #1569C7;"><b>{speciality}</b></td>
                    </tr>
                    <tr>
                        <td>Stage:</td><td style="color: #1569C7;"><b>{stage}</b></td>
                    </tr>
                    <tr>
                        <td>In or Out:</td><td style="color: #1569C7;"><b>{direction}</b></td>
                    </tr>
                    <tr>
                        <td>Date:</td><td style="color: #1569C7;"><b>{date}</b></td>
                    </tr>
                    <tr>
                        <td>Description:</td><td style="color: #1569C7;"><b>{description}</b></td>
                    </tr>
                    <tr>
                        <td>Path:</td><td style="color: #1569C7;"><b>{link}</b></td>
                    </tr>
                    <tr>
                        <td>Received by:</td><td style="color: #1569C7;"><b>{source}</b></td>
                    </tr>
                    <tr>
                        <td>Non-Task:</td><td style="color: #1569C7;"><b>{non_task}</b></td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

        if st.session_state.task_preview:

            if non_task:
                description = "Non-task"
                link = "Non-task"
                comments = "Non-task"

            st.text('')

            if pr_c.button('Add Task', type='primary', use_container_width=True):

                st.session_state.task_preview = False

                if direction == "In":
                    for single_set in set_of_dr:
                        reply = add_in_to_db(project, single_set, stage, direction, speciality[0], date,
                                             description,
                                             link, source, comments)

                        # st.write((project, single_set, stage, direction, speciality[0], date, description,
                        #           link, source, comments))
                        # reply = "Added <*> Successfully"

                        if '<*>' in reply:
                            rep1, rep2 = reply.split('<*>')
                            st.write(rep1)
                            st.info(rep2)
                        else:
                            st.warning(reply)

                else:
                    for single_spec in speciality:
                        reply = add_out_to_db(project, set_of_dr[0], stage, direction, single_spec, date,
                                              description,
                                              link, source, comments)
                        # st.write((project, set_of_dr[0], stage, direction, single_spec, date, description,
                        #           link, source, comments))
                        # reply = "Added <*> Successfully"
                        if 'ERROR' in reply.upper():
                            st.warning(reply)
                        else:
                            st.info(reply)

                st.button("N E X T")


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
        user_id = users_df[users_df.login == st.session_state.user].index.values[0]

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
