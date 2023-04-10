# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from pre_sets import trans_types
from projects import get_trans, get_proj_list, add_new_trans
from users import get_logins_for_registered


def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1, 15, 1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()

    with tr_content:
        st.title(':orange[Transmittals]')

        add_trans_tab, view_trans_tab = st.tabs(['Add New Transmittal', 'View Existing Transmittals'])

        with add_trans_tab:
            with st.form("add_trans"):
                lc, cc, rc = st.columns([5, 4, 4], gap='medium')
                project = lc.selectbox("Project", get_proj_list())
                t_type = lc.radio("Transmittal Type", trans_types, horizontal=True)
                lc.write("")
                ref_trans = rc.text_input("In reply to")
                trans_num = cc.text_input("Transmittal Number")
                subj = cc.text_input("Subject")
                ans_required = cc.radio("Reply required", ('Yes', 'No'), horizontal=True)
                cc.write("")
                responsible = cc.selectbox("Responsible Employee", get_logins_for_registered())
                cc.write("")
                link = rc.text_input("Link")
                reply_date = rc.date_input("Due Date")
                notes = rc.text_input('Notes')
                trans_date = lc.date_input("Transmittal Date")
                author = lc.text_input('Originator of the Transmittal')

                add_trans_but = lc.form_submit_button("Preview Transmittal's Data")

            if add_trans_but:
                l_prev, r_prev = st.columns([1, 8])
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
                            
                            **:blue[{trans_num}]**
                            
                            **:blue[{ref_trans}]**
                            
                            **:blue[{t_type}]**
                            
                            **:blue[{subj}]**
                            
                            **:blue[{link}]**
                            
                            **:blue[{trans_date}]**
                            
                            **:blue[{ans_required}]**
                            
                            **:blue[{reply_date}]**
                            
                            **:blue[{author}]**
                            
                            **:blue[{responsible}]**
                            
                            **:blue[{notes}]** 
                            """)

            if st.button('Add to DataBase'):
                reply = add_new_trans(project, trans_num, ref_trans, t_type, subj, link, trans_date, ans_required,
                                      reply_date, author, responsible, notes)
                # reporter(reply)
                st.info(reply)

        with view_trans_tab:
            my_all_tr = st.radio("Select the Option", ["My Transmittals", 'All Transmittals'], horizontal=True)

            if my_all_tr == "My Transmittals":
                user_email = st.session_state.user
            else:
                user_email = None

            df = get_trans(user_email)

            # if df == "Empty Table":
            #     st.wtite("No Available Transmittals")
            #     st.stop()
            #
            if isinstance(df, pd.DataFrame):
                if len(df) > 0:
                    st.subheader(f"{my_all_tr}: {len(df)}")
                    st.write(df)
                else:
                    st.info("No Tansmittals in DataBase")
                    st.stop()


