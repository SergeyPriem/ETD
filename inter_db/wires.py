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
from pony.orm import db_session, select

from inter_db.cables import get_cab_tags, get_cab_panels
from models import Wire, Cable
from utilities import err_handler


def select_filtered_wires(cab_tag):
    try:
        with db_session:
            cab = Cable.get(cable_tag=cab_tag)
            data = select((
                w.id,
                w.cable_id.cable_tag,
                w.wire_num,
                w.left_term_id.terminal_un,
                w.right_term_id.terminal_un,
                w.edit,
                w.notes,
                ) for w in Wire if cab == w.cable_id)[:]

        df = pd.DataFrame(data, columns=['id', 'cable_tag', 'wire_num', 'left_term_id', 'right_term_id',
                                         'edit', 'notes',])
        return df
    except Exception as e:
        st.toast(err_handler(e))


def wires_main(act):
    cab_tag_list = get_cab_tags()
    l, c, r = st.columns(3, gap='medium')
    cab_tag = c.selectbox("Cable Tag", cab_tag_list)

    if cab_tag:
        cab_pan_left, cab_pan_right = get_cab_panels(cab_tag)
        l.write(f": orange[Left Panel: {cab_pan_left}]")
        r.write(f": orange[Right Panel: {cab_pan_right}]")

        df = select_filtered_wires(cab_tag)

        if isinstance(df, pd.DataFrame):
            if len(df):
                data_to_show = st.data_editor(df, use_container_width=True, hide_index=True, key='wires_df')
            else:
                data_to_show = st.write(f"#### :blue[Wires of cable {cab_tag} not available ...]")

        if act == 'Create':
            data_to_show
            # create_w_con(cab_tag)

        if act == 'View':
            data_to_show

        if act == 'Delete':
            edited_df = data_to_show
            # if st.button("Delete Equipment"):
            #     delete_w_con(edited_df, cab_tag)

        if act == 'Edit':
            edited_df = data_to_show
            # if st.button("Edit Selected Cables"):
            #     edit_w_con(edited_df, cab_tag)
    else:
        st.write(f"#### :blue[Select Cable Tag to proceed...]")

