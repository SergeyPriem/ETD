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
                w.right_term_id.block_id.pan_id.eq_id.notes,
                w.right_term_id.block_id.pan_id.panel_tag,
                w.right_term_id.block_id.pan_id.descr,
                # w.right_term_id.block_id.pan_id.notes,
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
                'left_equip_tag', 'left_equip_descr', #'left_equip_notes',
                'left_panel_tag', 'left_panel_descr', 'left_panel_notes',
                'left_block_tag', 'left_term', 'left_int_circ', 'left_jumper', 'left_term_note',
                'cable_tag', 'cable_descr', 'cable_type', 'cable_wires', 'cable_section', 'cable_notes', 'wire_num',
                'right_equip_tag', 'right_equip_descr', #'right_equip_notes',
                'right_panel_tag', 'right_panel_descr', 'right_panel_notes',
                'right_block_tag', 'right_term', 'right_int_circ', 'right_jumper', 'right_term_note',
                'wire_notes',
            ])
        return wires_df

    # except Exception as e:
    #     st.toast(err_handler(e))


def draw_pan_connection(panel, dxf_template):
    ...

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

    st.stop()
    panels_list = list(term_df.left_panel_tag.unique())
    st.write(panels_list)

    template_path = f'temp_dxf/{save_uploaded_file(dxf_template)}'
    doc = open_dxf_file(template_path)
    msp = doc.modelspace()

    if 'term_coord' not in st.session_state:
        st.session_state.term_coord = {
            'x': 10,
            'y': 10,
        }

    ins_block = msp.add_blockref('equip_head',
                                 insert=(st.session_state.term_coord['x'], st.session_state.term_coord['x'])
                                 )
    att_values = {
        'EQUIP_TAG_DESCR': str(term_df.left_equip_tag[0]) + " - " + str(term_df.left_equip_descr[0]),
        'EQUIP_NOTES': v.cab_tag,
    }

    ins_block.add_auto_attribs(att_values)

    for p in panels_list:
        draw_pan_connection(p, msp)