# -*- coding: utf-8 -*-
import datetime
import pandas as pd
import streamlit as st
from admin_tools import get_list_index
from send_emails import send_mail
from utilities import REVISIONS, COMPLETION, STAGES, center_style, update_state, \
    title_with_help  # , make_long_delay, make_short_delay
from projects import update_sod, add_sod, update_unit_name_stage
from utilities import err_handler
from functools import lru_cache
from streamlit_extras.dataframe_explorer import dataframe_explorer


def drawing_sets():
    center_style()

    u_df = st.session_state.adb['users']
    proj_df = st.session_state.adb['project']
    sod_df = st.session_state.adb['sod']

    empty1, content, empty2 = st.columns([1, 30, 1])
    with empty1:
        st.empty()
    with empty2:
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('', help='На вкладке :orange[Drawings] отображаются комплекты чертежей, в которых Вы '
                         ':orange[Координатор или Разработчик] если выбрано My Units. '
                         'Выбрав All Units можно просмотреть все комплекты ЭлектроОтдела \n'
                         '---'
                         '\n'
                         'The :orange[Drawings] tab displays sets of drawings, in which you are the '
                         ':orange[Coordinator or Developer] (if My Units is selected). '
                         'By selecting All Units you can view all Units of Electrical Department.'
                )



    with content:
        # h_cont= """
        # <p style="text-align: center; color: #249ded;">На вкладке <b>Drawings</b> отображаются комплекты чертежей,
        # в которых Вы Координатор или Разработчик (если выбрано <b>My Units</b>). Выбрав <b>All Units</b> можно
        # просмотреть все комплекты ЭлектроОтдела</p>
        # <hr>
        # <p style="text-align: center; color: #249ded;">The <b>Drawings</b> tab displays sets of drawings,
        # in which you are the Coordinator or Developer (if <b>My Units</b> is selected). By selecting <b>All Units</b>
        # you can view all Units of Electrical Department.</p>
        # """
        #
        # title_with_help('Drawings', help_content=h_cont, ratio=36)


        st.title(":orange[Drawings]")
        st.divider()

        ds_left, lc, ds_center, cr, ds_right = st.columns([5, 6, 4, 5, 5])
        ds_center.text('')

        my_all = ds_center.radio("Select the Option", ["My Units", 'All Units'],
                                 horizontal=True, label_visibility='collapsed')

        if my_all == "My Units":
            user_id = st.session_state.user['id']
            sod_df = sod_df[(sod_df.coord_id == user_id) | (sod_df.perf_id == user_id)]

        sod_df.loc[:, 'unit_id'] = sod_df.index
        sod_df = sod_df.set_index('project_id').join(proj_df['short_name'])
        sod_df = sod_df.set_index('coord_id').join(u_df['login'])

        sod_df = sod_df.set_index('perf_id').join(u_df['login'], lsuffix='_coord', rsuffix='_perf')

        sod_df.rename(columns={'short_name': 'project', 'set_name': 'unit',
                               'login_coord': 'coordinator', 'login_perf': 'performer',
                               'current_status': 'status', 'trans_num': 'transmittal'}, inplace=True)
        #
        sod_df = sod_df[['unit_id', 'project', 'unit', 'coordinator', 'performer', 'stage', 'revision', 'start_date',
                         'status', 'request_date', 'transmittal', 'trans_date', 'notes']]

        proj_list = sod_df['project'].drop_duplicates()

        ds_left.subheader(f"{my_all}: {len(sod_df)}")

        ds_right.text('')
        units_ch_b = ds_right.checkbox("Show Units Table",
                                       help="Вывод таблицы всех Ваших Комплектов Чертежей"
                                            "---"
                                            "Display All Your Units"
                                       )

        if units_ch_b:
            st.data_editor(sod_df.set_index('unit_id'),
                                        key='show_units_for_drawings',
                                        use_container_width=True)

        proj_col, unit_col = st.columns(2, gap='medium')

        proj_selected = proj_col.selectbox("Project for Search", proj_list)

        units_list = sod_df[sod_df.project == proj_selected]['unit']

        unit_selected = unit_col.selectbox("Unit for Search", units_list)

        df_edit = sod_df.loc[(sod_df.unit == unit_selected) & (sod_df.project == proj_selected)]

        st.divider()
        st.subheader(f"Project: :blue[{proj_selected}]")
        st.subheader(f"Unit: :blue[{unit_selected}]")

        if len(df_edit) == 1:
            unit_id = df_edit.unit_id.to_numpy()[0]
        else:
            st.warning("Units not available")
            st.stop()

        all_logins = st.session_state.adb['users'].login.tolist()

        trans_df = st.session_state.adb['trans']

        proj_id = proj_df[proj_df.short_name == proj_selected].index.to_numpy()[0]

        try:
            trans_list = trans_df.loc[trans_df.project == proj_id, 'trans_num'].tolist()
        except Exception as e:
            st.write(err_handler(e))
            st.stop()

        old_coord = df_edit.coordinator.to_numpy()[0]
        old_perf = df_edit.performer.to_numpy()[0]

        old_rev = df_edit.revision.to_numpy()[0].split(" - ")

        try:
            if len(old_rev) != 2:
                old_rev = [old_rev[0], old_rev[0]]
        except:
            old_rev = ['R1', 'R1']

        old_status = df_edit.status.to_numpy()[0]
        old_notes = df_edit.notes.to_numpy()[0]
        old_trans = df_edit.transmittal.to_numpy()[0]
        trans_list.insert(0, 'Not required')

        with st.form("edit-unit_details"):
            l_c, c_c, r_c = st.columns(3, gap='medium')
            coord = l_c.selectbox("Coordinator", all_logins,
                                  index=get_list_index(all_logins, old_coord))
            perf = c_c.selectbox("Performer", all_logins,
                                 index=get_list_index(all_logins, old_perf))

            rev_min = l_c.selectbox("Revision (earliest)", REVISIONS,
                                    index=get_list_index(REVISIONS, old_rev[0]))

            rev_max = c_c.selectbox("Revision (most recent)", REVISIONS,
                                    index=get_list_index(REVISIONS, old_rev[1]))

            status = r_c.selectbox('Status', COMPLETION,
                                   index=get_list_index(COMPLETION, old_status))
            c_c.text('')
            c_c.text('')
            upd_trans_chb = c_c.checkbox("Add Transmittal")
            c_c.text('')

            trans_num = c_c.selectbox("New Transmittal Number", trans_list)

            notes = r_c.text_input("Notes (add new one)", max_chars=250)
            r_c.text_area("Notes (existing)", value=old_notes, max_chars=1500, height=126, disabled=True)

            if st.session_state.user['access_level'] in ['admin', 'super', 'dev']:
                check_disabled =False
                button_label = "Update Unit Details or Request for Update (if selected)"
            else:
                check_disabled =True
                button_label = "Update Unit Details"

            l_c.text_area(label="Transmittals' History", value=old_trans, height=126, disabled=True)

            l_c.text('')
            request_chb = l_c.checkbox('Request for Update', disabled=check_disabled)

            c_c.text('')
            upd_unit_but = c_c.form_submit_button(label=button_label, use_container_width=True)

        if upd_unit_but:

            rev = f"{rev_min} - {rev_max}"
            if not request_chb:
                if all([
                    old_coord == coord,
                    old_perf == perf,
                    old_rev == rev,
                    old_status == status,
                    old_notes == notes,
                    not upd_trans_chb
                ]):
                    st.warning('Nothing to Update')
                    st.stop()

                if upd_trans_chb and trans_num == "Not required":
                    st.warning("Select right Transmittal Number")
                    st.stop()

                reply = update_sod(unit_id, coord, perf, rev, status, trans_num, notes, upd_trans_chb)

                if reply['status'] == 201:

                    lc, cc, rc = st.columns([1, 2, 1], gap='medium')

                    lc.success("Updated!")

                    coord_email = reply['coord_email']
                    perf_email = reply['perf_email']

                    coord_report = f"{old_coord} >> {coord}" if old_coord != coord else "no changes"
                    perf_report = f"{old_perf} >> {perf}" if old_perf != perf else "no changes"
                    rev_report = f"{old_rev[0]} - {old_rev[1]} >> {rev}" if old_rev != rev else "no changes"
                    status_report = f"{old_status} >> {status}" if old_status != status else "no changes"
                    trans_report = trans_num if upd_trans_chb else "no changes"
                    notes_report = f'{old_notes} >> {notes}' if old_notes != notes else "no changes"

                    subj = f"{proj_selected}: {unit_selected}. Changes"

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
                              <b>{proj_selected}: {unit_selected}</b>
                            </h5>
                            <p>Some data for the Unit were updated</p>
                            <br>
                            <p>Coordinator: <b>{coord_report}</b></p>
                            <p>Performer: <b>{perf_report}</b></p>
                            <p>Revision: <b>{rev_report}</b></p>
                            <p>Status: <b>{status_report}</b></p>
                            <p>Transmittal: <b>{trans_report}</b></p>
                            <p>Notes: <b>{notes_report}</b></p>
                            <p>
                            <hr>
                            Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """
                    if st.session_state.user['login'] in coord_email:
                        coord_email = 'sergey.priemshiy@uzliti-en.com'

                    if st.session_state.user['login'] in perf_email:
                        perf_email = 'sergey.priemshiy@uzliti-en.com'

                    reply2 = send_mail(coord_email, perf_email, subj, html)

                    if reply2 == 200:
                        cc.success(f'Notifications were sent to {coord_email}, {perf_email}')

                        reply3 = update_state('sod')

                        if reply3 != 'Data is updated':
                            st.warning(reply3)
                            st.stop()

                        rc.text('')
                        rc.button('Close Report', key='close_unit_report', use_container_width=True)

                else:
                    st.warning(reply['err_descr'])

            if request_chb:

                coord_email = u_df.loc[u_df.login == coord, 'email'].to_numpy()[0]
                perf_email = u_df.loc[u_df.login == perf, 'email'].to_numpy()[0]

                if '@' not in coord_email:
                    st.warning("Can't get Coordinator email")
                    st.stop()

                if '@' not in perf_email:
                    st.warning("Can't get Performer email")
                    st.stop()

                subj = f"{proj_selected}: {unit_selected}. Request for Data Update"

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
                          <b>{proj_selected}: {unit_selected}</b>
                        </h5>
                        
                        <h3>
                            Please update Unit Details by link:
                              <a href="https://e-design.streamlit.app/">e-design.streamlit.app</a>
                        </h3>
                        
                        <p>
                        <hr>
                        Best regards, Administration 😎
                        </p>
                      </body>
                    </html>
                """

                reply2 = send_mail(coord_email, perf_email, subj, html)

                if reply2 == 200:
                    lc, rc = st.columns([2, 1], gap='medium')
                    lc.success(f'Notifications were sent to {coord_email}, {perf_email}')

                    rc.text('')
                    rc.button('Close Report', key='close_upd_sod2_report', use_container_width=True)

        st.write("")

        task_df = st.session_state.adb['task']

        spec_df = st.session_state.adb['speciality']

        units_tasks = task_df[task_df.s_o_d == unit_id]  # .tolist()

        units_tasks.loc[:,'task_id'] = units_tasks.index

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
        st.data_editor(units_tasks[['stage', 'speciality', 'date', 'description', 'link', 'source',
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
                    request_df = st.data_editor(not_aval_df, use_container_width=True,
                                                             height=600,
                                                             num_rows='fixed',
                                                             key='tasks',
                                                             disabled=False)

                with but_col:
                    request_chb = st.checkbox('Create Request')

                with request_col:
                    if request_chb:
                        if len(request_df[request_df.request].index):
                            st.subheader("Draft of e-mail")
                            st.markdown("""<u>Тема:</u>""", unsafe_allow_html=True)
                            st.markdown(f"**Недостающие задания для {proj_selected}: {unit_selected}**")
                            st.markdown("""<u>Тело:</u>""", unsafe_allow_html=True)
                            st.markdown(f"""
                            В ЭлектроОтделе сейчас в разработке комплект чертежей:
                            **{proj_selected}: {unit_selected}**.
                            В настоящее время отсутствуют задания по специальностям:
                            **{', '.join(request_df[request_df.request == True].index)}**.
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
                            **{', '.join(request_df[request_df.request == True].index)}**.
                            Kindly ask you to inform about a necessity of assignment and it's issue date.
                            """)
                        else:
                            st.warning("Select specialities for request")


def show_all_units(sod_df):

    temp_sod = sod_df.copy()
    temp_sod['request_update'] = False



    try:
        filtered_sod = dataframe_explorer(temp_sod, case=False)
    except Exception as e:
        st.write(f"<h5 style='text-align: center; color: red;'>Can't filter table... {err_handler(e)}</h5>",
                 unsafe_allow_html=True)
        filtered_sod = temp_sod

    st.markdown(f"<h4 style='text-align: center; color: #249ded;'>Records Q-ty: {len(filtered_sod)}:</h4>",
                unsafe_allow_html=True)

    sod_to_request = st.data_editor(filtered_sod, use_container_width=True,
                                                 key=st.session_state.req_lines_avail, height=800)
    return sod_to_request


def show_units_for_request(units):
    sod_to_request = units[units.request_update]

    if len(sod_to_request):
        st.divider()
        st.subheader(f"Send request for {len(sod_to_request)} Units?")
        st.dataframe(sod_to_request, use_container_width=True)

        # st.session_state.req_lines_avail = True
    return sod_to_request


def request_updates(temp_sod):
    u_df = st.session_state.adb['users']

    if len(temp_sod):
        st.divider()

        lc, rc = st.columns(2, gap='medium')
        cancel_but = lc.button('Cancel Request', use_container_width=True)
        request_but = rc.button('Request for Update', use_container_width=True)

        i = 0
        if request_but:
            st.subheader("Sent Requests:")
            for ind, row in temp_sod.iterrows():

                subj = f"{row.project_id}: {row.set_name}. Request for status update | Запрос на обновление статуса"

                html = f"""
                    <html>
                      <head></head>
                      <body>
                        <h3>
                          Hello, Colleague!
                          <hr>
                        </h3>
                        <h5>
                          Please update the Status of Unit: <u>{row.project_id}: {row.set_name}</u>
                           at Site <a href="https://e-design.streamlit.app/">e-design.streamlit.app</a>
                        </h5>
                        <h5>
                          Пожалуйста, обновите Статус Комплекта: <u>{row.project_id}: {row.set_name}</u>
                           на Сайте <a href="https://e-design.streamlit.app/">e-design.streamlit.app</a>
                        </h5>
                            <hr>
                            Best regards, Administration 😎
                        </p>
                      </body>
                    </html>
                """

                receiver = u_df.loc[u_df.login == row.coord_id, 'email'].to_numpy()[0]
                cc_rec = u_df.loc[u_df.login == row.perf_id, 'email'].to_numpy()[0]

                reply = send_mail(receiver=receiver, cc_rec=cc_rec, subj=subj, html=html)

                if reply == 200:
                    st.write(f":green[{row.project_id}: {row.set_name}]")
                    st.write(f":green[Sent to {receiver}, {cc_rec}]")

                    i += 1
                else:
                    st.warning(reply)

            st.session_state.req_lines_avail += 1

        if cancel_but:
            st.session_state.req_lines_avail += 1
            st.experimental_rerun()

        if i:
            st.button(f'{i} Requests Sent - OK', use_container_width=True)


def manage_units():

    center_style()

    u_df = st.session_state.adb['users'].copy()
    proj_df = st.session_state.adb['project'].copy()
    sod_df = st.session_state.adb['sod'].copy()

    @lru_cache(100)
    def change_proj_resp(x):
        return u_df.loc[u_df.index == x, 'login'].to_numpy()[0]

    proj_df.responsible_el = proj_df.responsible_el.apply(change_proj_resp)

    @lru_cache(100)
    def change_sod_resp(x):
        return u_df.loc[u_df.index == x, 'login'].to_numpy()[0]

    @lru_cache(100)
    def change_shortname(x):
        return proj_df.loc[proj_df.index == x, 'short_name'].to_numpy()[0]

    sod_df.project_id = sod_df.project_id.apply(change_shortname)
    sod_df.coord_id = sod_df.coord_id.apply(change_sod_resp)
    sod_df.perf_id = sod_df.perf_id.apply(change_sod_resp)

    empty_sets_1, content_sets, empty_sets_2 = st.columns([1, 14, 1])

    with empty_sets_1:
        st.empty()
    with empty_sets_2:
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('', help="Эта страница предназначена для :orange[Создания, Изменения и Просмотра] "
                         "Комплектов Чертежей Проекта \n"
                         "---"
                         "\n"
                         "This page is intended to :orange[Create, Edit and View] of Project Units")

    with content_sets:
        st.title(':orange[Units]')

        tab_create, tab_update, tab_preview = st.tabs(['Create New Unit', 'Edit Existing Unit', 'View All Units'])

        with tab_create:

            with st.form('new_sod'):
                l_c, r_c = st.columns(2, gap='medium')
                proj_short = l_c.selectbox('Select a Project *', st.session_state.proj_names)
                unit_name = r_c.text_input("Enter the Name for new Set of Drawings / Unit *", max_chars=200).strip()
                coordinator = l_c.selectbox("Coordinator *", st.session_state.appl_logins)
                performer = r_c.selectbox("Performer *", st.session_state.appl_logins)
                set_start_date = l_c.date_input('Start Date *', datetime.date.today(), key="new_set_time_picker")
                r_c.text('')
                stage = r_c.radio("Select the Stage *", STAGES, horizontal=True)
                r_c.text('')
                status = r_c.select_slider("Select the Current Status *", COMPLETION, value='0%')
                notes = l_c.text_area("Add Notes", max_chars=500, height=90).strip()
                l_c.write(":red[\* - required]")
                r_c.text('')
                create_sod_but = r_c.form_submit_button("Create", use_container_width=True)

            res_l, res_c, res_r = st.columns([1, 2, 1], gap='medium')

            if create_sod_but:

                reply = add_sod(proj_short, unit_name, stage, status, set_start_date, coordinator, performer, notes)

                if reply['status'] == 201:
                    res_l.success(f"New Set '{unit_name}' for Project '{proj_short}' is added to DataBase")

                    receiver = u_df.loc[u_df.login == coordinator, 'email'].to_numpy()[0]
                    cc_rec = u_df.loc[u_df.login == performer, 'email'].to_numpy()[0]

                    cur_user_email = st.session_state.user['email']

                    subj = f"{proj_short}: {unit_name}. New Unit | Новый комплект чертежей"

                    html = f"""
                        <html>
                          <head></head>
                          <body>
                            <h3>
                              Hello, Colleague!
                              <hr>
                            </h3>
                            <h5>
                              You got this message because you are responsible for New Unit:
                              <b>{proj_short}: {unit_name}</b>
                            </h5>
                            <p>
                            <hr>
                            Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """

                    if receiver == cc_rec:
                        cc_rec = 'sergey.priemshiy@uzliti-en.com'

                    if receiver == cur_user_email:
                        receiver = 'sergey.priemshiy@uzliti-en.com'

                    reply_2 = send_mail(receiver, cc_rec, subj, html)

                    if reply_2 == 200:
                        res_c.success(f'Notifications were sent to {receiver}, {cc_rec}')

                    reply3 = update_state('sod')

                    if reply3 != 'Data is updated':
                        st.warning(reply3)
                        st.stop()

                    res_r.button('OK', key='close_upd_sod2_report', use_container_width=True)

                else:
                    st.warning(reply['err_descr'])

        with tab_update:

            l_c, r_c = st.columns(2, gap='medium')

            proj_short = l_c.selectbox('Select Project', st.session_state.proj_names)

            unit_list = sod_df.loc[sod_df.project_id == proj_short, 'set_name'].tolist()

            if len(unit_list):

                unit_name = r_c.selectbox('Select Unit', unit_list)

                current_stage = sod_df.loc[sod_df.set_name == unit_name, 'stage'].to_numpy()[0]

                with st.form('update_unit'):
                    lc, rc = st.columns(2, gap='medium')
                    new_unit_name = lc.text_input('New Name for Unit', value=unit_name)
                    new_stage = rc.selectbox("New Stage for Unit", STAGES, index=get_list_index(STAGES, current_stage))

                    upd_unit_but = st.form_submit_button("Update Details for Unit", use_container_width=True)

                if upd_unit_but:
                    u_id = sod_df.loc[(sod_df.project_id == proj_short) &
                                      (sod_df.set_name == unit_name)].index.to_numpy()[0]

                    reply = update_unit_name_stage(u_id, new_unit_name, new_stage)

                    l_rep, c_rep, r_rep = st.columns([1, 2, 1], gap='medium')

                    if reply['status'] == 201:

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

                        receiver = u_df.loc[u_df.login == sod_df.loc[u_id, 'coord_id'], 'email'].to_numpy()[0]
                        cc_rec = u_df.loc[u_df.login == sod_df.loc[u_id, 'perf_id'], 'email'].to_numpy()[0]

                        if not (isinstance(receiver, str) and "@" in receiver):
                            st.warning("Can't get Coordinator e-mail...")
                            st.stop()

                        if not (isinstance(cc_rec, str) and "@" in cc_rec):
                            st.warning("Can't get Coordinator e-mail...")
                            st.stop()

                        if receiver == cc_rec:
                            cc_rec = 'sergey.priemshiy@uzliti-en.com'

                        reply2 = send_mail(receiver, cc_rec, subj, html)

                        if reply2 == 200:
                            c_rep.success(f'Notifications were sent to {receiver}, {cc_rec}')

                        reply3 = update_state('sod')

                        if reply3 != 'Data is updated':
                            st.warning(reply3)

                        r_rep.text('')
                        r_rep.button('Close Report', key='close_upd_unit_report', use_container_width=True)

                        st.stop()

                    else:
                        st.warning(reply['err_descr'])
                        st.stop()

            else:
                r_c.text("")
                r_c.write("")
                r_c.warning("Select a Project")


        with tab_preview:

            units_for_request = show_all_units(sod_df)

            sod_to_request = show_units_for_request(units_for_request)

            request_updates(sod_to_request)
