# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from pre_sets import trans_types
from projects import get_trans, add_new_trans
from users import get_logins_for_registered, get_logins_for_current


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
                project = lc.selectbox("Project", st.session_state.proj_names)
                t_type = lc.radio("Transmittal Type", trans_types, horizontal=True)
                lc.write("")
                ref_trans = rc.text_input("In reply to")
                trans_num = cc.text_input("Transmittal Number")
                subj = cc.text_input("Subject")
                ans_required = cc.radio("Reply required", ('Yes', 'No'), horizontal=True)
                cc.write("")
                responsible = cc.selectbox("Responsible Employee", get_logins_for_current())
                cc.write("")
                link = rc.text_input("Link")
                reply_date = rc.date_input("Due Date")
                notes = rc.text_input('Notes')
                trans_date = lc.date_input("Transmittal Date")
                author = lc.text_input('Originator of the Transmittal')

                add_trans_but = lc.form_submit_button("Preview Transmittal's Data", use_container_width=True)

            if add_trans_but:
                l_prev, r_prev = st.columns([1, 8])

                st.markdown("""<style>
                                .task_preview table, tr {
                                        border-style: hidden;
                                        margin: auto;
                                    }

                                .task_preview td {
                                        border-style: hidden;
                                        text-align: left;
                                    }
                                  </style>
                                  """, unsafe_allow_html=True)

                st.markdown(f"""
                <table class="task_preview">
                    <tr>
                        <td>Project:</td><td style="color: #1569C7;"><b>{project}</b></td>
                    </tr>
                    <tr>
                        <td>Transmittal Number:</td><td style="color: #1569C7;"><b>{trans_num}</b></td>
                    </tr>
                    <tr>
                        <td>In reply to:</td><td style="color: #1569C7;"><b>{ref_trans}</b></td>
                    </tr>
                    <tr>
                        <td>Transmittal Type:</td><td style="color: #1569C7;"><b>{t_type}</b></td>
                    </tr>
                    <tr>
                        <td>Subject:</td><td style="color: #1569C7;"><b>{subj}</b></td>
                    </tr>
                    <tr>
                        <td>Link:</td><td style="color: #1569C7;"><b>{link}</b></td>
                    </tr>
                    <tr>
                        <td>Transmittal Date:</td><td style="color: #1569C7;"><b>{trans_date}</b></td>
                    </tr>
                    <tr>
                        <td>Reply required:</td><td style="color: #1569C7;"><b>{ans_required}</b></td>
                    </tr>
                    <tr>
                        <td>Due Date:</td><td style="color: #1569C7;"><b>{reply_date}</b></td>
                    </tr>
                    <tr>
                        <td>Originator:</td><td style="color: #1569C7;"><b>{author}</b></td>
                    </tr>
                    <tr>
                        <td>Responsible Employee:</td><td style="color: #1569C7;"><b>{responsible}</b></td>
                    </tr>
                    <tr>
                        <td>Notes:</td><td style="color: #1569C7;"><b>{notes}</b></td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)

                # l_prev.markdown(f"""
                #             Project:
                #
                #             Transmittal Number:
                #
                #             In reply to:
                #
                #             Transmittal Type:
                #
                #             Subject:
                #
                #             Link:
                #
                #             Transmittal Date:
                #
                #             Reply required:
                #
                #             Due Date:
                #
                #             Originator:
                #
                #             Responsible Employee:
                #
                #             Notes:
                #             """)
                #
                # r_prev.markdown(f"""
                #             **:blue[{project}]**
                #
                #             **:blue[{trans_num}]**
                #
                #             **:blue[{ref_trans}]**
                #
                #             **:blue[{t_type}]**
                #
                #             **:blue[{subj}]**
                #
                #             **:blue[{link}]**
                #
                #             **:blue[{trans_date}]**
                #
                #             **:blue[{ans_required}]**
                #
                #             **:blue[{reply_date}]**
                #
                #             **:blue[{author}]**
                #
                #             **:blue[{responsible}]**
                #
                #             **:blue[{notes}]**
                #             """)
            status = "Issued Docs" if t_type == "Design Docs" else "Open"

            if st.button('Add to DataBase'):
                reply = add_new_trans(project, trans_num, ref_trans, t_type, subj, link, trans_date, ans_required,
                                      reply_date, author, responsible, notes, status)
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


