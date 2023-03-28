# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from projects import get_trans


def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1,15,1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()


    with tr_content:
        st.title(':orange[Transmittals]')

        my_all_tr = st.radio("Select the Option", ["My Transmittals", 'All Transmittals'], horizontal=True)

        st.subheader(my_all_tr)

        if my_all_tr == "My Transmittals":
            user_email = st.session_state.user
        else:
            user_email = None


        df = get_trans(user_email)
        st.write(df)
        # if isinstance(df, pd.DataFrame):
        #     df
        # else:
        #     st.write("Transmittals not Available")
        # placeholder = st.empty()
        # sleep(1)
        # # Replace the placeholder with some text:
        # placeholder.text("Hello")
        # sleep(1)
        # # Replace the text with a chart:
        # placeholder.line_chart({"data": [1, 5, 2, 6]})
        # sleep(1)
        # # Replace the chart with several elements:
        # with placeholder.container():
        #     st.write("This is one element")
        #     st.write("This is another")
        # sleep(1)
        # # Clear all those elements:
        # placeholder.empty()
        #
        # # import libraries


