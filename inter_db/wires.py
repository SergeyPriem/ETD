# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

# def delete_wires(wires_to_del):
#     st.session_state.intercon['wire'] = \
#         st.session_state.intercon['wire'][~st.session_state.intercon['wire'].wire_uniq.isin(wires_to_del)]
#     st.experimental_rerun()
#
# def add_wires(act_cable, wires_to_add):
#     wire_df = st.session_state.intercon['wire']
#
#     df2 = pd.DataFrame()
#     last_ind = 0
#     try:
#         last_num = int(wire_df.loc[wire_df.cab_tag == act_cable, 'wire_num'].max())
#     except:
#         last_num = 0
#
#     if not last_num or not isinstance(last_num, int):
#         last_num = 0
#
#     for w in range(0, wires_to_add):
#         wire_num = last_num + w + 1
#         df2.loc[last_ind + w, ["cab_tag", 'term_num_left', 'wire_num', 'term_num_right', 'wire_uniq', 'wire_to_del']] = \
#             [act_cable, 0, wire_num, 0, str(act_cable) + ":" + str(wire_num), False]
#
#     st.session_state.intercon['wire'] = pd.concat([st.session_state.intercon['wire'], df2])
#     st.session_state.intercon['wire'] = st.session_state.intercon['wire'].reset_index(drop=True)
#     st.experimental_rerun()
#
#
# def order_of_wires(df):
#     checked_list = df.wire_num.tolist()
#
#     if not (int(min(checked_list)) == 1 and int(max(checked_list)) == len(
#             checked_list) and len(checked_list) == len(set(checked_list))):
#         st.write("#### :red[Wire numbers not in order...]")
#         st.stop()
#
#
# def both_side_connection(df):
#     checker = True
#     df_left = df[df.full_term_tag_left != 'nan:0']
#     df_right = df[df.full_term_tag_right != 'nan:0']
#
#     if len(df_left) != len(df_right):
#         st.write(":red[Left and right connections quantity is different...]")
#         # st.button("Fix and save - OK", key='"Fix_and_save-OK"')
#
#         checker = False
#     # if len filtered left == len filtered right
#     # OK
#
#     for ind, row in df_left.iterrows():
#         if "nan" in row.full_term_tag_left.split(":")[0] or "0" in row.full_term_tag_left.split(":")[-1]:
#             st.write(f":red[Not selected LEFT terminal block or terminal for wire {row.wire_num}]")
#             checker = False
#
#     for ind, row in df_right.iterrows():
#         if "nan" in row.full_term_tag_right.split(":")[0] or "0" in row.full_term_tag_right.split(":")[-1]:
#             st.write(f":red[Not selected RIGHT terminal block or terminal for wire {row.wire_num}]")
#             checker = False
#
#     if not checker:
#         st.write('Fix and save!')
#         st.button("OK")
#         st.stop()
#
#
# def full_tag_duplicates(df):
#     df_left = df[df.full_term_tag_left != 'nan:0']
#     left_len = len(df_left[df_left.full_term_tag_left.duplicated()])
#
#     if left_len:
#         st.write(':red[duplicates in left terminal block]')
#
#     df_right = df[df.full_term_tag_right != 'nan:0']
#     right_len = len(df_right[df_right.full_term_tag_right.duplicated()])
#
#     if right_len:
#         st.write(':red[duplicates in right terminal block. Please fix and try again]')
#
#     if left_len or right_len:
#         st.button("OK")
#         st.stop()
#
#
# def check_wires_df(df):
#     order_of_wires(df)
#
#     for ind, row in df.iterrows():
#         pass
#
#     try:
#         df.wire_num = df.wire_num.astype("int")
#         df.term_num_left = df.term_num_left.astype("int")
#         df.term_num_right = df.term_num_right.astype("int")
#     except Exception as e:
#         st.write(e)
#
#     df.wire_uniq = df.cab_tag.astype('str') + ":" + \
#                    df.wire_num.astype('str')
#
#     df.full_term_tag_left = df.full_block_tag_left.astype('str') + ":" + \
#                             df.term_num_left.astype('str')
#
#     df.full_term_tag_right = df.full_block_tag_right.astype('str') + ":" + \
#                              df.term_num_right.astype('str')
#
#     full_tag_duplicates(df)
#
#     both_side_connection(df)
#
#     st.button("#### :green[Wires saved]")
#
#
# def save_wires(upd_cable_wires_df, act_cable):
#     temp_df = st.session_state.intercon['wire'].copy(deep=True)
#     temp_df = temp_df[temp_df.cab_tag != act_cable]
#
#     st.session_state.intercon['wire'] = pd.concat([temp_df, upd_cable_wires_df])
#     st.session_state.intercon['wire'].reset_index(drop=True, inplace=True)
#
#
# def edit_wires():
#     lc1, lc2, cc, rc = st.columns([2, 1, 1, 2], gap='medium')
#     cab_list = st.session_state.intercon['cable'].loc[:, 'cab_tag'].tolist()
#     # wires_qty_list = st.session_state.intercon['cab_descr'].loc[:, 'wire_quant'].tolist()
#     act_cable = lc1.selectbox('Select Cable for wires connection', cab_list)
#
#     # wire_num = rc.radio('Select Wires Quantity', wires_qty_list, horizontal=True)
#
#     if act_cable:
#         st.subheader(f'Termination Table for Cable :blue[{act_cable}]')
#         wire_df = st.session_state.intercon['wire']
#
#         if len(wire_df):
#
#             current_cable_wires_df = wire_df[wire_df.cab_tag == act_cable]
#
#             wires_to_del = []
#             wires_to_show = []
#
#             cab_df = st.session_state.intercon['cable']
#             block_df = st.session_state.intercon['block']
#
#             left_pan = cab_df.loc[cab_df.cab_tag == act_cable, 'full_pan_tag_left'].to_numpy()[0]
#             right_pan = cab_df.loc[cab_df.cab_tag == act_cable, 'full_pan_tag_right'].to_numpy()[0]
#
#             left_block_list = block_df.loc[block_df.full_pan_tag == left_pan, "full_block_tag"].tolist()
#             right_block_list = block_df.loc[block_df.full_pan_tag == right_pan, "full_block_tag"].tolist()
#
#             if len(current_cable_wires_df):
#                 # st.write(current_cable_wires_df)
#                 upd_cable_wires_df = st.data_editor(
#                     current_cable_wires_df,
#                     column_config={
#                         "cab_tag": st.column_config.TextColumn(
#                             "Cable Tag",
#                             disabled=True,
#                             default=act_cable,
#                         ),
#                         "full_block_tag_left": st.column_config.SelectboxColumn(
#                             "Left Cable Terminal Block",
#                             help="Available terminals at the Left Panel",
#                             width="medium",
#                             options=left_block_list,
#                         ),
#                         "term_num_left": st.column_config.NumberColumn(
#                             "Left Terminal Number",
#                             help="Number of Terminal",
#                             min_value=0,
#                             max_value=250,
#                             width="small",
#                         ),
#                         "wire_num": st.column_config.NumberColumn(
#                             "Number of Wire",
#                             min_value=1,
#                             max_value=100,
#                             width='small',
#                         ),
#
#                         "term_num_right": st.column_config.NumberColumn(
#                             "Right Terminal Number",
#                             help="Number of Terminal",
#                             min_value=0,
#                             max_value=250,
#                             width="small",
#                         ),
#
#                         "full_block_tag_right": st.column_config.SelectboxColumn(
#                             "Right Cable Terminal Block",
#                             help="Available terminals at the Right Panel",
#                             width="medium",
#                             options=right_block_list,
#                         ),
#                         "wire_to_del": st.column_config.CheckboxColumn(
#                             "Delete Wire",
#                             width="small",
#                             default=False
#                         ),
#                         "full_term_tag_left": st.column_config.TextColumn(
#                             width="small",
#                             disabled=True,
#                         ),
#                         "wire_uniq": st.column_config.TextColumn(
#                             width="small",
#                             disabled=True,
#                         ),
#                         "full_term_tag_right": st.column_config.TextColumn(
#                             width="small",
#                             disabled=True,
#                         ),
#                     },
#                     hide_index=True, num_rows='fixed', use_container_width=True)
#
#                 wires_to_del = upd_cable_wires_df.loc[
#                     upd_cable_wires_df.wire_to_del.astype('str') == 'True', 'wire_uniq'].tolist()
#
#                 wires_to_show = upd_cable_wires_df.loc[
#                     upd_cable_wires_df.wire_to_del.astype('str') == 'True', 'wire_num'].tolist()
#                 wires_to_show = [int(x) for x in wires_to_show]
#
#                 if st.button("SAVE TERMINATION TABLE", use_container_width=True):
#                     check_wires_df(upd_cable_wires_df)
#                     save_wires(upd_cable_wires_df, act_cable)
#             else:
#                 st.markdown("#### :blue[Please add wires to the cable]")
#         else:
#             st.markdown("#### :blue[Please add wires to the cable]")
#
#         # rc.text('')
#         rc.text('', help="Select the wires by checkbox 'Delete Wire'")
#         # cc.text('')
#         cc.text('', help="Select wires quantity first. Wires will be numbered in order")
#
#         wires_to_add = lc2.number_input(f'Number of wires to add', min_value=1, max_value=37)
#
#         if cc.button("Add wires", use_container_width=True):
#             add_wires(act_cable, wires_to_add)
#             st.write("##### Wires added")
#
#         if rc.button(f'Delete selected wires {wires_to_show}', use_container_width=True):
#             delete_wires(wires_to_del)
#             st.write("##### Wires deleted")
#     else:
#         st.subheader(f'Select the Cable for Termination')
from pony.orm import db_session, select, delete
from streamlit_option_menu import option_menu

from inter_db.cables import get_filtered_cables
from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.terminals import get_panel_terminals
from models import Wire, Cable
from utilities import err_handler, act_with_warning


def create_wires(cab_tag, wires_num):
    try:
        with db_session:
            cable = Cable.get(cable_tag=cab_tag)
            for w in range(1, wires_num + 1):
                Wire(
                    cable_id=cable,
                    wire_num=w
                )
            st.toast(f"{w} wires created")
    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_wires.clear()
        st.experimental_rerun()


@st.cache_data(show_spinner=False)
def get_filtered_wires(cab_tag):
    try:
        with db_session:
            cab = Cable.get(cable_tag=cab_tag)
            data = select((
                              w.id,
                              w.cable_id.cable_tag,
                              w.wire_num,
                              w.left_term_id,
                              w.right_term_id,
                              w.edit,
                              w.notes,
                          ) for w in Wire if cab == w.cable_id)[:]

        df = pd.DataFrame(data, columns=['id', 'cable_tag', 'wire_num', 'left_term_id', 'right_term_id',
                                         'edit', 'notes', ])
        return df
    except Exception as e:
        st.toast(err_handler(e))


def delete_wires(cab_tag):
    # try:
    # with db_session:
    #     cab = Cable.get(cable_tag=cab_tag)
    #     delete(w for w in Wire if w.cable_id == cab)



    st.toast(f"All wires of {cab_tag} deleted")
    # except Exception as e:
    #     st.toast(err_handler(e))
    # finally:
    #     get_filtered_wires.clear()



def wires_main(act):
    eq_tag_list = list(get_eqip_tags())

    lc1, rc1 = st.columns(2, gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with lc1:
        selected_left_equip = option_menu('Select the Left Side Equipment',
                                          options=eq_tag_list,
                                          icons=['-'] * len(eq_tag_list),
                                          orientation='horizontal',
                                          menu_icon='1-square')

    if selected_left_equip == 'No equipment available':
        st.stop()

    left_pan_tag_list = list(get_panel_tags(selected_left_equip))

    if len(left_pan_tag_list) == 0:
        left_pan_tag_list = 'No panels available'

    with lc1:
        selected_left_panel = option_menu('Select the Left Side Panel',
                                          options=left_pan_tag_list,
                                          icons=['-'] * len(left_pan_tag_list),
                                          orientation='horizontal', menu_icon='2-square')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with rc1:
        selected_right_equip = option_menu('Select the Right Side Equipment',
                                           options=eq_tag_list,
                                           icons=['-'] * len(eq_tag_list),
                                           orientation='horizontal',
                                           menu_icon='3-square')

    if selected_right_equip == 'No equipment available':
        st.stop()

    right_pan_tag_list = list(get_panel_tags(selected_right_equip))

    if len(right_pan_tag_list) == 0:
        right_pan_tag_list = 'No panels available'

    with rc1:
        selected_right_panel = option_menu('Select the Right Side Panel',
                                           options=right_pan_tag_list,
                                           icons=['-'] * len(right_pan_tag_list),
                                           orientation='horizontal', menu_icon='4-square')

    cab_df = get_filtered_cables(selected_left_equip, selected_left_panel, selected_right_equip, selected_right_panel)

    cab_tag_list = cab_df.cable_tag.tolist()

    if isinstance(cab_df, pd.DataFrame):
        cab_tag_list = cab_df.cable_tag.tolist()
    else:
        st.toast(cab_tag_list)
        st.stop()

    if len(cab_tag_list) == 0:
        cab_tag_list = ['No cables available']

    cab_tag = option_menu('Select the Cable',
                          options=cab_tag_list,
                          icons=['-'] * len(cab_tag_list),
                          orientation='horizontal', menu_icon='5-square')

    if cab_tag:

        st.write(":blue[Selected Cable Details]")
        st.data_editor(cab_df[cab_df.cable_tag == cab_tag], use_container_width=True)

        df = get_filtered_wires(cab_tag)

        data_to_show = None

        if isinstance(df, pd.DataFrame):

            if len(df):

                left_terminals = get_panel_terminals(selected_left_equip, selected_left_panel)
                right_terminals = get_panel_terminals(selected_right_equip, selected_right_panel)
                st.write(":blue[Wires Details]")
                data_to_show = st.data_editor(df,
                                              column_config={
                                                  "id": st.column_config.NumberColumn(
                                                      "ID",
                                                      width='small'
                                                  ),
                                                  "cable_tag": st.column_config.TextColumn(
                                                      "Cable Tag",
                                                      width='mediun',
                                                      disabled=True
                                                  ),
                                                  "wire_num": st.column_config.NumberColumn(
                                                      "Wire's Number",
                                                      width='small',
                                                  ),
                                                  "left_term_id": st.column_config.SelectboxColumn(
                                                      "Left Terminal",
                                                      options=left_terminals,
                                                      width='large',
                                                  ),
                                                  "right_term_id": st.column_config.SelectboxColumn(
                                                      "Right Terminal",
                                                      options=right_terminals,
                                                      width='large',
                                                  ),
                                                  "edit": st.column_config.CheckboxColumn(
                                                      "Edit",
                                                      width='small'),
                                                  "notes": st.column_config.TextColumn(
                                                      "Notes",
                                                      width='large'
                                                  )
                                              },
                                              use_container_width=True, hide_index=True, key='wires_df')

            else:
                data_to_show = st.write(f"#### :blue[Wires of cable {cab_tag} not available ...]")

        else:
            st.write(f"#### :blue[No wires available for selected Cable...]")
            st.stop()

        if act == 'Create':
            data_to_show
            if st.button('Create Wires'):
                create_wires(cab_tag, cab_df.loc[cab_df.cable_tag == cab_tag, 'wire'].to_numpy()[0])

        if act == 'View':
            data_to_show

        if act == 'Delete':
            data_to_show
            if st.button("Delete All Wires"):
                act_with_warning(
                    left_function=delete_wires,
                    left_args=cab_tag,
                    header_message="All wires will and their connections will be deleted!"
                )
                st.write("RETURNED from DEL")

        if act == 'Edit':
            edited_df = data_to_show
            # if st.button("Edit Selected Wires"):
            #     edit_wires(edited_df, cab_tag)
    else:
        st.write(f"#### :blue[Select Cable Tag to proceed...]")
