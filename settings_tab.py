# -*- coding: utf-8 -*-
import random

import streamlit as st
from st_btn_group import st_btn_group
from streamlit_option_menu import option_menu

from admin_tools import get_list_index
from models import Users
from projects import get_table, get_all
from send_emails import send_mail
from users import update_settings, update_user_reg_data
from utilities import center_style, update_tables


def settings_content():
    center_style()
    empty1_set, content_set, empty2_set = st.columns([1, 2, 1])
    with empty1_set:
        st.empty()
    with empty2_set:
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('')
        st.text('', help=':blue[Эта страница предназначена для настроек более комфортного использования Приложения. '
                         'Можно настроить:] \n'
                         '- расположение Главного Меню\n'
                         '- объем загрузки данных из базы (все проекты, текущие, или все кроме отмененных и '
                         'остановленных)\n'
                         '- сменить пароль пользователя \n'
                         '***'
                         '\n'
                         ':blue[This page is intended for settings for more comfortable use of the Application. \n'
                         'Available settings:] \n'
                         '- main menu location \n'
                         '- amount of data downloaded from the database (all projects, current, or '
                         'all except canceled and suspended) \n'
                         '- change user password')

    with content_set:

        st.title(':orange[Settings]')

        menu_pos_tab, scope_tab, change_pass_tab = st.tabs(['Menu Position', 'Scope of Load', 'Change Password'])

        with menu_pos_tab:
            with st.form('adjust_settings'):
                l_f, r_f = st.columns(2)

                # menu_position = l_f.radio('Location of menu', ("Top", "Left"),
                #                           index=st.session_state.user['vert_menu'], horizontal=True)
                # r_f.write('')

                buttons = [
                    {"label": "Left of the Screen",
                     "value": "Left",
                     },
                    {"label": "Top of the Screen",
                     "value": "Top",
                     },
                ]

                with l_f:
                    # menu_position = st_btn_group(buttons=buttons, key="1", shape='default', size='compact',
                    #                              align='center', disabled=False, merge_buttons=False,
                    #                              gap_between_buttons=44, display_divider=False, return_value=False)

                    menu_position = option_menu(None, ['Left Side', 'Top Side'], icons=['arrow-left', 'arrow-up', ],
                                                orientation="horizontal")

                appl_upd_set_but = r_f.form_submit_button('Apply menu position', use_container_width=True)

            if appl_upd_set_but:
                if menu_position == 'Left Side':
                    st.session_state.user['vert_menu'] = 1
                else:
                    st.session_state.user['vert_menu'] = 0

                reply = update_settings(st.session_state.user['login'], st.session_state.user['vert_menu'])
                st.session_state.adb['users'] = get_table(Users)
                st.success(reply)
                st.experimental_rerun()

        with scope_tab:
            with st.form('change_scope'):
                l_c, r_c = st.columns([2, 1], gap='medium')
                scope = l_c.radio("Choose the Preferred Scope loaded from DB",
                                  ['Only Current Projects', 'All Projects', 'All excluding cancelled and suspended'],
                                  index=get_list_index(
                                      ['Only Current Projects', 'All Projects',
                                       'All excluding cancelled and suspended'],
                                      st.session_state.proj_scope
                                  ),
                                  help=":green[Only Current Projects] is preferable for speed of Application "
                                       "and Memory Usage",
                                  horizontal=True)
                r_c.text("")
                scope_conf_but = r_c.form_submit_button('Apply Selected Scope', use_container_width=True)

            if scope_conf_but:
                st.session_state.proj_scope = scope
                st.session_state.adb = get_all()
                st.success('Settings Updated')

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

                    receiver = st.session_state.user['email']
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
                        reply = update_user_reg_data(st.session_state.user['login'], upd_pass_2)
                        st.info(reply)
                else:
                    st.write("After pressing 'Get Confirmation Code' you will get Confirmation Code by e-mail")
                    st.write("Enter the Code and press 'Update Password'")
