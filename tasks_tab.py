# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from pre_sets import specialities
from projects import get_projects_names, get_sets_for_project, add_in_to_db, add_out_to_db, \
    get_tasks


def tasks_content():
    ass_1, ass_content, ass_2 = st.columns([1, 9, 1])
    with ass_1:
        st.empty()
    with ass_2:
        st.empty()
    with ass_content:
        st.title(':orange[Tasks]')

        ass_tab1, ass_tab2 = st.tabs(['Add New Task', 'View Existing Tasks'])

        with ass_tab1:
            add_task(ass_tab1)

        with ass_tab2:
            own_all = st.radio('Select', ("Own", "All"), horizontal=True, label_visibility='collapsed')
            view_tasks(ass_tab2, own_all)


def add_task(ass_content):
    with ass_content:
        # left_col, right_col = st.columns(2)
        project = st.selectbox('Select the Project', get_projects_names())
        with st.form(key="add_ass"):
            set_of_dr = st.multiselect('Select the Set Of Drawings / Unit',
                                       options=get_sets_for_project(project))

            left_col2, right_col2 = st.columns(2)
            speciality = left_col2.multiselect("Speciality", specialities)
            description = right_col2.text_input('Description of Task')

            col_31, col_32, col_33, col_34 = st.columns([1, 1, 1, 3])
            direction = col_31.radio('Direction', ('IN', 'OUT'), horizontal=True)
            col_32.write('')
            col_32.write('')
            date = col_33.date_input('Date')
            non_assign = col_32.checkbox('Non-Task')
            stage = col_34.radio('Stage', ('Detail Design', 'Basic Design', 'Feasibility Study',
                                           'Adaptation', 'As-built'), horizontal=True)

            left_col3, right_col3 = st.columns(2)
            link = left_col3.text_input('Path')
            comments = left_col3.text_input('Comments')
            source = right_col3.text_area('Received by:', value='Received by paper', height=127)

            ass_submitted = st.form_submit_button("Preview Task")

            if ass_submitted:
                if non_assign:
                    description = "Non-assignment"
                    link = "Non-assignment"
                    comments = "Non-assignment"

                right_col2.write("")
                right_col2.write("")
                left_col2.markdown(f"""
                Project: **:blue[{project}]**
                <br>
                Speciality: **:blue[{speciality}]**
                <br>
                Stage: **:blue[{stage}]**
                <br>
                In or Out: **:blue[{direction}]**
                <br>
                Non-Task: **:blue[{non_assign}]**
                """, unsafe_allow_html=True)
                right_col2.markdown(f"""
                Set of Drawings / Unit: **:blue[{set_of_dr}]**
                <br>
                Date: **:blue[{date}]**
                <br>
                Description: **:blue[{description}]**
                <br>
                Path: **:blue[{link}]**
                <br>
                Received by: **:blue[{source}]**
                """, unsafe_allow_html=True)

                reply = ''

        if st.button('Add Task'):

            if direction == "IN":
                for single_set in set_of_dr:
                    reply = add_in_to_db(project, single_set, stage, direction, speciality[0], date, description,
                                         link, source, comments)
            else:
                for single_spec in speciality:
                    reply = add_out_to_db(project, set_of_dr[0], stage, direction, single_spec, date, description,
                                          link, source, comments)

            if '<*>' in reply:
                rep1, rep2 = reply.split('<*>')
                st.write(rep1)
                st.info(rep2)
            else:
                st.warning(reply)


def view_tasks(ass_tab2, own_all):
    with ass_tab2:
        if own_all == 'Own':
            df = get_tasks(st.session_state.user)
        else:
            df = get_tasks()

        df_orig = pd.DataFrame()

        if isinstance(df, pd.DataFrame):
            df_orig = df.copy().set_index('id')
        else:
            st.warning(df)
            st.stop()

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
