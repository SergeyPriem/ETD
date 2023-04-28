# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from utilities import trans_types, get_cur_u_id
from projects import add_new_trans, get_trans_for_preview
from users import get_logins_for_current

def det_trans_from_df(login=None):
    u_id = get_cur_u_id()
    trans_df = st.session_state.adb['trans']

    proj_df = st.session_state.adb['project']
    u_df = st.session_state.adb['users']

    if login:
        trans_df = trans_df[trans_df.responsible == u_id]

    trans_df = trans_df.merge(proj_df[['short_name']], how='left', left_on="project", right_on='id')
    trans_df = trans_df.merge(u_df[['login']], how='left', left_on="responsible", right_on='id')
    trans_df = trans_df.merge(u_df[['login']], how='left', left_on="responsible", right_on='id')
    trans_df.project = trans_df.short_name
    trans_df.responsible = trans_df.login_x
    trans_df.users = trans_df.login_y

    trans_df = trans_df.drop(columns=['short_name', 'login_x', 'login_y'])
    trans_df.rename(columns={'users': 'Added By'}, inplace=True)

    return trans_df


def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1, 15, 1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()

    with tr_content:
        st.markdown("""
            <style>
                div[data-testid="column"]:nth-of-type(1)
                {
                    text-align: center;
                } 

                div[data-testid="column"]:nth-of-type(2)
                {
                    text-align: center;
                } 

                div[data-testid="column"]:nth-of-type(3)
                {
                    text-align: center;
                } 
            </style>
            """, unsafe_allow_html=True)

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
                responsible = cc.selectbox("Responsible Employee", st.session_state.appl_logins)
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

            if t_type == "Design Docs":
                status = "Issued Docs"
                in_out = "Out"
            else:
                status = "Open"
                in_out = "In"


            if st.button('Add to DataBase'):
                reply = add_new_trans(project, trans_num, ref_trans, t_type, subj, link, trans_date, ans_required,
                                      reply_date, author, responsible, notes, status, in_out)
                # reporter(reply)
                st.info(reply)

        with view_trans_tab:
            my_all_tr = st.radio("Select the Option", ["My Transmittals", 'All Transmittals'], horizontal=True)

            if my_all_tr == "My Transmittals":
                user_login = st.session_state.user
            else:
                user_login = None

            # u_id = get_cur_u_id()

            # df = get_trans_for_preview(user_login)
            df = det_trans_from_df(user_login)

            if isinstance(df, pd.DataFrame):
                if len(df) > 0:
                    st.subheader(f"{my_all_tr}: {len(df)}")
                    st.write(df)
                else:
                    st.info("No Tansmittals in DataBase")
                    st.stop()


