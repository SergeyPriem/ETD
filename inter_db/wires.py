# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.cables import get_filtered_cables
from inter_db.equipment import get_eqip_tags
from inter_db.panels import get_panel_tags
from inter_db.terminals import get_panel_terminals
from models import Wire, Cable, Block, Terminal
from utilities import err_handler, act_with_warning


@st.cache_data(show_spinner=False)
def get_filtered_wires(cab_tag):
    try:
        with db_session:
            # cab = Cable.get(cable_tag=cab_tag)
            data = select((
                              w.id,
                              w.cable_id.cable_tag,
                              w.wire_num,
                              w.left_term_id,
                              w.right_term_id,
                              w.edit,
                              w.notes,
                          ) for w in Wire if w.cable_id.cable_tag == cab_tag)[:]

        df = pd.DataFrame(data, columns=['id', 'cable_tag', 'wire_num', 'left_term_id', 'right_term_id',
                                         'edit', 'notes', ])
        return df
    except Exception as e:
        return err_handler(e)


def edit_wires(edited_df, cab_tag):
    df = edited_df[edited_df.edit.astype('str') == "True"]
    i = 0
    try:
        with db_session:
            for ind, row in df.iterrows():
                wire = Wire[ind]
                left_panel = Cable.get(cable_tag=cab_tag).left_pan_id
                right_panel = Cable.get(cable_tag=cab_tag).right_pan_id

                left_ful_term = row.left_term_id.split(" : ")
                right_ful_term = row.right_term_id.split(" : ")

                if len(left_ful_term) == 2 and len(right_ful_term) == 2:

                    left_block_tag = left_ful_term[0]
                    right_block_tag = right_ful_term[0]

                    left_term_num = left_ful_term[1]
                    right_term_num = right_ful_term[1]

                    left_block = select(b for b in Block
                                        if b.block_tag == left_block_tag and b.pan_id == left_panel).first()
                    right_block = select(b for b in Block
                                        if b.block_tag == right_block_tag and b.pan_id == right_panel).first()

                    left_term = select(t for t in Terminal
                                       if t.block_id == left_block and t.terminal_num == left_term_num)
                    right_term = select(t for t in Terminal
                                       if t.block_id == right_block and t.terminal_num == right_term_num)
                    wire.set(
                        left_term_id=left_term,
                        right_term_id=right_term,
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


def create_wires(cab_tag, wires_num):
    try:
        with db_session:
            cable = Cable.get(cable_tag=cab_tag)
            for w in range(1, wires_num + 1):
                Wire(
                    cable_id=cable,
                    wire_num=w
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


def wires_main(act):

    eq_tag_list = list(get_eqip_tags())

    lc1, rc1 = st.columns(2, gap='medium')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with lc1:
        # selected_left_equip = st.radio('Select the Left Side Equipment',
        #                                   options=eq_tag_list,
        #                                   horizontal=True)

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
        # selected_left_panel = st.radio('Select the Left Side Panel',
        #                                   options=left_pan_tag_list,
        #                                   horizontal=True)
        selected_left_panel = option_menu('Select the Left Side Panel',
                                          options=left_pan_tag_list,
                                          icons=['-'] * len(left_pan_tag_list),
                                          orientation='horizontal', menu_icon='2-square')

    if len(eq_tag_list) == 0:
        eq_tag_list = 'No equipment available'
    with rc1:
        # selected_right_equip = st.radio('Select the Right Side Equipment',
        #                                    options=eq_tag_list,
        #                                    horizontal=True)
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
        # selected_right_panel = st.radio('Select the Right Side Panel',
        #                                    options=right_pan_tag_list,
        #                                    horizontal=True)
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

    # cab_tag = st.radio('Select the Cable',
    #                       options=cab_tag_list,
    #                       horizontal=True)
    cab_tag = option_menu('Select the Cable',
                          options=cab_tag_list,
                          icons=['-'] * len(cab_tag_list),
                          orientation='horizontal', menu_icon='5-square')

    if cab_tag == 'No cables available':
        st.write(f"#### :blue[Select Cable Tag to proceed ore create new one]")
        st.stop()

    st.write(":blue[Selected Cable Details]")
    st.data_editor(cab_df[cab_df.cable_tag == cab_tag], use_container_width=True)

    df = get_filtered_wires(cab_tag)

    if not isinstance(df, pd.DataFrame):
        st.write(f"#### :blue[No wires available for selected Cable...]")
        st.stop()

    if len(df):

        if act == "Edit":
            left_terminals = get_panel_terminals(selected_left_equip, selected_left_panel)
            right_terminals = get_panel_terminals(selected_right_equip, selected_right_panel)
        else:
            left_terminals = []
            right_terminals = []

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
            if st.button("Edit Selected Wires"):
                edit_wires(edited_df, cab_tag)

    else:
        st.write(f"#### :blue[Wires of cable {cab_tag} not available ...]")
        if act == 'Create':
            if st.button('Create Wires'):
                create_wires(cab_tag, cab_df.loc[cab_df.cable_tag == cab_tag, 'wire'].to_numpy()[0])


