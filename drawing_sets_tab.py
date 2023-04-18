# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import streamlit as st
from admin_tools import get_list_index
from pre_sets import specialities, sod_revisions, sod_statuses, stages
from projects import get_trans_nums, update_sod, add_sod
from pre_sets import reporter

def show_sets():
    st.session_state.w.empty()
    with st.session_state.w.container():
        if st.session_state.edit_sod['project']:

            cur_sod = st.session_state.edit_sod
            proj = cur_sod.get('project', None)
            my_or_all = cur_sod.get('my_all', None)
            sod = cur_sod.get('project', None)

        else:
            proj = None
            my_or_all = None
            sod = None

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

        empty1, content, empty2 = st.columns([1, 30, 1])
        with empty1:
            st.empty()
        with empty2:
            st.empty()

        with content:
            st.title(':orange[Drawing Sets]')

            ds_left, lc, ds_center, cr, ds_rigth = st.columns([5, 6, 4, 5, 5])
            ds_center.text('')

            my_all = ds_center.radio("Select the Option", ["My Units", 'All Units'],
                                     index=get_list_index(["My Units", 'All Units'], my_or_all),
                                     horizontal=True, label_visibility='collapsed')

            u_df = st.session_state.adb['users']
            proj_df = st.session_state.adb['project']
            df = st.session_state.adb['sod']

            if my_all == "My Units":
                user_login = st.session_state.user
                user_id = u_df.loc[u_df.login == user_login].index.values[0]
                df = df[(df.coord_id == user_id) | (df.perf_id == user_id)]


            df['unit_id'] = df.index
            df = df.set_index('project_id').join(proj_df['short_name'])
            df = df.set_index('coord_id').join(u_df['login'])

            df = df.set_index('perf_id').join(u_df['login'], lsuffix='_coord', rsuffix='_perf')

            df.rename(columns={'short_name': 'project', 'set_name': 'unit',
                               'login_coord': 'coordinator', 'login_perf': 'performer',
                               'current_status': 'status', 'trans_num': 'transmittal'}, inplace=True)
            #
            df = df[['unit_id', 'project', 'unit', 'coordinator', 'performer', 'stage', 'revision', 'start_date',
                     'status', 'request_date', 'transmittal', 'trans_date', 'notes']]

            proj_list = df['project'].drop_duplicates()

            ds_left.subheader(f"{my_all}: {len(df)}")

            ds_rigth.text('')
            units_ch_b = ds_rigth.checkbox("Show Units Table")

            if units_ch_b:
                st.experimental_data_editor(df.set_index('unit_id'), use_container_width=True)

            proj_col, unit_col = st.columns(2, gap='medium')

            if st.session_state.edit_sod['unit'] and st.session_state.edit_sod['project']:

                units_list = df[df.project == st.session_state.edit_sod['project']]['unit']

                df_edit = df.loc[(df.unit == st.session_state.edit_sod['unit'])
                                 & (df.project == st.session_state.edit_sod['project'])]

                unit_selected = unit_col.selectbox("Unit for Search", units_list, index=get_list_index(units_list, sod))
                proj_selected = proj_col.selectbox("Project for Search", proj_list, index=get_list_index(proj_list, proj))

            else:
                ## SELECT PROJECT
                proj_selected = proj_col.selectbox("Project for Search", proj_list, index=get_list_index(proj_list, proj))

                units_list = df[df.project == proj_selected]['unit']

                # SELECT SOD
                unit_selected = unit_col.selectbox("Unit for Search", units_list, index=get_list_index(units_list, sod))


                df_edit = df.loc[(df.unit == unit_selected) & (df.project == proj_selected)]

            st.divider()
            st.subheader(f"Project: :red[{proj_selected}]. Unit: :red[{unit_selected}]")
            st.experimental_data_editor(df_edit[['unit_id', 'coordinator', 'performer', 'stage', 'revision', 'start_date',
                                                 'status', 'transmittal', 'trans_date', 'notes']].set_index('unit_id'),
                                        use_container_width=True)


            if len(df_edit) == 1:
                unit_id = df_edit.unit_id.values[0]
            else:
                st.warning("Duplicated Units. Please fix it")
                st.stop()

            if st.button('Edit Details'):
                st.session_state.edit_sod['coordinator'] = df_edit.coordinator.values[0]
                st.session_state.edit_sod['performer'] = df_edit.performer.values[0]
                st.session_state.edit_sod['revision'] = df_edit.revision.values[0]
                st.session_state.edit_sod['status'] = df_edit.status.values[0]
                st.session_state.edit_sod['notes'] = df_edit.notes.values[0]
                st.session_state.edit_sod['project'] = proj_selected
                st.session_state.edit_sod['unit'] = unit_selected
                st.session_state.edit_sod['unit_id'] = unit_id
                st.session_state.edit_sod['my_all'] = my_all
                st.session_state.edit_sod['state'] = True

                st.experimental_rerun()

            st.divider()

            # units_tasks = get_own_tasks(unit_id) ###
            task_df = st.session_state.adb['task']

            spec_df = st.session_state.adb['speciality']

            units_tasks = task_df[task_df.s_o_d == unit_id]  # .tolist()

            units_tasks['task_id'] = units_tasks.index

            units_tasks = units_tasks.set_index("speciality").join(spec_df)

            units_tasks.reset_index(inplace=True)

            units_tasks['speciality'] = units_tasks.abbrev

            # if isinstance(units_tasks, str):
            #     if units_tasks == "Empty Table":
            #         st.warning('No Tasks Available for selected Unit')
            #         st.stop()
            #
            # if not isinstance(units_tasks, pd.DataFrame):
            #     st.stop()

            task_col, in_out_col, quant_col = st.columns([9, 2, 2])

            with in_out_col:
                in_out_radio = st.radio("Select Incoming / Outgoing", ('In', 'Out'), horizontal=True)

            if in_out_radio == "In":
                units_tasks = units_tasks[(units_tasks.in_out == 'Входящие') | (units_tasks.in_out == 'In')]
            else:
                units_tasks = units_tasks[(units_tasks.in_out == 'Исходящие') | (units_tasks.in_out == 'Out')]

            with task_col:
                st.subheader(f"Available Tasks")

            with quant_col:
                st.write("")
                st.write("")
                st.write(f'Quantity: {len(units_tasks)}')

            units_tasks = units_tasks.sort_values(by=['speciality', 'date'], ascending=[True, False])
            st.experimental_data_editor(units_tasks[['stage', 'speciality', 'date', 'description', 'link', 'source',
                                                     'comment', 'backup_copy', 'coord_log', 'perf_log', 'added_by',
                                                     'task_id']].set_index('task_id'),
                                        use_container_width=True)
            st.divider()

            aval_spec = list(units_tasks.speciality.drop_duplicates())

            spec_dual = specialities  # (*specialities, *specialities_rus)
            not_aval_spec = []

            for i in spec_dual:
                if i not in aval_spec:
                    not_aval_spec.append(i)

            not_aval_df = pd.DataFrame(not_aval_spec, columns=['speciality'])
            not_aval_df['request'] = False
            not_aval_df = not_aval_df.set_index('speciality')

            if in_out_radio == "In":
                req_checkbox = st.checkbox('Create Draft for not available Tasks')
                if req_checkbox:
                    st.subheader("Not available Tasks for Specialities. Here you can create request for assignments")
                    not_aval_col, empty_col, but_col, request_col = st.columns([4, 1, 3, 10])
                    with not_aval_col:
                        request_df = st.experimental_data_editor(not_aval_df, use_container_width=True, height=600,
                                                                 num_rows='fixed', key='tasks', disabled=False)

                    with but_col:
                        request_but = st.button('Create Request')

                    with request_col:
                        if request_but:
                            if len(request_df[request_df.request].index):
                                st.subheader("Draft of e-mail")
                                st.markdown("""<u>Тема:</u>""", unsafe_allow_html=True)
                                st.markdown(f"**Недостающие задания для {proj_selected}: {unit_selected}**")
                                st.markdown("""<u>Тело:</u>""", unsafe_allow_html=True)
                                st.markdown(f"""
                                В ЭлектроОтделе сейчас в разработке комплект чертежей:
                                **{proj_selected}: {unit_selected}**.
                                В настоящее время отсутствуют задания по специальностям:
                                **{', '.join(request_df[request_df.request == True].index.values)}**.
                                Просим сообщить о необходимости задания и его сроке выдачи.
                                """)
                                st.write('')
                                st.markdown("""<u>Subject:</u>""", unsafe_allow_html=True)
                                st.markdown(
                                    f"**Not available assignments for {proj_selected}: {unit_selected}**")
                                st.markdown("""<u>Body:</u>""", unsafe_allow_html=True)
                                st.markdown(f"""
                                Currently Electrical Department is developing:
                                **{proj_selected}: {unit_selected}**.
                                For now we haven't assignments from:
                                **{', '.join(request_df[request_df.request == True].index.values)}**.
                                Kindly ask you to inform about a necessity of assignment and it's issue date.
                                """)
                            else:
                                st.warning("Select specialities for request")


def edit_sets():
    st.session_state.w.empty()
    with st.session_state.w.container():
        cur_sod = st.session_state.edit_sod

        empty_sets_1, content_sets, empty_sets_2 = st.columns([3, 5, 3])
        with empty_sets_1:
            st.empty()
        with empty_sets_2:
            st.empty()

        with content_sets:

            # all_logins = get_all_logins()
            all_logins = st.session_state.adb['users'].login.tolist()

            with st.form('upd_set_detail'):
                st.subheader("Edit Details")
                st.subheader(f"Project: :red[{cur_sod.get('project', '!!!')}]")
                st.subheader(f"Unit: :red[{cur_sod.get('unit', '!!!')}]")
                left_sod, center_sod, right_sod = st.columns([7, 1, 7])
                left_sod.subheader("")
                left_sod.write("")
                upd_trans_chb = right_sod.checkbox('Add Transmittal')
                with left_sod:
                    coord = st.selectbox("Coordinator", all_logins,
                                         index=get_list_index(all_logins, cur_sod.get('coordinator', '!!!')))

                    perf = st.selectbox("Performer", all_logins,
                                        index=get_list_index(all_logins, cur_sod.get('performer', '!!!')))

                    rev = st.selectbox("Revision", sod_revisions,
                                       index=get_list_index(sod_revisions, cur_sod.get('revision', '!!!')))

                    status = st.selectbox('Status', sod_statuses,
                                          index=get_list_index(sod_statuses, cur_sod.get('status', '!!!')))

                with right_sod:
                    trans_list = get_trans_nums(cur_sod.get('project', '!!!'))

                    if not isinstance(trans_list, list):
                        st.warning(trans_list)
                        st.stop()

                    trans_num = st.selectbox('New Transmittal Number', trans_list)
                    trans_date = st.date_input('New Transmittal Date')
                    notes = st.text_area("Notes (don't delete, just add to previous)",
                                         value=cur_sod.get('notes', '!!!'), height=125)

                set_upd_but = st.form_submit_button("Update in DB", use_container_width=True, type="primary")

            if set_upd_but:
                reply = update_sod(cur_sod.get('unit_id', '!!!'), coord, perf, rev, status, trans_num,
                                   trans_date, notes, upd_trans_chb)

                if reply is True:
                    reporter("Updated!")

                    unit_id = st.session_state.edit_sod['unit_id']

                    sod_df = st.session_state.adb['sod']

                    sod_df.at[unit_id, 'coord_id'] = coord
                    sod_df.at[unit_id, 'perf_id'] = perf
                    sod_df.at[unit_id, 'revision'] = rev
                    sod_df.at[unit_id, 'current_status'] = status
                    if upd_trans_chb:
                        sod_df.at[unit_id, 'trans_num'] = trans_num
                        sod_df.at[unit_id, 'trans_date'] = trans_date
                    sod_df.at[unit_id, 'notes'] = notes
                    st.session_state.adb['sod'] = sod_df

                else:
                    reporter(reply, 3)

                st.session_state.edit_sod['state'] = False
                st.session_state.edit_sod['unit'] = None
                st.session_state.edit_sod['project'] = None
                st.experimental_rerun()

            if st.button("Escape", use_container_width=True):
                st.session_state.edit_sod['state'] = False
                st.session_state.edit_sod['unit'] = None
                st.session_state.edit_sod['project'] = None
                st.experimental_rerun()


def drawing_sets():
    # st.write(st.session_state.edit_sod)
    if 'edit_sod' in st.session_state:
        if st.session_state.edit_sod['state']:
            edit_sets()
        else:
            show_sets()

def create_new_unit():
    st.session_state.w.empty()
    with st.session_state.w.container():
        empty_sets_1, content_sets, empty_sets_2 = st.columns([1, 9, 1])
        with empty_sets_1:
            st.empty()
        with empty_sets_2:
            st.empty()

        with content_sets:
            st.title(':orange[Create new Set of Drawings / Unit]')

            with st.form('new_sod'):
                proj_short = st.selectbox('Select a Project', st.session_state.proj_names)
                set_name = st.text_input("Enter the Name for new Set of Drawings / Unit").strip()
                stage = st.radio("Select the Stage", stages, horizontal=True)
                coordinator = st.selectbox("Coordinator", st.session_state.appl_logins)
                performer = st.selectbox("Performer", st.session_state.appl_logins)
                set_start_date = st.date_input('Start Date', datetime.date.today(), key="new_set_time_picker")
                status = st.select_slider("Select the Current Status", sod_statuses, value='0%')
                notes = st.text_area("Add Notes").strip()
                create_sod_but = st.form_submit_button("Create", use_container_width=True)

            if create_sod_but:
                reply = add_sod(proj_short, set_name, stage, status, set_start_date, coordinator, performer, notes)
                reporter(reply)

                if "ERROR" not in reply.upper():
                    sod_df = st.session_state.adb['sod']
                    u_df = st.session_state.adb['users']
                    proj_df = st.session_state.adb['project']

                    next_id = sod_df.index.max() + 1

                    project_id = proj_df.query('short_name == @proj_short').index.values[0]
                    coord_id = u_df.query('login == @coordinator').index.values[0]
                    perf_id = u_df.query('login == @performer').index.values[0]

                    st.session_state.adb['sod'] = sod_df.append(
                        {'id': next_id, 'project_id': project_id, 'set_name': set_name, 'coord_id': coord_id,
                         'perf_id': perf_id, 'stage': stage, 'revision': "R1", 'current_status': status,
                         'notes': notes, 'aux': f"{st.session_state.user}: {str(datetime.datetime.now())[:-10]}"
                         }
                    )

