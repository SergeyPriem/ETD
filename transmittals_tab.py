# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from pre_sets import trans_types
from projects import get_trans, get_proj_list
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
                add_trans_but = lc.form_submit_button("Preview Filled Form")

            if add_trans_but:
                st.markdown("""<style> .nobord table, tr, td, ths {
                        border-style: hidden;
                  </style> """, unsafe_allow_html=True)
                # st.markdown(f"""
                # <table class="nobord">
                # <tr>
                #     <td>Project</td>
                #     <td>{project}</td>
                #     <td></td>
                #     <td>Transmittal Number</td>
                #     <td>{in_trans}</td>
                #     <td></td>
                #     <td>In reply to</td>
                #     <td>{out_trans}</td>
                # </tr>
                #
                # <tr>
                #     <td>Transmittal Type</td>
                #     <td>{t_type}</td>
                #     <td></td>
                #     <td>Subject</td>
                #     <td>{subj}</td>
                #     <td></td>
                #     <td>Link</td>
                #     <td>{link}</td>
                # </tr>
                #
                # <tr>
                #     <td>Transmittal Date</td>
                #     <td>{in_date}</td>
                #     <td></td>
                #     <td>Reply required</td>
                #     <td>{ans_required}</td>
                #     <td></td>
                #     <td>Due Date</td>
                #     <td>{out_date}</td>
                # </tr>
                #
                # <tr>
                #     <td>Originator of the Transmittal</td>
                #     <td>{author}</td>
                #     <td></td>
                #     <td>Responsible Employee</td>
                #     <td>{responsible}</td>
                #     <td></td>
                #     <td>Notes</td>
                #     <td>{notes}</td>
                # </tr>
                #
                # </table>
                # <br>
                # """, unsafe_allow_html=True)

                st.markdown(f"""
                            Project: **:blue[{project}]**
                            
                            Transmittal Number:  **:blue[{in_trans}]**
                            
                            In reply to:  **:blue[{out_trans}]**
                            
                            Transmittal Type:  **:blue[{t_type}]**
                            
                            Subject:  **:blue[{subj}]**
                            
                            Link:  **:blue[{link}]**
                            
                            Transmittal Date: **:blue[{in_date}]**
                            
                            Reply required:  **:blue[{ans_required}]**
                            
                            Due Date:  **:blue[{out_date}]**
                            
                            Originator of the Transmittal:  **:blue[{author}]**
                            
                            Responsible Employee:  **:blue[{responsible}]**
                            
                            Notes:  **:blue[{notes}]**
                            """)


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
                     add_trans_but, responsible, author}
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


