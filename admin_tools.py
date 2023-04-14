# -*- coding: utf-8 -*-

import datetime
import pandas as pd
import streamlit as st
from models import Project, Task, VisitLog, SOD, Users, Trans, Speciality
from pre_sets import proj_statuses, reporter, stages, sod_statuses, sod_revisions
from projects import create_project, get_table, update_projects, add_sod, get_sets_names, get_set_to_edit, \
    get_trans_nums
from users import get_logins_for_current, get_all_logins


def get_list_index(a_list: list, elem: str) -> int:
    try:
        ind = a_list.index(elem)
        return ind
    except:
        return 0

def manage_projects():
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
            with st.form("create_project", clear_on_submit=False):
                proj_short = st.text_input('Project Name - short')
                proj_full = st.text_area('Project Name - full')
                responsible_el = st.selectbox('Responsible Person', get_logins_for_current())
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

                reporter(reply)
                # st.session_state.preview_proj_stat = False

        with proj_tab2:
            proj_to_edit_list = st.multiselect('Select Projects to Edit', st.session_state.proj_names)

            if proj_to_edit_list:
                proj_df = get_table(Project)

                if not isinstance(proj_df, pd.DataFrame):
                    st.warning(proj_df)
                    st.stop()

                # proj_df = proj_df.set_index('short_name')
                proj_df = proj_df[proj_df.short_name.isin(proj_to_edit_list)]
                proj_df['to_del'] = False
                proj_df['edit'] = False

                # st.write(proj_df)
                edited_proj_df = st.experimental_data_editor(proj_df)

                if st.button("Update in DataBase", key="update_project"):
                    proj_len_edited = len(edited_proj_df[edited_proj_df.edit])
                    if proj_len_edited:
                        reply = update_projects(edited_proj_df)
                        reporter(reply)
                    else:
                        reporter("No selection to Edit")

        with viewer_tab:
            # tab_list = get_tab_names()
            tab_name = st.radio("Select the Table for view", (
                Task, Project, SOD, Users, VisitLog, Trans, Speciality), horizontal=True)

            df = get_table(tab_name)
            if isinstance(df, pd.DataFrame):
                st.info(f'Records Q-ty: {len(df)}')
                # st.write(df)
                st.experimental_data_editor(df, use_container_width=True)
            else:
                st.warning('No records found')


st.cache_data(ttl=600)
def manage_sets():
    empty_sets_1, content_sets, empty_sets_2 = st.columns([1, 9, 1])
    with empty_sets_1:
        st.empty()
    with empty_sets_2:
        st.empty()

    with content_sets:
        st.title(':orange[Manage Drawings Sets]')
        sets_edit, sets_create = st.tabs(['Edit Existing Set of Drawings', 'Create Set of Drawings'])
        with sets_create:

            st.subheader("Create Set of Drawings")

            with st.form('new_sod'):
                proj_short = st.selectbox('Select a Project', st.session_state.proj_names)
                set_name = st.text_input("Enter the Name for new Set of Drawings / Unit").strip()
                stage = st.radio("Select the Stage", stages, horizontal=True)
                coordinator = st.selectbox("Coordinator", st.session_state.registered_logins)
                performer = st.selectbox("Performer", st.session_state.registered_logins)
                set_start_date = st.date_input('Start Date', datetime.date.today(), key="new_set_time_picker")
                status = st.select_slider("Select the Current Status", sod_statuses, value='0%')
                notes = st.text_area("Add Notes").strip()
                create_sod_but = st.form_submit_button("Create",use_container_width=True)

            if create_sod_but:
                reply = add_sod(proj_short, set_name, stage, status, set_start_date, coordinator, performer, notes)
                reporter(reply)

        with sets_edit:
            st.subheader('Edit Existing Set of Drawings')
            proj_for_sets_edit = st.selectbox('Select Projects for Edited Unit / Set', st.session_state.proj_names,)

            sets_list = get_sets_names(proj_for_sets_edit)

            if isinstance(sets_list, list):
                set_to_edit = st.selectbox('Select Unit / Set of Drawings', sets_list)
            else:
                reporter(sets_list)
                st.stop()

            sets_tuple = get_set_to_edit(proj_for_sets_edit, set_to_edit)

            if not isinstance(sets_tuple, tuple):
                st.warning(sets_tuple)
                st.stop()
            all_logins = get_all_logins()
            # st.write(sets_tuple)


            with st.form('upd_set_detail'):
                left_sod, center_sod, right_sod = st.columns([7, 1, 7])
                left_sod.subheader(f'Update Information for Selected Unit / Set of Drawings')
                right_sod.write("")
                upd_trans_chb = right_sod.checkbox('Update Transmittal')
                with left_sod:
                    coord = st.selectbox("Coordinator", all_logins,
                                         index=get_list_index(all_logins, sets_tuple[2]))

                    perf = st.selectbox("Performer", all_logins,
                                        index=get_list_index(all_logins, sets_tuple[3]))

                    rev = st.selectbox("Revision", sod_revisions,
                                       index=get_list_index(sod_revisions, sets_tuple[5]))

                    status = st.selectbox('Status', sod_statuses,
                                          index=get_list_index(sod_statuses, sets_tuple[6]))

                with right_sod:

                    trans_list = get_trans_nums(proj_for_sets_edit)

                    if not isinstance(trans_list, list):
                        st.warning(trans_list)
                        st.stop()

                    trans_num = st.selectbox('New Transmittal Number', trans_list)
                    trans_date = st.date_input('New Transmittal Date')
                    notes = st.text_area('Notes', value=sets_tuple[10], height=120)

                set_upd_but = st.form_submit_button("Update in DB", use_container_width=True)

                if set_upd_but:
                    if upd_trans_chb:
                        st.write(
                            coord,
                            perf,
                            rev,
                            status,
                            trans_num,
                            trans_date,
                            notes,
                        )
                    else:
                        st.write(
                            coord,
                            perf,
                            rev,
                            status,
                            notes,
                        )



