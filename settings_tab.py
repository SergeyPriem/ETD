# -*- coding: utf-8 -*-
import streamlit as st

def drawing_sets():
    empty1_set, content_set, empty2_set = st.columns([1, 30, 1])
    with empty1_set:
        st.empty()
    with empty2_set:
        st.empty()

    with content_set:
        st.title(':orange[Settings]')
        st.write('This page is intended to make some adjustments for more comfortable use of Application')
