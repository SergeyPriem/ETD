# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from utilities import trans_types, center_style, update_state #, make_short_delay, make_long_delay
from projects import add_new_trans


def check_trans_data(project, trans_num, t_type, subj, link,
                     author, responsible, in_out):
    if project == '-- Type right here or select from list --' or\
            responsible == '-- Type right here or select from list --':
        st.info('Make proper selection...')
        st.stop()

    variables = (project, trans_num, t_type, subj, link, author, responsible, in_out)
    names = ("Project", "Transmittal Number", "Transmittal Type", "Subject", "Link",
             "Originator of the Transmittal", "responsible", "in_out")

    field_dict = dict(zip(names, variables))

    check_sum = 0
    for k, v in field_dict.items():
        if len(v) < 2:
            st.markdown(f"The field :red['{k}'] is too short...")
            check_sum += 1

    if check_sum > 0:
        return False
    else:
        return True


def det_trans_from_df(login=None):
    trans_df = st.session_state.adb['trans']

    proj_df = st.session_state.adb['project']
    u_df = st.session_state.adb['users']

    if login:
        trans_df = trans_df[trans_df.responsible == st.session_state.user['id']]

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

    # make_short_delay()

    center_style()

    tr_empty1, tr_content, tr_empty2 = st.columns([1, 15, 1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()

    with tr_content:

        st.title(':orange[Transmittals]')

        add_trans_tab, view_trans_tab = st.tabs(['Add New Transmittal', 'View Existing Transmittals'])

        with add_trans_tab:

            proj_list = st.session_state.proj_names
            if '-- Type right here or select from list --' not in proj_list:
                proj_list.insert(0, '-- Type right here or select from list --')

            responsible_list = st.session_state.appl_logins

            if '-- Type right here or select from list --' not in responsible_list:
                responsible_list.insert(0, '-- Type right here or select from list --')

            with st.form("add_trans"):
                lc, cc, rc = st.columns([5, 4, 4], gap='medium')
                project = lc.selectbox("Project", proj_list)
                t_type = lc.radio("Transmittal Type", trans_types, horizontal=True)
                lc.write("")
                ref_trans = rc.text_input("In reply to")
                trans_num = cc.text_input("Transmittal Number", max_chars=50)
                subj = cc.text_input("Subject", max_chars=255)
                ans_required = cc.radio("Reply required", ('Yes', 'No'), horizontal=True)
                cc.write("")
                responsible = cc.selectbox("Responsible Employee", responsible_list)
                cc.write("")
                link = rc.text_input("Link", max_chars=200)
                reply_date = rc.date_input("Due Date")
                notes = rc.text_input('Notes', max_chars=500)
                trans_date = lc.date_input("Transmittal Date")
                author = lc.text_input('Originator of the Transmittal', max_chars=50)

                add_trans_but = st.form_submit_button("Preview Transmittal's Data", use_container_width=True)

            if add_trans_but:

                # make_long_delay()

                if project != '-- Type right here or select from list --':
                    # l_prev, r_prev = st.columns([1, 8])

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

                else:
                    st.info('Make proper selection...')
                    st.stop()

            if t_type == "Design Docs":
                status = "Issued Docs"
                in_out = "Out"
            else:
                status = "Open"
                in_out = "In"

            if st.button('Add to DataBase', use_container_width=True):

                trans_checker = check_trans_data(project, trans_num, t_type, subj, link, author, responsible, status)

                if trans_checker:

                    reply = add_new_trans(project, trans_num, ref_trans, t_type, subj, link, trans_date, ans_required,
                                          reply_date, author, responsible, notes, status, in_out)
                    st.info(reply)

                    reply3 = update_state('trans')

                    if reply3 != 'Data is updated':
                        st.warning(reply3)
                        st.stop()

                    # make_short_delay()

                else:
                    st.warning("Please Update fields properly...")

        with view_trans_tab:
            my_all_tr = st.radio("Select the Option", ["My Transmittals", 'All Transmittals'], horizontal=True)

            if my_all_tr == "My Transmittals":
                user_login = st.session_state.user['login']
            else:
                user_login = None

            df = det_trans_from_df(user_login)

            if isinstance(df, pd.DataFrame):
                if len(df) > 0:
                    st.subheader(f"{my_all_tr}: {len(df)}")
                    st.write(df)
                else:
                    st.info("No Tansmittals in DataBase")
                    st.stop()
