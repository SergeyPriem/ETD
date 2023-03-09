# -*- coding: utf-8 -*-

from time import sleep
import streamlit as st


def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1,9,1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()


    with tr_content:
        st.title(':orange[Transmittals]')

        placeholder = st.empty()
        sleep(1)
        # Replace the placeholder with some text:
        placeholder.text("Hello")
        sleep(5)
        # Replace the text with a chart:
        placeholder.line_chart({"data": [1, 5, 2, 6]})
        sleep(5)
        # Replace the chart with several elements:
        with placeholder.container():
            st.write("This is one element")
            st.write("This is another")
        sleep(3)
        # Clear all those elements:
        placeholder.empty()