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
                lc, cc, rc = st.columns(3, gap='medium')
                project = lc.selectbox("Project", get_proj_list())
                t_type = lc.selectbox("Transmittal Type", trans_types)
                out_trans = lc.text_input("In reply to:")
                in_trans = cc.text_input("Transmittal Number")
                subj = cc.text_input("Subject")
                ans_required = cc.radio("Reply required", ('Yes', 'No'), horizontal=True)
                cc.write("")
                in_date = rc.date_input("Transmittal Date")
                out_date = rc.date_input("Due Date")
                link = rc.text_input("Link")
                notes = cc.text_area('Notes')
                lc.write("")
                lc.write("")
                add_trans_but = lc.form_submit_button("Add Transmittal", use_container_width=True)

            if add_trans_but:
                st.info(f"""
                     {in_trans,
                     in_date,
                     out_trans,
                     ans_required,
                     out_date,
                     project,
                     subj,
                     link,
                     t_type,
                     notes,
                     add_trans_but}
                     """
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


