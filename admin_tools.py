# -*- coding: utf-8 -*-

import datetime

import pandas as pd
import streamlit as st

from models import Appl_user, User, Project, Assignment, Contact, Visit_log, Set_draw
from pre_sets import proj_statuses, reporter, stages, sod_statuses, add_logo
from projects_db import create_project, get_projects_names, get_table, update_projects, create_set, get_sets_names, \
    get_sets_to_edit, update_sets
from users_db import get_appl_emails


def manage_projects():
    add_logo()
    empty_proj_1, content_proj, empty_proj_2 = st.columns([1, 9, 1])
    with empty_proj_1:
        st.empty()
    with empty_proj_2:
        st.empty()

    with content_proj:
        st.title(':orange[Manage Projects]')
        proj_tab1, proj_tab2, viewer_tab = st.tabs(['Create Project', 'Edit Existing Project', 'View Tables'])

        with proj_tab1:
            # st.subheader('Add New Project')
            proj_short = st.text_input('Project Name - short')
            proj_full = st.text_area('Project Name - full')
            responsible_el = st.selectbox('Responsible Person', get_appl_emails())
            proj_status = st.radio('Project Status', proj_statuses, horizontal=True)
            client = st.text_input('Client')
            proj_tech_ass = st.text_area('Link for Technical Assignment')
            proj_tech_conditions = st.text_area('Link for Technical Conditions')
            proj_surveys = st.text_area('Link for Technical Surveys')
            proj_mdr = st.text_area('Link for MDR')
            proj_man = st.text_input('Project Manager')
            proj_notes = st.text_area('Notes')
            proj_preview_col, proj_create_col = st.columns([1, 1])

            with proj_preview_col:
                preview_checkbox = st.checkbox('Preview Project',
                                               value=st.session_state.preview_proj_stat)
            with proj_create_col:
                create_proj_button = st.button('Create Project', use_container_width=True,
                                               disabled=not preview_checkbox)
            if preview_checkbox:
                st.write(f"""
                Short Name: **:blue[{proj_short}]**
                Full Name: **:blue[{proj_full}]**
                Responsible: **:blue[{responsible_el}]**
                Status: **:blue[{proj_status}]**
                Client: **:blue[{client}]**
                Link for Technical Assignment: **:blue[{proj_tech_ass}]**
                Link for Technical Conditions: **:blue[{proj_tech_conditions}]**
                Link for Technical Surveys: **:blue[{proj_surveys}]**
                Link for MDR: **:blue[{proj_mdr}]**
                Project Manager: **:blue[{proj_man}]**
                Notes: **:blue[{proj_notes}]**
                """)

            if create_proj_button:
                reply = create_project(proj_short, proj_full, client, proj_man, responsible_el,
                                       proj_status, proj_tech_ass, proj_tech_conditions,
                                       proj_surveys, proj_mdr, proj_notes)

                reporter(reply, 3)
                st.session_state.preview_proj_stat = False

        with proj_tab2:
            proj_to_edit_list = st.multiselect('Select Projects to Edit', get_projects_names())
            if proj_to_edit_list:

                proj_df = get_table('project')

                if not isinstance(proj_df, pd.DataFrame):
                    st.warning(proj_df)
                    st.stop()

                proj_df = proj_df.set_index('id')
                proj_df = proj_df[proj_df.short_name.isin(proj_to_edit_list)]
                proj_df['to_del'] = False
                proj_df['edit'] = False

                st.write(proj_df)
                edited_proj_df = st.experimental_data_editor(proj_df)

                if st.button("Update in DataBase", key="update_project"):
                    proj_len_edited = len(edited_proj_df[edited_proj_df.edit])
                    if proj_len_edited:
                        reply = update_projects(edited_proj_df)
                        reporter(reply, 3)
                    else:
                        reporter("No selection to Edit", 3)

        with viewer_tab:
            # tab_list = get_tab_names()
            tab_name = st.radio("Select the Table for view", (
                Assignment, Appl_user, Contact, Project, Set_draw, Visit_log, User,), horizontal=True)

            df = get_table(tab_name)
            st.info(f'Records Q-ty: {len(df)}')
            st.write(df)


def manage_sets():
    add_logo()
    empty_sets_1, content_sets, empty_sets_2 = st.columns([1, 9, 1])
    with empty_sets_1:
        st.empty()
    with empty_sets_2:
        st.empty()

    with content_sets:
        st.title(':orange[Manage Drawings Sets]')
        sets_create, sets_edit = st.tabs(['Create Set of Drawings',
                                          'Edit Existing Set of Drawings'])
        with sets_create:

            st.subheader("Create Set of Drawings")
            proj_short = st.selectbox('Select a Project', get_projects_names())
            set_name = st.text_input("Enter the Name for new Set of Drawings / Unit")
            stage = st.radio("Select the Stage", stages, horizontal=True)
            colleagues = get_appl_emails()
            coordinator = st.selectbox("Coordinator", colleagues)
            performer = st.selectbox("Performer", colleagues)
            set_start_date = st.date_input('Start Date', datetime.date.today(), key="new_set_time_picker")
            status = st.select_slider("Select the Current Status", sod_statuses, value='0%')
            notes = st.text_area("Add Notes")

            if st.button("Create", key="create sod"):
                reply = create_set(proj_short, set_name, stage, coordinator, performer, status,
                                   set_start_date, notes)
                reporter(reply, 3)

        with sets_edit:
            st.subheader('Edit Existing Set of Drawings')
            proj_for_sets_edit = st.selectbox('Select Projects for Edited Unit / Set',
                                              get_projects_names(), )

            sets_list = get_sets_names(proj_for_sets_edit)

            if not isinstance(sets_list, list):
                reporter(sets_list, 3)
                st.stop()
            else:
                set_to_edit = st.selectbox('Select Unit / Set of Drawings', sets_list)

            sets_df = get_sets_to_edit(proj_for_sets_edit, set_to_edit)

            if not isinstance(sets_df, pd.DataFrame):
                st.warning(sets_df)
                st.stop()
            sets_df = sets_df.set_index('id')
            sets_df['to_del'] = False
            sets_df['edit'] = False
            edited_set_df = st.experimental_data_editor(sets_df, use_container_width=True)

            if st.button('Update in DataBase', key="update_set"):
                len_edited = len(edited_set_df[edited_set_df.edit])
                if len_edited:
                    reply = update_sets(edited_set_df)
                    reporter(reply, 3)
                else:
                    reporter("No selection to Edit", 3)


def table_viewer():

    table_dict = {
        'Applied Users': Appl_user,
        'Registered Users': User,
        'Projects': Project,
        'Assignments': Assignment,
        'Contacts': Contact,
        'Visit Log': Visit_log,
    }

    st.subheader('Table Viewer')
    db_names = st.radio('Select the DB table', ('appl_user', 'user', 'project', 'assignment'),
                        horizontal=True)

    db_table = table_dict.get(db_names)

    df = get_table(db_table)

    if isinstance(df, pd.DataFrame):
        st.write(df)
    else:
        st.warning(df)
