# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from models import Assignment
from pre_sets import specialities, reporter
from projects_db import get_projects_names, get_table, get_sets_for_project, add_in_to_db, add_out_to_db


def assignments_content():
    ass_1, ass_content, ass_2 = st.columns([1, 9, 1])
    with ass_1:
        st.empty()
    with ass_2:
        st.empty()
    with ass_content:
        st.title(':orange[Assignments]')

        ass_tab1, ass_tab2 = st.tabs(['Add Assignment', 'View Assignments'])

        with ass_tab1:
            add_assignment(ass_tab1)

        with ass_tab2:
            view_assignments(ass_tab2)


def add_assignment(ass_content):
    with ass_content:
        left_col, right_col = st.columns(2)
        project = left_col.selectbox('Select the Project', get_projects_names())
        with st.form(key="add_ass"):
            set_of_dr = right_col.multiselect('Select the Set Of Drawings / Unit',
                                              options=get_sets_for_project(project))

            left_col2, right_col2 = st.columns(2)
            speciality = left_col2.multiselect("Speciality", specialities)
            description = right_col2.text_input('Description of Assignment')

            col_31, col_32, col_33, col_34 = st.columns([1, 1, 1, 3])
            direction = col_31.radio('Direction', ('IN', 'OUT'), horizontal=True)
            col_32.write('')
            col_32.write('')
            date = col_33.date_input('Date')
            non_assign = col_32.checkbox('Non-Assignment')
            stage = col_34.radio('Stage', ('Detail Design', 'Basic Design', 'Feasibility Study',
                                           'Adaptation', 'As-built'), horizontal=True)

            left_col3, right_col3 = st.columns(2)
            link = left_col3.text_input('Path')
            comments = left_col3.text_input('Comments')
            source = right_col3.text_area('Received by:', value='Received by paper', height=127)


            ass_submitted = st.form_submit_button("Add Assignment")


            if ass_submitted:
                if non_assign:
                    description = "Non-assignment"
                    link = "Non-assignment"
                    comments = "Non-assignment"

                if left_col2.checkbox('Preview'):
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
                    Non-Assignment: **:blue[{non_assign}]**
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

            # if st.button('Add to DataBase'):
                if direction == "IN":
                    for single_set in set_of_dr:
                        reply = add_in_to_db(project, single_set, stage, direction, speciality[0], date, description,
                                             link, source, 'log', comments)
                        # reporter(reply, 10)
                        st.text(reply)
                else:
                    for single_spec in speciality:
                        reply = add_out_to_db(project, set_of_dr[0], stage, direction, single_spec, date, description,
                                              link, source, comments)
                        # reporter(reply, 10)
                        st.text(reply)


def view_assignments(ass_tab2):
    with ass_tab2:
        df = get_table(Assignment)
        df_orig = pd.DataFrame()
        if isinstance(df, pd.DataFrame):
            df_orig = df.copy()
            df_orig = df_orig.set_index('id')
        else:
            st.warning(df)
            st.stop()

        df.project = df.project.str.upper()
        df.set_draw = df.set_draw.str.upper()

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

        real_dir = set(df.in_out)
        id_val = id_col.text_input('ID')
        proj_val = proj_col.text_input('Project')
        set_val = set_col.text_input('Set of Drawings / Unit')
        spec_val = spec_col.selectbox("Speciality", real_spec, disabled=st.session_state.spec_disable)

        dir_val = dir_col.radio("In-Out", real_dir, horizontal=True)
        df_orig = df_orig[df_orig.in_out == dir_val]

        df_temp = df_orig.copy()
        df_temp.project = df_temp.project.str.upper()
        df_temp.set_draw = df_temp.set_draw.str.upper()

        if len(id_val):
            df_orig = df_orig[df_orig.index == int(id_val)]
        else:
            if not st.session_state.spec_disable:
                df_orig = df_orig.loc[df_orig.speciality == spec_val]
            if proj_val:
                df_orig = df_orig.loc[df_temp.project.str.contains(proj_val.upper())]
            if set_val:
                df_orig = df_orig.loc[df_temp.set_draw.str.contains(set_val.upper())]
        st.write(f"{len(df_orig)} records found")
        st.experimental_data_editor(df_orig, use_container_width=True)
