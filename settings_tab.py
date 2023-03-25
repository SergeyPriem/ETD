# -*- coding: utf-8 -*-
import streamlit as st

from pony_users import update_settings


def settings_content():
    empty1_set, content_set, empty2_set = st.columns([1, 30, 1])
    with empty1_set:
        st.empty()
    with empty2_set:
        st.empty()

    with content_set:

        st.title(':orange[Settings]')
        st.text('This page is intended to make some adjustments for more comfortable use of Application')

        st.markdown("---")
        left_col, empty_col, centr_col, right_col = st.columns([7,3, 3,5], gap='medium')

        st.session_state.delay = left_col.select_slider('Time delay for info messages',
                                                        options=[1,2,3,4], value=st.session_state.delay)

        with centr_col:
            menu_position = st.radio('Location of menu', ("Top", "Left", ),
                                     index=st.session_state.vert_menu, horizontal=True)

        with right_col:
            st.write('')
            st.write('')
            if st.button("Apply"):
                if menu_position == 'Left':
                    st.session_state.vert_menu = 1
                else:
                    st.session_state.vert_menu = 0
                update_settings(st.session_state.user, st.session_state.vert_menu, st.session_state.delay)
                # save preferences to DB
                st.experimental_rerun()




