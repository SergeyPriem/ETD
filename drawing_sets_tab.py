# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from pre_sets import specialities, specialities_rus
from projects import get_sets, get_own_tasks


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

        ds_left, lc, ds_center, cr, ds_rigth = st.columns([5, 6, 4, 5, 5])
        ds_center.text('')

        # st.markdown("""
        #     <style>
        #         .element-container_css-qvoliw_e1tzin5v2{
        #             margin-left: auto;
        #             margin-right: auto;
        #         }
        #     </style>
        #     """, unsafe_allow_html=True)

        # expand-trigger
        my_all = ds_center.radio("Select the Option", ["My Units", 'All Units'],
                                 horizontal=True, label_visibility='collapsed')

        if my_all == "My Units":
            user_login = st.session_state.user
        else:
            user_login = None

        df = get_sets(user_login)

        if not isinstance(df, pd.DataFrame):
            st.write("No Units available in DataBase")
            st.stop()

        proj_list = df.project

        ds_left.subheader(f"{my_all}: {len(proj_list)}")

        ds_rigth.text('')
        units_ch_b = ds_rigth.checkbox("Show Units Table")

        if units_ch_b:
            if 'id' in df.columns:
                df.set_index('id', inplace=True)
            st.experimental_data_editor(df, use_container_width=True)

        if isinstance(df, pd.DataFrame):
            proj_list = df['project'].drop_duplicates()
        else:
            st.write(df)

        proj_selected = st.selectbox("Project for Search", proj_list)
        units_list = df[df.project == proj_selected]['unit']

        unit_selected = st.selectbox("Unit for Search", units_list)

        unit_id = df.loc[df.unit == unit_selected, 'id']

        st.write(unit_id)

        # if "id" in df.columns:
        #     df.set_index('id', inplace=True)
        #
        # df.insert(1, 'view_tasks', False)

        # edit_df = st.experimental_data_editor(df, use_container_width=True, height=200,
        #                                       num_rows='fixed', key='sets', disabled=False)

        # edited_num = len(edit_df[edit_df.view_tasks])

        # set_id = edit_df.loc[edit_df.view_tasks].index

        st.subheader(f"Project: :red[{proj_selected}]. Unit: :red[{unit_selected[0]}]")

        units_tasks = get_own_tasks(unit_id)  # .values[0]

        if isinstance(units_tasks, str):
            if units_tasks == "Empty Table":
                st.warning('No Tasks Available for selected Unit')
                st.stop()

        if not isinstance(units_tasks, pd.DataFrame):
            st.stop()

        task_col, in_out_col, quant_col = st.columns([9, 2, 2])

        with in_out_col:
            in_out_radio = st.radio("Select Incoming / Outgoing", ('In', 'Out'), horizontal=True)

        if in_out_radio == "In":
            units_tasks = units_tasks[(units_tasks.in_out == 'Входящие') | (units_tasks.in_out == 'In')]
        else:
            units_tasks = units_tasks[(units_tasks.in_out == 'Исходящие') | (units_tasks.in_out == 'Out')]

        with task_col:
            # st.subheader(f"Available Assignments for :red[{set_id[0]}: {set_id[1]}:] {in_out_radio}")
            st.subheader(f"Available Assignments")

        with quant_col:
            st.write("")
            st.write("")
            st.write(f'Quantity: {len(units_tasks)}')

        units_tasks = units_tasks.sort_values(by=['speciality', 'date'], ascending=[True, False])
        st.experimental_data_editor(units_tasks[['stage', 'speciality', 'date', 'description', 'link', 'source',
                                                 'comment', 'backup_copy', 'coord_log', 'perf_log', 'added_by']],
                                    use_container_width=True)
        st.divider()

        aval_spec = list(units_tasks.speciality.drop_duplicates())

        spec_dual = (*specialities, *specialities_rus)
        not_aval_spec = []

        for i in spec_dual:
            if i not in aval_spec:
                not_aval_spec.append(i)

        not_aval_df = pd.DataFrame(not_aval_spec, columns=['speciality'])
        not_aval_df['request'] = False
        not_aval_df = not_aval_df.set_index('speciality')

        if in_out_radio == "In":
            st.subheader("Not available Assignments for Specialities. Here you can create request for assignments")
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
                        # {proj_selected}]. Unit: :red[{units_selected[0]}]")
                        st.markdown(f"**Недостающие задания для {proj_selected}: {unit_selected[0]}**")
                        st.markdown("""<u>Тело:</u>""", unsafe_allow_html=True)
                        st.markdown(f"""
                        В ЭлектроОтделе сейчас в разработке комплект чертежей:
                        **{proj_selected}: {unit_selected[0]}**.
                        В настоящее время отсутствуют задания по специальностям:
                        **{', '.join(request_df[request_df.request == True].index.values)}**.
                        Просим сообщить о необходимости задания и его сроке выдачи.
                        """)
                        st.write('')
                        st.markdown("""<u>Subject:</u>""", unsafe_allow_html=True)
                        st.markdown(
                            f"**Not available assignments for {proj_selected}: {unit_selected[0]}**")
                        st.markdown("""<u>Body:</u>""", unsafe_allow_html=True)
                        st.markdown(f"""
                        Currently Electrical Department is developing:
                        **{proj_selected}: {unit_selected[0]}**.
                        For now we haven't assignments from:
                        **{', '.join(request_df[request_df.request == True].index.values)}**.
                        Kindly ask you to inform about a necessity of assignment and it's issue date.
                        """)
                    else:
                        st.warning("Select specialities for request")

        if edited_num > 1:
            st.info("Please select only one row for preview")
