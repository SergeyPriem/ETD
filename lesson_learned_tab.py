# -*- coding: utf-8 -*-

import streamlit as st

from util.utilities import center_style


def lessons_content():

    center_style()

    empty1, content, empty2 = st.columns([1, 30, 1])
    with empty1:
        st.empty()
    with empty2:
        st.empty()

    with content:
        st.title(':orange[Knowledge] - under Development')
        st.write('It would be great to collect, store and share experiences of technical'
                 ' solutions from which lessons can be learned')

        content_col1, content_col2 = st.columns(2, gap="medium")
        with content_col1:
            st.text_area("Place here your story about some valuable experience")
        with content_col2:
            st.text_area("Поместите сюда текст о каком-либо интересном опыте")

        st.button("SAVE")
