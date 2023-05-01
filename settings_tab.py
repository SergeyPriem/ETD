# -*- coding: utf-8 -*-
import streamlit as st
import random

from admin_tools import get_list_index
from models import Users
from projects import get_table, get_all
from send_emails import send_mail
from users import update_settings, update_user_reg_data


def settings_content():
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

    empty1_set, content_set, empty2_set = st.columns([1, 4, 1])
    with empty1_set:
        st.empty()
    with empty2_set:
        st.empty()

    with content_set:

        st.title(':orange[Settings]')
        st.write('This page is intended to make some adjustments for more comfortable use of Application')

        menu_pos_tab, scope_tab, change_pass_tab = st.tabs(['Menu Position', 'Scope of Load', 'Change Password'])

        with menu_pos_tab:
            with st.form('adjust_settings'):
                l_f, r_f = st.columns(2)

                menu_position = l_f.radio('Location of menu', ("Top", "Left"),
                                          index=st.session_state.vert_menu, horizontal=True)
                r_f.write('')

                appl_set_but = r_f.form_submit_button('Apply menu position', use_container_width=True)

            if appl_set_but:
                if menu_position == 'Left':
                    st.session_state.vert_menu = 1
                else:
                    st.session_state.vert_menu = 0

                update_settings(st.session_state.user, st.session_state.vert_menu)
                st.session_state.adb['users'] = get_table(Users)
                st.experimental_rerun()

        with scope_tab:
            with st.form('change_scope'):
                l_c, r_c = st.columns(2, gap='medium')
                scope = l_c.radio("Choose the Preferred Scope loaded from DB",
                                 ['Only Current Projects', 'All Projects', 'All excluding cancelled and suspended'],
                                 index=get_list_index(
                                     ['Only Current Projects', 'All Projects', 'All excluding cancelled and suspended'],
                                     st.session_state.proj_scope
                                 ),
                                 horizontal=True)
                scope_conf_but = r_c.form_submit_button('Apply Selected Scope', use_container_width=True)

            if scope_conf_but:
                st.session_state.proj_scope = scope
                st.session_state.adb = get_all()

        with change_pass_tab:
            with st.form("UpData"):

                upd_pass_1 = st.text_input('Updated Password', type='password', key='upd_pass_1',
                                           disabled=not st.session_state.logged)
                upd_pass_2 = st.text_input('Repeat Updated Password', type='password', key='upd_pass_2',
                                           disabled=not st.session_state.logged)

                get_conf_code = st.form_submit_button("Get Confirmation Code", use_container_width=True)

            if get_conf_code:
                if (len(upd_pass_1) < 3) or (upd_pass_1 != upd_pass_2):
                    st.warning("""❗ Password should be at least 3 symbols  
                        ❗ Password and Repeat Password should be the same""")
                    st.stop()

                if 'upd_conf_num' not in st.session_state:
                    st.session_state.upd_conf_num = "".join(random.sample("123456789", 4))

                upd_html = f"""
                        <html>
                          <head></head>
                          <body>
                            <h3>
                              Hello, Colleague!
                              <hr>
                            </h3>
                            <h5>
                              You got this message because you want to update your data on ETD site
                            </h5>
                            <p>
                                Please confirm your registration by entering the confirmation code 
                                <b>{st.session_state.upd_conf_num}</b> 
                                at the <a href="https://e-design.streamlit.app/">site</a> Update form
                                <hr>
                                Best regards, Administration 😎
                            </p>
                          </body>
                        </html>
                    """

                if not st.session_state.upd_code_sent:
                    u_df = st.session_state.adm['users']
                    receiver = u_df[u_df.login == st.session_state.user].email.to_numpy()[0]
                    email_sent = send_mail(receiver=receiver,
                                           cc_rec="sergey.priemshiy@uzliti-en.com",
                                           html=upd_html, subj="Confirmation of Data Update on ETD site")
                    if email_sent == 200:
                        st.session_state.upd_code_sent = True
                    else:
                        st.session_state.upd_code_sent = False
                        st.write("Confirmation code is not send. Refresh the page and try again")

                update_pass = None
                if st.session_state.upd_code_sent is True:
                    with st.form('pass_confirm'):
                        entered_upd_code = st.text_input("Confirmation Code from Email")
                        update_pass = st.form_submit_button("Update Password")

                if update_pass:
                    if st.session_state.upd_conf_num != entered_upd_code:
                        st.warning("Confirmation code is wrong, try again")
                        st.stop()
                    else:
                        reply = update_user_reg_data(st.session_state.user, upd_pass_2)
                        st.info(reply)
                else:
                    st.write("After pressing 'Get Confirmation Code' you will get Confirmation Code by e-mail")
                    st.write("Enter the Code and press 'Update Password'")
