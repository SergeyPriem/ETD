# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import streamlit as st
from admin_tools import get_list_index
from models import SOD
from send_emails import send_mail
from utilities import sod_revisions, sod_statuses, stages
from projects import update_sod, add_sod, get_table, update_unit_name_stage
from users import err_handler


def drawing_sets():
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
        st.divider()

        ds_left, lc, ds_center, cr, ds_rigth = st.columns([5, 6, 4, 5, 5])
        ds_center.text('')

        my_all = ds_center.radio("Select the Option", ["My Units", 'All Units'],
                                 horizontal=True, label_visibility='collapsed')

        u_df = st.session_state.adb['users']
        proj_df = st.session_state.adb['project']
        df = st.session_state.adb['sod']

        if my_all == "My Units":
            user_login = st.session_state.user
            user_id = u_df.loc[u_df.login == user_login].index.to_numpy()[0]
            df = df[(df.coord_id == user_id) | (df.perf_id == user_id)]

        df.loc[:, 'unit_id'] = df.index
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

        proj_selected = proj_col.selectbox("Project for Search", proj_list)

        units_list = df[df.project == proj_selected]['unit']

        unit_selected = unit_col.selectbox("Unit for Search", units_list)

        df_edit = df.loc[(df.unit == unit_selected) & (df.project == proj_selected)]

        st.divider()
        st.subheader(f"Project: :red[{proj_selected}]")
        st.subheader(f"Unit: :red[{unit_selected}]")

        if len(df_edit) == 1:
            unit_id = df_edit.unit_id.to_numpy()[0]
        else:
            st.warning("Units not available")
            st.stop()

        all_logins = st.session_state.adb['users'].login.tolist()

        trans_df = st.session_state.adb['trans']

        proj_df = st.session_state.adb['project']

        proj_id = proj_df[proj_df.short_name == proj_selected].index.to_numpy()[0]

        try:
            trans_list = trans_df.loc[trans_df.project == proj_id, 'trans_num'].tolist()
            # st.write(trans_list)
        except Exception as e:
            st.write(err_handler(e))
            st.stop()

        # if st.session_state.user == 'sergey.priemshiy':
        #     st.write(proj_df)
        #     st.write(proj_id)
        #     if trans_list:
        #         st.write(trans_list)
        #     st.write(trans_df)

        trans_list.insert(0, 'Not required')

        with st.form("edit-unit_details"):
            l_c, r_c = st.columns(2, gap='medium')
            coord = l_c.selectbox("Coordinator", all_logins,
                                  index=get_list_index(all_logins, df_edit.coordinator.to_numpy()[0]))
            perf = l_c.selectbox("Performer", all_logins,
                                 index=get_list_index(all_logins, df_edit.performer.to_numpy()[0]))
            rev = l_c.selectbox("Revision", sod_revisions,
                                index=get_list_index(sod_revisions, df_edit.revision.to_numpy()[0]))
            status = l_c.selectbox('Status', sod_statuses,
                                   index=get_list_index(sod_statuses, df_edit.status.to_numpy()[0]))

            r_c.text('')
            r_c.text('')
            upd_trans_chb = r_c.checkbox("Add Transmittal")
            r_c.text('')
            trans_num = r_c.selectbox("New Transmittal Number", trans_list)
            notes = r_c.text_area("Notes (don't delete, just add to previous)",
                                  value=df_edit.notes.to_numpy()[0], max_chars=1500, height=127)
            upd_unit_but = st.form_submit_button("Update Unit Details")

        if upd_unit_but:
            if upd_trans_chb and trans_num == "Not required":
                st.warning("Select right Transmittal Number")
                st.stop()
            else:
                reply = update_sod(unit_id, coord, perf, rev, status, trans_num, notes, upd_trans_chb)

            if reply == 200:
                st.success("Updated!")
                st.session_state.adb['sod'] = get_table(SOD)

            else:
                st.warning(reply)

        st.write("")

        # units_tasks = get_own_tasks(unit_id) ###
        task_df = st.session_state.adb['task']

        spec_df = st.session_state.adb['speciality']

        units_tasks = task_df[task_df.s_o_d == unit_id]  # .tolist()

        units_tasks['task_id'] = units_tasks.index

        units_tasks = units_tasks.set_index("speciality").join(spec_df)

        units_tasks.reset_index(inplace=True)

        units_tasks['speciality'] = units_tasks.abbrev

        task_col, in_out_col, quant_col = st.columns([9, 2, 2])

        with in_out_col:
            in_out_radio = st.radio("Select Incoming / Outgoing", ('In', 'Out'), horizontal=True)

        if in_out_radio == "In":
            units_tasks = units_tasks[(units_tasks.in_out == 'In')]
        else:
            units_tasks = units_tasks[(units_tasks.in_out == 'Out')]

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

        spec_dual = st.session_state.spec  # (*specialities, *specialities_rus)
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





def manage_units():
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

    empty_sets_1, content_sets, empty_sets_2 = st.columns([1, 9, 1])
    with empty_sets_1:
        st.empty()
    with empty_sets_2:
        st.empty()

    with content_sets:
        st.title(':orange[Manage Units]')

        tab_create, tab_update = st.tabs(['Create New Unit', 'Edit Existing Unit'])

        with tab_create:
            with st.form('new_sod'):
                proj_short = st.selectbox('Select a Project', st.session_state.proj_names)
                set_name = st.text_input("Enter the Name for new Set of Drawings / Unit", max_chars=200).strip()
                stage = st.radio("Select the Stage", stages, horizontal=True)
                coordinator = st.selectbox("Coordinator", st.session_state.appl_logins)
                performer = st.selectbox("Performer", st.session_state.appl_logins)
                set_start_date = st.date_input('Start Date', datetime.date.today(), key="new_set_time_picker")
                status = st.select_slider("Select the Current Status", sod_statuses, value='0%')
                notes = st.text_area("Add Notes", max_chars=500).strip()
                create_sod_but = st.form_submit_button("Create", use_container_width=True)

            if create_sod_but:
                reply = add_sod(proj_short, set_name, stage, status, set_start_date, coordinator, performer, notes)
                if reply == 201:
                    st.success(f"New Set '{set_name}' for Project '{proj_short}' is added to DataBase")
                    # sod_df = st.session_state.adb['sod']
                    # u_df = st.session_state.adb['users']
                    # proj_df = st.session_state.adb['project']
                    #
                    # next_id = sod_df.index.max() + 1
                    #
                    # project_id = proj_df.query('short_name == @proj_short').index.to_numpy()[0]
                    # coord_id = u_df.query('login == @coordinator').index.to_numpy()[0]
                    # perf_id = u_df.query('login == @performer').index.to_numpy()[0]
                    #
                    # dict_df = pd.DataFrame(
                    #     [
                    #         {
                    #             'id': next_id, 'project_id': project_id, 'set_name': set_name, 'coord_id': coord_id,
                    #             'perf_id': perf_id, 'stage': stage, 'revision': "R1", 'current_status': status,
                    #             'notes': notes, 'aux': f"{st.session_state.user}: {str(datetime.datetime.now())[:-10]}"
                    #         }
                    #     ]
                    # )
                    #
                    # st.session_state.adb['sod'] = sod_df.append(dict_df)
                    st.session_state.adb['sod'] = get_table(SOD)

                else:
                    st.warning(reply)

        with tab_update:
            l_c, r_c = st.columns(2, gap='medium')

            proj_short = l_c.selectbox('Select Project', st.session_state.proj_names)

            proj_df = st.session_state.adb['project']
            proj_id = proj_df.loc[proj_df.short_name == proj_short].index.to_numpy()[0]

            sod_df = st.session_state.adb['sod']

            u_list = sod_df.loc[sod_df.project_id == proj_id, 'set_name'].tolist()



            unit_name = r_c.selectbox('Select Unit', u_list)

            current_stage = sod_df.loc[sod_df.set_name == unit_name, 'stage'].to_numpy()[0]

            with st.form('update_unit'):
                lc, rc = st.columns(2, gap='medium')
                new_unit_name = lc.text_input('New Name for Unit', value=unit_name)
                new_stage = rc.selectbox("New Stage for Unit", stages, index=get_list_index(stages, current_stage))

                upd_unit_but = st.form_submit_button("Update Details for Unit", use_container_width=True)

            if upd_unit_but:
                u_id = sod_df.loc[(sod_df.project_id == proj_id) & (sod_df.set_name == unit_name)].index.to_numpy()[0]
                reply = update_unit_name_stage(u_id, new_unit_name, new_stage)

                l_rep, r_rep = st.columns(2, gap='medium')

                st.write(reply)

                if reply['status'] == 201:
                    st.session_state.adb['sod'] = reply['sod']

                    l_rep.success('Unit Details Updated')

                    subj = f"{proj_short}: {unit_name}. Changes"

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
                              <b>{proj_short}</b>
                            </h5>
                            <p>Some data for the Project were updated</p>
                            <br>
                            <p>Project short name: <b>{proj_short}</b></p>
                            <p>Old Unit name: <b>{unit_name}</b></p>
                            <p>New Unit Name: <b>{new_unit_name}</b></p>
                            <p>Old Project Stage: <b>{current_stage}</b></p>
                            <p>New Project Stage: <b>{new_stage}</b></p>
                            <p>
                            <hr>
                            Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """

                    u_df = st.session_state.adb['users']

                    receiver = u_df[sod_df[u_id, 'coord_id'].to_numpy()[0], 'email'].to_numpy()[0]
                    cc_rec = u_df[sod_df[u_id, 'perf_id'].to_numpy()[0], 'email'].to_numpy()[0]

                    if receiver == cc_rec:
                        cc_rec = 'sergey.priemshiy@uzliti-en.com'

                    reply2 = send_mail(receiver, cc_rec, subj, html)

                    if reply2 == 200:
                        r_rep.success(f'Informational e-mail was sent to {receiver}, {cc_rec}')
                else:
                    st.warning(reply['err_descr'])
