# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.cables import get_filtered_cables
from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.utils import get_panel_terminals

from models import Wire, Cable, Block, Terminal
from utilities import err_handler, act_with_warning


@st.cache_data(show_spinner=False)
def get_filtered_wires(cab_tag):
    try:
        with db_session:
            data = select((
                              w.id,
                              w.cable_id.cable_tag,
                              w.wire_num,
                              str(w.left_term_id.block_id.block_tag) + " : " + str(w.left_term_id.terminal_num),
                              str(w.right_term_id.block_id.block_tag) + " : " + str(w.right_term_id.terminal_num),
                              w.edit,
                              w.notes,
                          ) for w in Wire if w.cable_id.cable_tag == cab_tag)[:]

            df = pd.DataFrame(data, columns=['id', 'cable_tag', 'wire_num', 'left_term_id', 'right_term_id',
                                             'edit', 'notes', ])
        return df
    except Exception as e:
        return err_handler(e)


def edit_wires(edited_df, cab_tag, all_wires=False):
    if all_wires:
        df = edited_df
    else:
        df = edited_df[edited_df.edit.astype('str') == "True"]

    i = 0
    try:
        with db_session:
            for ind, row in df.iterrows():

                j = 0
                if " : " in row.left_term_id:
                    left_ful_term = row.left_term_id.split(" : ")
                else:
                    j += 1
                    st.toast(f"Wrong Left terminal for wire {row.wire_num}")

                if " : " in row.right_term_id:
                    right_ful_term = row.right_term_id.split(" : ")
                else:
                    j += 1
                    st.toast(f"Wrong Left terminal for wire {row.wire_num}")

                if j > 0:
                    continue

                if len(left_ful_term) == 2 and len(right_ful_term) == 2:

                    wire = Wire[row.id]
                    left_panel = Cable.get(cable_tag=cab_tag).left_pan_id
                    right_panel = Cable.get(cable_tag=cab_tag).right_pan_id

                    left_block_tag = left_ful_term[0]
                    right_block_tag = right_ful_term[0]

                    left_term_num = left_ful_term[1]
                    right_term_num = right_ful_term[1]

                    left_block = select(b for b in Block
                                        if b.block_tag == left_block_tag and b.pan_id == left_panel).first()
                    right_block = select(b for b in Block
                                         if b.block_tag == right_block_tag and b.pan_id == right_panel).first()

                    left_term = select(t for t in Terminal
                                       if t.block_id == left_block and t.terminal_num == left_term_num).first()
                    right_term = select(t for t in Terminal
                                        if t.block_id == right_block and t.terminal_num == right_term_num).first()
                    wire.set(
                        left_term_id=left_term.get_pk(),
                        right_term_id=right_term.get_pk(),
                        notes=row.notes
                    )
                    i += 1
                else:
                    st.toast(f"##### :red[Wrong terminals for wire {row.wire_num}]")
            st.toast(f"##### :green[{i} wires updated]")
    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_wires.clear()
        st.experimental_rerun()


def create_wires(cab_tag, wires_num, left_term_init, right_term_init):
    try:
        with db_session:
            cable = Cable.get(cable_tag=cab_tag)

            left_block = left_term_init.split(" : ")[0]
            left_term = left_term_init.split(" : ")[1]

            right_block = right_term_init.split(" : ")[0]
            right_term = right_term_init.split(" : ")[1]

            left_term_first = select(t for t in Terminal
                                     if t.block_id.block_tag == left_block and t.terminal_num == left_term).first()
            right_term_first = select(t for t in Terminal
                               if t.block_id.block_tag == right_block and t.terminal_num == right_term).first()

            for w in range(1, wires_num + 1):
                Wire(
                    cable_id=cable,
                    wire_num=w,
                    left_term_id=left_term_first,
                    right_term_id=right_term_first,
                )

            st.toast(f"##### :green[{w} wires created]")
    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_wires.clear()
        st.experimental_rerun()


def delete_wires(cab_tag):
    try:
        with db_session:
            wires = select(w for w in Wire if w.cable_id.cable_tag == cab_tag)[:]
            for w in wires:
                w.delete()
            st.toast(f"##### :green[All wires of {cab_tag} deleted]")
    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_filtered_wires.clear()
        st.experimental_rerun()


def check_dulicated_terminals(df):
    i=0
    left_series = df.left_term_id
    right_series = df.right_term_id

    left_dup = left_series[left_series.duplicated(keep="first")].tolist()
    right_dup = right_series[right_series.duplicated(keep="first")].tolist()
    lc, rc = st.columns(2)
    if len(left_dup) > 0:
        lc.write("##### :red[Duplicates found in left termination]")
        lc.write(left_dup)
    if len(right_dup) > 0:
        rc.write("##### :red[Duplicates found in right termination]")
        rc.write(right_dup)

    if len(left_dup) > 0 or len(right_dup) > 0:
        for l in left_dup:
            if "999" not in l:
                i += 1
        for r in right_dup:
            if "999" not in r:
                i += 1
    if i > 0:
        st.stop()


def wires_main(act):
    eq_tag_list = list(get_eqip_tags())

    lc1, rc1 = st.columns(2, gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    with lc1:
        selected_left_equip = option_menu('Select the Left Side Equipment',
                                          options=eq_tag_list,
                                          icons=['-'] * len(eq_tag_list),
                                          orientation='horizontal',
                                          menu_icon='1-square')

    left_pan_tag_list = list(get_panel_tags(selected_left_equip))

    if len(left_pan_tag_list) == 0:
        left_pan_tag_list = ['No panels available']

    with lc1:
        selected_left_panel = option_menu('Select the Left Side Panel',
                                          options=left_pan_tag_list,
                                          icons=['-'] * len(left_pan_tag_list),
                                          orientation='horizontal', menu_icon='2-square')

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    with rc1:
        selected_right_equip = option_menu('Select the Right Side Equipment',
                                           options=eq_tag_list,
                                           icons=['-'] * len(eq_tag_list),
                                           orientation='horizontal',
                                           menu_icon='3-square')

    right_pan_tag_list = list(get_panel_tags(selected_right_equip))

    if len(right_pan_tag_list) == 0:
        right_pan_tag_list = ['No panels available']

    with rc1:
        selected_right_panel = option_menu('Select the Right Side Panel',
                                           options=right_pan_tag_list,
                                           icons=['-'] * len(right_pan_tag_list),
                                           orientation='horizontal', menu_icon='4-square')

    cab_df = get_filtered_cables(selected_left_equip, selected_left_panel, selected_right_equip, selected_right_panel)


    if isinstance(cab_df, pd.DataFrame) and len(cab_df) != 0:
        cab_tag_list = cab_df.cable_tag.tolist()
    else:
        cab_tag_list = ['No cables available']
        st.toast(cab_df)


    cab_tag = option_menu('Select the Cable',
                          options=cab_tag_list,
                          icons=['-'] * len(cab_tag_list),
                          orientation='horizontal', menu_icon='5-square')

    if cab_tag == 'No cables available':
        st.stop()

    st.write(":blue[Selected Cable Details]")
    st.data_editor(cab_df[cab_df.cable_tag == cab_tag], use_container_width=True)

    left_terminals = get_panel_terminals(selected_left_equip, selected_left_panel)
    right_terminals = get_panel_terminals(selected_right_equip, selected_right_panel)

    df = get_filtered_wires(cab_tag)

    if not isinstance(df, pd.DataFrame):
        st.write(f"#### :blue[No wires available for selected Cable...]")
        st.stop()

    if len(df):
        st.write(":blue[Wires Details]")
        edited_df = st.data_editor(df,
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

        if act == 'Delete':

            if st.button("Delete All Wires"):
                act_with_warning(
                    left_function=delete_wires,
                    left_args=cab_tag,
                    header_message="All wires and their connections will be deleted!",
                    warning_message="Delete?",
                    waiting_time=7, use_buttons=False
                )

        if act == 'Edit':
            c1, c2, c3, c4, c5 = st.columns(5, gap='large')
            if c2.button("Save Selected Wires Termination",
                         help="It will be faster but without complete duplicates check"):
                check_dulicated_terminals(edited_df[edited_df.edit.astype('str') == "True"])
                edit_wires(edited_df, cab_tag, all_wires=False)

            if c4.button("Save All Wires Termination", help="It will be slower but with complete duplicates check"):
                check_dulicated_terminals(edited_df)
                edit_wires(edited_df, cab_tag, all_wires=True)

    else:
        st.write(f"#### :blue[Wires of cable {cab_tag} not available ...]")
        if act == 'Create':
            if st.button('Create Wires'):
                st.write(f"Left Terminals: {left_terminals}")
                st.write(f"Right Terminals: {right_terminals}")
                if left_terminals[0] and right_terminals[0]:
                    if " : " in left_terminals[0] and " : " in right_terminals[0]:
                        create_wires(cab_tag,
                                     cab_df.loc[cab_df.cable_tag == cab_tag, 'wire'].to_numpy()[0],
                                     left_terminals[0],
                                     right_terminals[0])
                    else:
                        st.toast(f"##### :orange[Create terminals first]")
                else:
                    st.toast(f"##### :orange[Create terminals first]")
