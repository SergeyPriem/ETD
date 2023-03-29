# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from pre_sets import trans_types
from projects import get_trans, get_proj_list


def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1,15,1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()


    with tr_content:
        st.title(':orange[Transmittals]')


        add_trans_tab, view_trans_tab = st.tabs(['Add New Transmittal', 'View Existing Transmittals'])

        with add_trans_tab:
            with st.form("add_trans"):
                left_col, center_col, right_col = st.columns(3, gap='medium')
                project = left_col.selectbox("Project", get_proj_list())
                in_trans = center_col.text_input("Transmittal Number")
                in_date = right_col.date_input("Transmittal Date")
                t_type = left_col.selectbox("Transmittal Type", trans_types)
                ans_required = center_col.radio("Reply required", ('Yes', 'No'), horizontal=True)
                center_col.text()
                out_date = right_col.date_input("Due Date")
                out_trans = left_col.text_input("In reply to:")
                subj = center_col.text_input("Subject")
                link = right_col.text_input("Link")
                notes = center_col.text_area('Notes')
                add_trans_but = st.form_submit_button("Add Transmittal")

            if add_trans_but:
                st.info(
                    in_trans,
                    in_date,
                    out_trans,
                    ans_required,
                    out_date,
                    project,
                    subj,
                    link,
                    t_type,
                    notes,
                    add_trans_but
                )


        with view_trans_tab:
            my_all_tr = st.radio("Select the Option", ["My Transmittals", 'All Transmittals'], horizontal=True)
            st.subheader(my_all_tr)

            if my_all_tr == "My Transmittals":
                user_email = st.session_state.user
            else:
                user_email = None

            df = get_trans(user_email)

            if isinstance(df, pd.DataFrame):
                if len(df)>0:
                    st.write(df)
                else:
                    st.info("No Tansmittals in DataBase")

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


