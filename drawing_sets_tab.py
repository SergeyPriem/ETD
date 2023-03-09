# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st

from pre_sets import specialities, specialities_rus
from projects_db import get_sets, get_own_tasks


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
            user_email = st.session_state.user
        else:
            user_email = None

        df = get_sets(user_email)

        proj_list = df['project'].drop_duplicates()

        proj_selected = st.selectbox("Project for Search", proj_list)
        sets_list = df[df.project == proj_selected]['set_name']

        sets_selected = st.multiselect("Set / Unit for Search", sets_list)

        df = df[df.set_name.isin(sets_selected)].set_index("id")

        df['preview'] = False

        edit_df = st.experimental_data_editor(df, use_container_width=True, height=200,
                                              num_rows='fixed', key='sets', disabled=False)
        edited_num = len(edit_df[edit_df.preview == True])

        if edited_num == 1:
            # st.write(edited_num)
            proj_set = (edit_df[edit_df.preview]['project'].values[0], edit_df[edit_df.preview]['set_name'].values[0])
            task_col, in_out_col, quant_col = st.columns([9, 2, 2])

            with in_out_col:
                in_out_radio = st.radio("Select Incoming / Outgoing", ('In', 'Out'), horizontal=True)

            # with reset_col:
            #     st.text('')
            #     reset_but = st.button('Reset')
            sets_tasks = get_own_tasks(proj_set).set_index('id')

            if in_out_radio == "In":
                sets_tasks = sets_tasks[(sets_tasks.in_out == 'Входящие') | (sets_tasks.in_out == 'In')]
            else:
                sets_tasks = sets_tasks[(sets_tasks.in_out == 'Исходящие') | (sets_tasks.in_out == 'Out')]

            with task_col:
                task_head = st.subheader(f"Available Tasks for :red[{proj_set[0]}: {proj_set[1]}]")

            with quant_col:
                st.write("")
                st.write("")
                st.write(f'Quantity: {len(sets_tasks)}')

            sets_tasks = sets_tasks.sort_values(by=['speciality', 'date'], ascending=[True, False])
            st.write(sets_tasks)

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
                st.subheader("Not available Tasks for Specialities. Here you can create request for assignments")
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
                                f"**Недостающие задания для {sets_tasks.project.values[0]}: {sets_tasks.set_draw.values[0]}**")
                            st.markdown("""<u>Тело:</u>""", unsafe_allow_html=True)
                            st.markdown(f"""
                            В ЭлектроОтделе сейчас в разработке комплект чертежей:  
                            **{sets_tasks.project.values[0]}: {sets_tasks.set_draw.values[0]}**.  
                            В настоящее время отсутствуют задания по специальностям: 
                            **{', '.join(request_df[request_df.request == True].index.values)}**.  
                            Просим сообщить о необходимости задания и его сроке выдачи.
                            """)
                            st.write('')
                            st.markdown("""<u>Subject:</u>""", unsafe_allow_html=True)
                            st.markdown(
                                f"**Not available assignments for {sets_tasks.project.values[0]}: {sets_tasks.set_draw.values[0]}**")
                            st.markdown("""<u>Body:</u>""", unsafe_allow_html=True)
                            st.markdown(f"""
                            Currently Electrical Department is developing:  
                            **{sets_tasks.project.values[0]}: {sets_tasks.set_draw.values[0]}*.  
                            For now we haven't assignments from: 
                            **{', '.join(request_df[request_df.request == True].index.values)}**.  
                            Kindly ask you to inform about a necessity of assignment at it's issue date.
                            """)
                        else:
                            st.warning("Select specialities for request")
