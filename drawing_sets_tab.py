# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
from pre_sets import specialities, specialities_rus
from projects import get_sets, get_own_tasks

st.cache_data(ttl=600)


def drawing_sets():
    empty1, content, empty2 = st.columns([1, 30, 1])
    with empty1:
        st.empty()
    with empty2:
        st.empty()

    with content:
        st.title(':orange[Drawing Sets]')

        my_all = st.radio("Select the Option", ["My Sets", 'All Sets'], horizontal=True)

        st.subheader(my_all)

        if my_all == "My Sets":
            user_login = st.session_state.user
        else:
            user_login = None

        df = get_sets(user_login)

        if not isinstance(df, pd.DataFrame):
            st.write("No sets available in DataBase")
            st.stop()

        st.write(df)

        proj_list = df.project_id

        if isinstance(df, pd.DataFrame):
            proj_list = df['project_id'].drop_duplicates()
        else:
            st.write(df)

        proj_selected = st.selectbox("Project for Search", proj_list)
        sets_list = df[df.project_id == proj_selected]['set_name']

        sets_selected = st.multiselect("Set / Unit for Search", sets_list)

        df = df[df.set_name.isin(sets_selected)]  # .set_index("project_id")

        df.insert(0, 'preview', False)

        edit_df = st.experimental_data_editor(df, use_container_width=True, height=200,
                                              num_rows='fixed', key='sets', disabled=False)

        edited_num = len(edit_df[edit_df.preview == True])

        if edited_num == 1:
            st.markdown("---")
            proj_set = (
            edit_df[edit_df.preview]['project_id'].values[0], edit_df[edit_df.preview]['set_name'].values[0])
            task_col, in_out_col, quant_col = st.columns([9, 2, 2])

            with in_out_col:
                in_out_radio = st.radio("Select Incoming / Outgoing", ('In', 'Out'), horizontal=True)

            sets_tasks = get_own_tasks(proj_set)  # .set_index('id')
            st.write(sets_tasks)

            if in_out_radio == "In":
                sets_tasks = sets_tasks[(sets_tasks.in_out == 'Входящие') | (sets_tasks.in_out == 'In')]
            else:
                sets_tasks = sets_tasks[(sets_tasks.in_out == 'Исходящие') | (sets_tasks.in_out == 'Out')]

            with task_col:
                st.subheader(f"Available Assignments for :red[{proj_set[0]}: {proj_set[1]}:] {in_out_radio}")

            with quant_col:
                st.write("")
                st.write("")
                st.write(f'Quantity: {len(sets_tasks)}')

            sets_tasks = sets_tasks.sort_values(by=['speciality', 'date'], ascending=[True, False])
            st.write(sets_tasks[['stage', 'speciality', 'date', 'description', 'link', 'source', 'comment',
                                 'backup_copy', 'coord_log', 'perf_log', 'added_by']])
            st.markdown("---")

            aval_spec = list(sets_tasks.speciality.drop_duplicates())

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
                    # st.write(request_df)

                with but_col:
                    request_but = st.button('Create Request')

                with request_col:
                    if request_but:
                        if len(request_df[request_df.request == True].index):
                            st.subheader("Draft of e-mail")
                            st.markdown("""<u>Тема:</u>""", unsafe_allow_html=True)
                            st.markdown(
                                f"**Недостающие задания для {proj_set[0]}: {proj_set[1]}**")
                            st.markdown("""<u>Тело:</u>""", unsafe_allow_html=True)
                            st.markdown(f"""
                            В ЭлектроОтделе сейчас в разработке комплект чертежей:
                            **{proj_set[0]}: {proj_set[1]}**.
                            В настоящее время отсутствуют задания по специальностям:
                            **{', '.join(request_df[request_df.request == True].index.values)}**.
                            Просим сообщить о необходимости задания и его сроке выдачи.
                            """)
                            st.write('')
                            st.markdown("""<u>Subject:</u>""", unsafe_allow_html=True)
                            st.markdown(
                                f"**Not available assignments for {proj_set[0]}: {proj_set[1]}**")
                            st.markdown("""<u>Body:</u>""", unsafe_allow_html=True)
                            st.markdown(f"""
                            Currently Electrical Department is developing:
                            **{proj_set[0]}: {proj_set[1]}**.
                            For now we haven't assignments from:
                            **{', '.join(request_df[request_df.request == True].index.values)}**.
                            Kindly ask you to inform about a necessity of assignment and it's issue date.
                            """)
                        else:
                            st.warning("Select specialities for request")
