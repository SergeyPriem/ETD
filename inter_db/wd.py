# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select
from streamlit_option_menu import option_menu

from inter_db.utils import get_eqip_tags
from models import Wire, Cable, Equip, Panel

from utilities import err_handler, tab_to_df, open_dxf_file, save_uploaded_file
import ezdxf


def get_all_terminals(equip_tag):
    # try:
    with db_session:
        equip = Equip.get(equipment_tag=equip_tag)
        panels = select(p for p in Panel if p.eq_id == equip)[:]
        cables = select(cab for cab in Cable if cab.left_pan_id in panels)[:]
        wires = select(
            (
                w.id,
                w.left_term_id.block_id.pan_id.eq_id.equipment_tag,
                w.left_term_id.block_id.pan_id.eq_id.descr,
                # w.left_term_id.block_id.pan_id.eq_id.notes,
                w.left_term_id.block_id.pan_id.panel_tag,
                w.left_term_id.block_id.pan_id.descr,
                w.left_term_id.block_id.pan_id.notes,
                w.left_term_id.block_id.block_tag,
                w.left_term_id.terminal_num,
                w.left_term_id.int_circuit,
                w.left_term_id.int_link,
                w.left_term_id.notes,
                w.cable_id.cable_tag,
                w.cable_id.purpose_id.circuit_descr,
                w.cable_id.type_id.cab_type,
                w.cable_id.wires_id.wire_num,
                w.cable_id.sect_id.section,
                w.cable_id.notes,
                w.wire_num,
                w.right_term_id.block_id.pan_id.eq_id.equipment_tag,
                w.right_term_id.block_id.pan_id.eq_id.descr,
                # w.right_term_id.block_id.pan_id.eq_id.notes,
                w.right_term_id.block_id.pan_id.panel_tag,
                w.right_term_id.block_id.pan_id.descr,
                w.right_term_id.block_id.pan_id.notes,
                w.right_term_id.block_id.block_tag,
                w.right_term_id.terminal_num,
                w.right_term_id.int_circuit,
                w.right_term_id.int_link,
                w.right_term_id.notes,
                w.notes
            )
            for w in Wire if w.cable_id in cables)[:]

        wires_df = pd.DataFrame(
            data=wires, columns=[
                'id',
                'left_equip_tag', 'left_equip_descr',  # 'left_equip_notes',
                'left_panel_tag', 'left_panel_descr', 'left_panel_notes',
                'left_block_tag', 'left_term', 'left_int_circ', 'left_jumper', 'left_term_note',
                'cable_tag', 'cable_descr', 'cable_type', 'cable_wires', 'cable_section', 'cable_notes', 'wire_num',
                'right_equip_tag', 'right_equip_descr',  # 'right_equip_notes',
                'right_panel_tag', 'right_panel_descr', 'right_panel_notes',
                'right_block_tag', 'right_term', 'right_int_circ', 'right_jumper', 'right_term_note',
                'wire_notes',
            ])
        return wires_df

    # except Exception as e:
    #     st.toast(err_handler(e))


def draw_equip_head(msp, term_df=None, right_shift=None):
    st.session_state.term_coord['x'] = 10
    st.session_state.term_coord['y'] -= 20

    ins_block = msp.add_blockref('equip_head',
                                 insert=(st.session_state.term_coord['x'], st.session_state.term_coord['y']))
    att_values = {
        'EQUIP_TAG_DESCR': str(term_df.left_equip_tag[0]) + " - " + str(term_df.left_equip_descr[0]),
        'EQUIP_NOTES': "----",
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('equip_head',
                                 insert=(
                                     st.session_state.term_coord['x'] + right_shift,
                                     st.session_state.term_coord['y']))
    att_values = {
        'EQUIP_TAG_DESCR': str(term_df.right_equip_tag[0]) + " - " + str(term_df.right_equip_descr[0]),
        'EQUIP_NOTES': "----",
    }
    ins_block.add_auto_attribs(att_values)

    st.session_state.term_coord['y'] -= 8


def draw_pan_head(pan_head_df, msp, right_shift):
    st.session_state.term_coord['x'] = 17
    st.session_state.term_coord['y'] -= 12

    ins_block = msp.add_blockref('panel_head',
                                 insert=(st.session_state.term_coord['x'], st.session_state.term_coord['y']))
    att_values = {
        'PANEL_TAG_DESCR': str(pan_head_df.left_panel_tag[0]) + " - " + str(pan_head_df.left_panel_descr[0]),
        'PANEL_NOTES': pan_head_df.left_panel_notes[0],
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('panel_head',
                                 insert=(
                                     st.session_state.term_coord['x'] +
                                     right_shift, st.session_state.term_coord['y']))
    att_values = {
        'PANEL_TAG_DESCR': str(pan_head_df.right_panel_tag[0]) + " - " + str(pan_head_df.right_panel_descr[0]),
        'PANEL_NOTES': pan_head_df.righ_panel_notes[0],
    }
    ins_block.add_auto_attribs(att_values)

    st.session_state.term_coord['y'] -= 8


def draw_block_head(msp, shift, panel_tag, block_tag):
    st.session_state.term_coord['x'] = 62
    st.session_state.term_coord['y'] -= 12

    ins_block = msp.add_blockref('block_head',
                                 insert=(st.session_state.term_coord['x'] + shift, st.session_state.term_coord['y']))
    att_values = {
        'PANEL_TAG': panel_tag,
        'BLOCK_TAG': block_tag,
    }
    ins_block.add_auto_attribs(att_values)

    # st.session_state.term_coord['y'] -= 8


def add_current_symbol(msp, shift):
    msp.add_blockref('current_symbol', insert=(st.session_state.term_coord['x'], st.session_state.term_coord['y']))
    msp.add_blockref('current_symbol',
                     insert=(st.session_state.term_coord['x'] + shift, st.session_state.term_coord['y']))


def add_int_jumper(msp, shift):
    msp.add_blockref('jumper', insert=(st.session_state.term_coord['x'] + shift, st.session_state.term_coord['y']))


def add_ext_link(msp, shift, ext_link, right_side):
    if right_side:
        ins_block = msp.add_blockref('right_external_link',
                                     insert=(st.session_state.term_coord['x'] + shift,
                                             st.session_state.term_coord['y']))
        att_values = {'RIGHT_EXT_LINK': ext_link, }
        ins_block.add_auto_attribs(att_values)
    else:
        ins_block = msp.add_blockref('left_external_link',
                                     insert=(st.session_state.term_coord['x'] + shift,
                                             st.session_state.term_coord['y']))
        att_values = {'LEFT_EXT_LINK': ext_link, }
        ins_block.add_auto_attribs(att_values)


def draw_terminal(msp=None, right_shift=None, left_note=None, left_wire_num=None, left_term=None, left_circuit=None,
                  right_note=None, right_wire_num=None, right_term=None, right_circuit=None, cab_purpose=None,
                  left_int_jumper=None, left_ext_jumper=None, right_int_jumper=None, right_ext_jumper=None):
    st.session_state.term_coord['x'] = 62

    ins_block = msp.add_blockref('block_head',
                                 insert=(st.session_state.term_coord['x'], st.session_state.term_coord['y']))
    att_values = {
        'LEFT_NOTE': left_note,
        'LEFT_WIRE_NUM': left_wire_num,
        'LEFT_TERM': left_term,
        'LEFT_CIRCUIT': left_circuit,
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('block_head',
                                 insert=(
                                     st.session_state.term_coord['x'] +
                                     right_shift - 20, st.session_state.term_coord['y']))
    att_values = {
        'RIGHT_NOTE': right_note,
        'RIGHT_WIRE_NUM': right_wire_num,
        'RIGHT_TERM': right_term,
        'RIGHT_CIRCUIT': right_circuit,
    }

    ins_block.add_auto_attribs(att_values)

    if cab_purpose == "AC - current":
        add_current_symbol(msp, right_shift - 20)

    if left_int_jumper:
        add_int_jumper(msp, 0)

    if left_ext_jumper:
        add_ext_link(msp, 0, ext_link="", right_side=False)

    if right_int_jumper:
        add_int_jumper(msp, right_shift - 20)

    if right_ext_jumper:
        add_ext_link(msp, right_shift - 20, ext_link="", right_side=True)

    st.session_state.term_coord['y'] -= 5


def generate_wd():
    eq_tag_list = list(get_eqip_tags())

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    else:
        if len(eq_tag_list) > 1:
            eq_tag_list.append("ALL")

    c1, c2 = st.columns([3, 1], gap='medium')

    with c1:
        selected_equip = option_menu('Select the Equipment',
                                     options=eq_tag_list,
                                     icons=['-'] * len(eq_tag_list),
                                     orientation='horizontal',
                                     menu_icon='1-square')
    dxf_template = c2.file_uploader("TEMPLATE loader", type='dxf')

    term_df = get_all_terminals(selected_equip)

    if isinstance(term_df, pd.DataFrame) and len(term_df):
        st.data_editor(term_df, use_container_width=True, hide_index=True)
    else:
        st.write("##### :blue[No links found...]")

    right_equip_list = list(term_df.right_equip_tag.unique())

    panels_list = list(term_df.left_panel_tag.unique())
    st.write(panels_list)

    template_path = f'temp_dxf/{save_uploaded_file(dxf_template)}'
    doc = open_dxf_file(template_path)
    msp = doc.modelspace()

    if 'term_coord' not in st.session_state:
        st.session_state.term_coord = {
            'l_x': 0,
            'l_y': 0,
            'r_x': 220,
            'r_y': 0,
        }

    right_shift = 220

    draw_equip_head(msp, term_df, right_shift)

    for r_eqip in right_equip_list:

        for p in panels_list:

            panel_df = term_df[term_df.left_pan_tag == p]
            draw_pan_head(panel_df, msp, right_shift)

            cable_tag_list = panel_df.cable_tag.to_list()

            for cable_tag in cable_tag_list:

                cable_df = panel_df[panel_df.cable_tag == cable_tag]

                left_blocks = list(cable_df.left_block_tag.unique())
                right_blocks = list(cable_df.right_block_tag.unique())

                for left_block in left_blocks:

                    left_block_df = cable_df[cable_df.left_block_tag == left_block]

                    draw_block_head(b)

                    left_terminals = list(left_block_df.left_term.unique())

                    for lt in left_terminals:
                        draw_terminal(lt)

                for right_block in right_blocks:

                    right_block_df = cable_df[cable_df.right_block_tag == right_block]

                    draw_block_head(b)

                    right_terminals = list(right_block_df.left_term.unique())

                    for rt in right_terminals:
                        draw_terminal(rt)

                draw_cable(cable_tag)



