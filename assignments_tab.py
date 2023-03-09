# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from models import Assignment
from pre_sets import specialities
from projects_db import get_projects_names, get_table


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
        project = st.selectbox('Select the Project', get_projects_names())
        set_of_dr = st.multiselect('Select the Set Of Drawings / Unit',
                                   options=(1, 2, 3, 4, 5, 'Colored text, using the syntax :red[text to be colored], '
                                                           'where color needs to be replaced with any of the following '
                                                           'supported colors: blue, green, orange, red, violet', 7, 8,
                                            9,
                                            10))

        speciality = st.multiselect("Speciality", specialities)
        stage = st.radio('Stage', ('Detail Design', 'Basic Design', 'Feasibility Study',
                                   'Adaptation', 'As-built'), horizontal=True)
        proj_col1, proj_col2, proj_col3 = st.columns(3, gap="small")
        with proj_col1:
            direction = st.radio('Direction', ('IN', 'OUT'), horizontal=True)
        with proj_col2:
            date = st.date_input('Date')
        with proj_col3:
            st.text('')
            st.text('')
            anti_task = st.checkbox('Non-Assignment')

        description = st.text_input('Description of Assignment')
        path = st.text_input('Path')

        received = st.text_area('Received by:', value='Received by paper')

        if st.button('Preview'):
            st.markdown(f"""
            Project: **:blue[{project}]**
            <br>
            Set of Drawings / Unit: **:blue[{set_of_dr}]**
            <br>
            Speciality: **:blue[{speciality}]**
            """, unsafe_allow_html=True)
            if st.button('Add to DataBase'):
                st.write('DONE!')


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

        if len(id_val):
            df_orig = df_orig[df_orig.index == int(id_val)]
        else:
            if not st.session_state.spec_disable:
                df_orig = df_orig.loc[df_orig.speciality == spec_val]
            if proj_val:
                df_orig = df_orig.loc[df_orig.project.str.contains(proj_val.upper())]
            if set_val:
                df_orig = df_orig.loc[(df_orig.set_draw.str.contains(set_val.upper()))]
        st.write(f"{len(df_orig)} records found")
        st.experimental_data_editor(df_orig, use_container_width=True)
