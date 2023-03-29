# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from pre_sets import trans_types, reporter
from projects import get_trans, get_proj_list, add_new_trans
from users import get_registered_emails


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
                t_type = lc.radio("Transmittal Type", trans_types, horizontal=True)
                lc.write("")
                out_trans = rc.text_input("In reply to")
                in_trans = cc.text_input("Transmittal Number")
                subj = cc.text_input("Subject")
                ans_required = cc.radio("Reply required", ('Yes', 'No'), horizontal=True)
                cc.write("")
                responsible = cc.selectbox("Responsible Employee", get_registered_emails())
                cc.write("")
                link = rc.text_input("Link")
                out_date = rc.date_input("Due Date")
                notes = rc.text_input('Notes')
                in_date = lc.date_input("Transmittal Date")
                author = lc.text_input('Originator of the Transmittal')
                add_trans_but = lc.form_submit_button("Preview Transmittal's Data")

            if add_trans_but:
                l_prev, r_prev = st.columns([1,8])
                l_prev.markdown(f"""
                            Project:
                            
                            Transmittal Number:
                            
                            In reply to:
                            
                            Transmittal Type:
                            
                            Subject:
                            
                            Link:
                            
                            Transmittal Date:
                            
                            Reply required:
                            
                            Due Date:
                            
                            Originator:
                            
                            Responsible Employee:
                            
                            Notes: 
                            """)

                r_prev.markdown(f"""
                            **:blue[{project}]**
                            
                            **:blue[{in_trans}]**
                            
                            **:blue[{out_trans}]**
                            
                            **:blue[{t_type}]**
                            
                            **:blue[{subj}]**
                            
                            **:blue[{link}]**
                            
                            **:blue[{in_date}]**
                            
                            **:blue[{ans_required}]**
                            
                            **:blue[{out_date}]**
                            
                            **:blue[{author}]**
                            
                            **:blue[{responsible}]**
                            
                            **:blue[{notes}]** 
                            """)

            if st.button('Add to DataBase'):
                reply = add_new_trans(project, in_trans, out_trans, t_type, subj, link, in_date, ans_required,
                                      out_date, author, responsible, notes)
                reporter(reply)


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


