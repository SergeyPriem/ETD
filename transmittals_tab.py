# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from utilities import TRANS_TYPES, center_style, update_state, get_list_index, \
    TRANS_STATUSES  # , make_short_delay, make_long_delay
from projects import add_new_trans, update_trans


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
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('', help='Эта страница для регистрации :orange[Входящих и Исходящих Трансмитталов] \n'
                         '***'
                         '\n'
                         'This page is for :orange[Incoming and Outgoing Transmittals registration]')

    with tr_content:

        st.title(':orange[Transmittals]')

        add_trans_tab, view_trans_tab, edit_trans_tab = st.tabs(
            ['Add New Transmittal', 'View Existing Transmittals', 'Edit Existing Transmittals'])

        with add_trans_tab:

            proj_list = st.session_state.proj_names

            responsible_list = st.session_state.appl_logins

            with st.form("add_trans"):
                lc, cc, rc = st.columns([5, 4, 4], gap='medium')
                project = lc.selectbox("Project *", proj_list)
                # t_type = lc.radio("Transmittal Type *", TRANS_TYPES, horizontal=True)
                trans_date = lc.date_input("Transmittal Date *")

                lc.write("")
                with lc:
                    t_type = option_menu(None,
                                         TRANS_TYPES,
                                         icons=["-", "-", "-", "-", "-", "-"],
                                         default_index=0,
                                         orientation='horizontal')


                ref_trans = rc.text_input("Previous Transmittal",
                                          help=":blue[Номер трансмиттала, на который получен текущий ответ] \n"
                                          "***"
                                          "\n :blue[Transmittal to which a current response was received]"
                                          )
                trans_num = cc.text_input("Transmittal Number *", max_chars=50)
                subj = cc.text_input("Subject *", max_chars=255)
                # ans_required = cc.radio("Our Reply Required *", ('Yes', 'No'), horizontal=True)

                cc.write("")
                with cc:
                    ans_required = option_menu(None,
                                               ["Is our reply requited:", "Yes", "No"],
                                               icons=['-', '-', '-'],
                                               default_index=1,
                                               orientation='horizontal')

                responsible = cc.selectbox("Responsible Employee *", responsible_list)
                cc.write("")
                link = rc.text_input("Link *", max_chars=200)
                rc.write('')
                rc.write('')
                reply_date = rc.date_input("Due Date")
                notes = rc.text_input('Notes', max_chars=500)

                author = lc.text_input('Originator of the Transmittal *', max_chars=50)

                l_c, r_c = st.columns([1, 9], gap='medium')
                l_c.write(':red[\* - required]')
                add_trans_but = r_c.form_submit_button("Preview Transmittal's Data", use_container_width=True)

            if add_trans_but:

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
                            <td>Our Reply Required:</td><td style="color: #1569C7;"><b>{ans_required}</b></td>
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

            if ans_required == "Is our reply requited:":
                st.write("Select is answer required or not...")
                st.stop()

            ans_required_num = 1 if ans_required == "Yes" else 0

            if t_type == "Design Docs":
                status = "Issued Docs"
                in_out = "Out"
            else:
                status = "Open"
                in_out = "In"

            if st.button('Add to DataBase', use_container_width=True):

                trans_checker = check_trans_data(project, trans_num, t_type, subj, link, author, responsible, status)

                if trans_checker:

                    l_col, r_col = st.columns([2, 1], gap='medium')

                    reply = add_new_trans(project, trans_num, ref_trans, t_type, subj, link, trans_date,
                                          ans_required_num, reply_date, author, responsible, notes, status, in_out)
                    l_col.success(reply)

                    r_col.text('')
                    r_col.button('Close Report', key='close_trans_report', use_container_width=True)

                    reply3 = update_state('trans')

                    if reply3 != 'Data is updated':
                        st.warning(reply3)
                        st.stop()

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
                    st.dataframe(df)
                else:
                    st.info("No Tansmittals in DataBase")
                    st.stop()

        with edit_trans_tab:
            l_col, r_col = st.columns(2, gap='medium')
            proj = l_col.selectbox('Select the Project', st.session_state.proj_names)

            if proj != '-- Type right here or select from list --':
                trans_df = st.session_state.adb['trans']
                proj_df = st.session_state.adb['project']
                proj_id = proj_df.loc[proj_df.short_name == proj].index.to_numpy()[0]
                u_df = st.session_state.adb['users']

                # st.experimental_show(proj_id)
                # st.experimental_show(trans_df.project)

                if st.session_state.user['access_level'] == 'performer':
                    trans_list = trans_df.loc[(trans_df.project == proj_id) & (
                            trans_df.responsible == st.session_state.user['id']), 'trans_num'].tolist()
                else:
                    trans_list = trans_df.loc[(trans_df.project == proj_id), 'trans_num'].tolist()
                # st.experimental_show(trans_list)

                if len(trans_list):

                    selected_trans = r_col.selectbox('Select Transmittal to edit', trans_list)
                    sel_trans_df = trans_df[trans_df.trans_num == selected_trans]

                    sel_trans_id = sel_trans_df.index.to_numpy()[0]

                    sel_trans_type = sel_trans_df.t_type.to_numpy()[0]

                    sel_trans_dict = sel_trans_df.to_dict('records')[0]

                    old_responsible = u_df.loc[u_df.index == sel_trans_dict['responsible'], 'login'].to_numpy()[0]

                    # st.experimental_show(sel_trans_df)
                    # st.experimental_show(old_responsible)
                    # st.experimental_show(sel_trans_dict)
                    # st.experimental_show(st.session_state.appl_logins)
                    # st.experimental_show(get_list_index(st.session_state.appl_logins, old_responsible))

                    with st.form('edit_trans'):
                        lc, rc = st.columns(2, gap='medium')
                        trans_date = lc.date_input('Transmittal Date', value=sel_trans_dict['trans_date'])
                        responsible = rc.selectbox('Responsible', st.session_state.appl_logins,
                                                   index=get_list_index(
                                                       st.session_state.appl_logins, old_responsible
                                                       )
                                                   )
                        author = lc.text_input('Originator of the Transmittal', value=sel_trans_dict['author'])
                        in_reply_to = lc.text_input('Previous Transmittal', value=sel_trans_dict['ref_trans'])
                        subj = rc.text_input('Subject', value=sel_trans_dict['subj'])
                        ref_date = rc.date_input('Previous Transmittal Date', value=sel_trans_dict['ref_date'])
                        link = lc.text_input('Link', value=sel_trans_dict['link'])
                        rc.text('')
                        t_type = rc.radio('Transmittal Type', TRANS_TYPES,
                                          index=get_list_index(TRANS_TYPES, sel_trans_type), horizontal=True)
                        prev_ans_req = 'Yes' if sel_trans_dict['ans_required'] == 1 else "No"

                        upd_ans_required = lc.radio('Our Reply Required', options=["Yes", "No"],
                                                    index=get_list_index(["Yes", "No"], prev_ans_req),
                                                    horizontal=True)
                        upd_status = rc.radio('Status', TRANS_STATUSES,
                                              index=get_list_index(TRANS_STATUSES, sel_trans_dict['status']),
                                              horizontal=True)
                        upd_trans_but = st.form_submit_button('Update Transmittal Data', use_container_width=True)

                    if upd_trans_but:
                        responsible_id = u_df[u_df.login == responsible].index.to_numpy()[0]
                        fin_ans_req = 1 if upd_ans_required == "Yes" else 0

                        reply = update_trans(sel_trans_id, trans_date, responsible_id, author, in_reply_to,
                                             ref_date, subj, link, t_type, fin_ans_req, upd_status)

                        if reply['status'] == 201:
                            l_rep, r_rep = st.columns(2, gap='medium')
                            reply3 = update_state('trans')

                            if reply3 != 'Data is updated':
                                st.warning(reply3)

                            l_rep.success('Transmittal Updated')
                            r_rep.text('')
                            r_rep.button('Close Report', key='close_upd_unit_report', use_container_width=True)
                        else:
                            st.error(reply['err_descr'])

                else:
                    st.warning('Transmittals for selected Project are not available...')































