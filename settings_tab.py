# -*- coding: utf-8 -*-
import streamlit as st

from app import home_content
from users import update_settings


def settings_content():
    empty1_set, content_set, empty2_set = st.columns([1, 10, 1])
    with empty1_set:
        st.empty()
    with empty2_set:
        st.empty()

    with content_set:

        st.title(':orange[Settings]')
        st.text('This page is intended to make some adjustments for more comfortable use of Application')

        st.markdown("---")
        with st.form('adjust_settings'):
            st.session_state.delay = st.select_slider('Time delay for info messages',
                                                      options=[0,1,2,3,4], value=st.session_state.delay)

            menu_position = st.radio('Location of menu', ("Top", "Left", ),
                                         index=st.session_state.vert_menu, horizontal=True)

            appl_set_but = st.form_submit_button('Apply')

        if appl_set_but:
            if menu_position == 'Left':
                st.session_state.vert_menu = 1
            else:
                st.session_state.vert_menu = 0
            update_settings(st.session_state.user, st.session_state.vert_menu, st.session_state.delay)
            # save preferences to DB
            home_content()




