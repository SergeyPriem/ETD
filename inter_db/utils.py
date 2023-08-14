﻿# -*- coding: utf-8 -*-
import streamlit as st
from pony.orm import db_session, select
import pandas as pd

from inter_db.read_all_tabs import get_all_blocks
from models import Panel, Block, Terminal, Equip, Cable, Cab_purpose, Cab_types, Cab_wires, Cab_sect, Wire
from utilities import err_handler


@st.cache_data(show_spinner=False)
def get_eqip_tags():
    try:
        with db_session:
            eq_tags = select(eq.equipment_tag for eq in Equip)[:]
        return eq_tags
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_panel_terminals(equip_tag, panel_tag):
    try:
        with db_session:
            panel = select(p for p in Panel if p.panel_tag == panel_tag and p.eq_id.equipment_tag == equip_tag).first()
            blocks = select(b for b in Block if b.pan_id == panel)[:]

            # data = select(str(t.block_id.block_tag) + " : " + str(t.terminal_num)
            #               for t in Terminal if t.block_id in blocks)[:]
            data = select(str(t.block_id.block_tag) + " : " + str(t.terminal_num)
                          for t in Terminal if t.block_id in blocks)[:]
        return data
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_panels_by_equip_panel_tag(equip_tag, pan_tag):
    try:
        with db_session:
            if pan_tag != 'ALL':
                data = select(
                    (
                        p.id,
                        p.eq_id.equipment_tag,
                        p.panel_tag,
                        p.descr,
                        p.edit,
                        p.notes,
                    )
                    for p in Panel
                    if equip_tag == p.eq_id.equipment_tag and pan_tag == p.panel_tag)[:]
            else:
                data = select(
                    (
                        p.id,
                        p.eq_id.equipment_tag,
                        p.panel_tag,
                        p.descr,
                        p.edit,
                        p.notes,
                    )
                    for p in Panel
                    if equip_tag == p.eq_id.equipment_tag)[:]

        df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description',
                                         'edit', 'notes', ])
        return df
    except Exception as e:
        return err_handler(e)


@st.cache_data(show_spinner=False)
def get_filtered_panels(equip):
    try:
        with db_session:
            equip_id = Equip.get(equipment_tag=equip)
            data = select(
                (p.id,
                 p.eq_id.equipment_tag,
                 p.panel_tag,
                 p.descr,
                 p.edit,
                 p.notes,
                 p.panel_un,
                 )
                for p in Panel
                if p.eq_id == equip_id
            )[:]
        df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description',
                                         'edit', 'notes', 'panel_un'])
        return df
    except Exception as e:
        return err_handler(e)


@st.cache_data(show_spinner=False)
def get_panel_tags(eq_tag):
    try:
        with db_session:
            eq_tags = select(p.panel_tag for p in Panel if p.eq_id.equipment_tag == eq_tag)[:]
        return eq_tags
    except Exception as e:
        return [err_handler(e)]


@st.cache_data(show_spinner=False)
def get_blocks_list_by_eq_pan(selected_equip, selected_panel):
    try:
        with db_session:
            data = select(b.block_tag
                          for b in Block
                          for p in b.pan_id
                          if selected_panel == b.pan_id.panel_tag and
                          selected_equip == p.eq_id.equipment_tag)[:]

            return data
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_selected_block(selected_equip, selected_panel, selected_block):
    try:
        with db_session:
            if selected_block != 'ALL':
                data = select(
                    (
                        b.id,
                        b.pan_id.panel_un,
                        b.block_tag,
                        b.descr,
                        b.edit,
                        b.notes,
                    )
                    for b in Block
                    for p in b.pan_id
                    if selected_panel == b.pan_id.panel_tag and
                    selected_equip == p.eq_id.equipment_tag and
                    selected_block == b.block_tag
                )[:]
            else:
                data = select(
                    (
                        b.id,
                        b.pan_id.panel_un,
                        b.block_tag,
                        b.descr,
                        b.edit,
                        b.notes,
                    )
                    for b in Block
                    for p in b.pan_id
                    if selected_panel == b.pan_id.panel_tag and
                    selected_equip == p.eq_id.equipment_tag
                )[:]

        df = pd.DataFrame(data, columns=['id', 'panel_tag', 'block_tag', 'description',
                                         'edit', 'notes'])
        return df
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_selected_block_terminals(selected_equip, selected_panel, selected_block):
    try:
        with db_session:
            equip = Equip.get(equipment_tag=selected_equip)
            panel = select(p for p in Panel if p.panel_tag == selected_panel and p.eq_id == equip).first()
            block = select(b for b in Block if b.pan_id == panel and b.block_tag == selected_block).first()
            data = select(
                (
                    t.id,
                    t.block_id.block_tag,
                    t.terminal_num,
                    t.int_circuit,
                    t.int_link,
                    t.edit,
                    t.notes,
                )
                for t in Terminal if t.block_id == block)[:]

        df = pd.DataFrame(data,
                          columns=['id', 'block_id', 'terminal_num', 'int_circuit', 'int_link', 'edit', 'notes', ])

        return df
    except Exception as e:
        st.toast(err_handler(e))


def create_terminals(selected_equip, selected_panel, selected_block, terminals):
    i = 0
    try:
        with db_session:
            equip = Equip.get(equipment_tag=selected_equip)
            panel = select(p for p in Panel if p.panel_tag == selected_panel and p.eq_id == equip).first()
            block = select(b for b in Block if b.pan_id == panel and b.block_tag == selected_block).first()
            exist_terminals = select(te.terminal_num for te in Terminal if te.block_id == block)[:]

            for t in terminals:
                t = str(t)
                if t in exist_terminals:
                    st.toast(f"##### :red[Terminal {t} already exists...]")
                    continue

                Terminal(
                    block_id=block,
                    terminal_num=t,
                    int_circuit="",
                    int_link="",
                    edit=False,
                    notes='',
                )
                i += 1

            if 'isolated' in exist_terminals or 'isolated' in terminals:
                pass
            else:
                Terminal(
                    block_id=block,
                    terminal_num='isolated',
                    int_circuit="SPARE",
                    int_link="SPARE",
                    edit=False,
                    notes='',
                )

        st.toast(f"##### :green[{i} terminals added]")

    except Exception as e:
        st.toast(err_handler(e))
    finally:
        get_selected_block_terminals.clear()
        get_panel_terminals.clear()
        st.experimental_rerun()


def create_terminals_with_internals(selected_equip, selected_panel, selected_block, terminals):
    i = 0
    try:
        with db_session:
            equip = Equip.get(equipment_tag=selected_equip)
            panel = select(p for p in Panel if p.panel_tag == selected_panel and p.eq_id == equip).first()
            block = select(b for b in Block if b.pan_id == panel and b.block_tag == selected_block).first()
            exist_terminals = select(te for te in Terminal if te.block_id == block)[:]

            for t in terminals:
                if t in exist_terminals or t.terminal_num == "isolated":
                    st.toast(f"##### :red[Terminal {t.terminal_num} already exists...]")
                    continue

                Terminal(
                    block_id=block,
                    terminal_num=t.terminal_num,
                    int_circuit=t.int_circuit,
                    int_link=t.int_link,
                    edit=False,
                    notes=t.notes,
                )
                i += 1
            st.toast(f"##### :green[{i} terminals added]")

            Terminal(
                block_id=block,
                terminal_num='isolated',
                int_circuit='SPARE',
                int_link='SPARE',
                edit=False,
            )
    except Exception as e:
        st.toast(err_handler(e))


def create_block(equip_tag, panel_tag):
    with st.form('add_block'):
        c1, c2, c3, c4, c5, c6 = st.columns([0.5, 0.5, 1, 1, 1.5, 0.5], gap='medium')
        c1.text_input('Equipment Tag *', value=equip_tag, disabled=True)
        c2.text_input('Panel Tag *', value=panel_tag, disabled=True)
        block_tag = c3.text_input('Block Tag *')
        block_descr = c4.text_input('Block Description')
        block_notes = c5.text_input('Notes')
        c6.text('')
        c6.text('')
        block_but = c6.form_submit_button("Add", use_container_width=True)

    if block_but:
        add_block_to_db(equip_tag, panel_tag, block_tag, block_descr, block_notes)
        st.button("OK")


def add_block_to_db(equip_tag, panel_tag, block_tag, block_descr, block_notes):
    if all([len(panel_tag), len(block_tag)]):
        try:
            with db_session:
                # equip = Equip.get(equipment_tag=equip_tag)
                panel = select(p for p in Panel
                               if p.eq_id.equipment_tag == equip_tag and p.panel_tag == panel_tag).first()

                added_block = Block(pan_id=panel, block_tag=block_tag, descr=block_descr, edit=False, notes=block_notes)

            st.toast(f"""#### :green[Block {block_tag} added!]""")

        except Exception as e2:
            st.toast(f"""#### :red[Seems, such Terminal Block already exists!]""")
            st.toast(err_handler(e2))
        finally:
            get_all_blocks.clear()
            get_selected_block.clear()
            get_blocks_list_by_eq_pan.clear()
            # st.button("OK")
        return added_block
    else:
        st.toast(f"""#### :red[Please fill all required (*) fields!]""")


@st.cache_data(show_spinner=False)
def get_terminals_by_block_id(block_id):
    ...


def good_index(ind_ex, row_w):
    if isinstance(row_w.id, int):
        st.write("row.id")
        return row_w.id
    if isinstance(row_w[0], int):
        st.write("row[0]")
        return row_w[0]
    if isinstance(ind_ex, int):
        st.write('index')
        return ind_ex
    st.write('False')
    return False


@st.cache_data(show_spinner=False)
def get_cab_panels(cab_tag):
    try:
        with db_session:
            cab_tags = select((c.left_pan_id.panel_un, c.right_pan_id.panel_un)
                              for c in Cable if c.cable_tag == cab_tag).first()
        return cab_tags
    except Exception as e:
        st.toast(err_handler(e))


@st.cache_data(show_spinner=False)
def get_cab_tags():
    try:
        with db_session:
            cab_tags = select(c.cable_tag for c in Cable)[:]
        return list(cab_tags)
    except Exception as e:
        return err_handler(e)


@st.cache_data(show_spinner=False)
def get_filtered_cables(left_eq, left_pan, right_eq, right_pan):
    try:
        with db_session:
            left_pan = select(p for p in Panel if p.panel_tag == left_pan and p.eq_id.equipment_tag == left_eq).first()

            right_pan = select(
                p for p in Panel if p.panel_tag == right_pan and p.eq_id.equipment_tag == right_eq).first()

            if left_pan and right_pan:
                data = select(
                    (c.id, c.cable_tag, c.purpose_id.circuit_descr, c.type_id.cab_type, c.wires_id.wire_num,
                     c.sect_id.section, c.left_pan_id.panel_tag, c.right_pan_id.panel_tag, c.edit, c.notes,)
                    for c in Cable
                    if (c.left_pan_id == left_pan) and (c.right_pan_id == right_pan))[:]

                df = pd.DataFrame(data, columns=['id', 'cable_tag', 'purpose', 'type', 'wire', 'section',
                                                 'left_pan_tag', 'right_pan_tag', 'edit', 'notes', ])
                return df
    except Exception as e:
        # st.toast(err_handler(e))
        st.toast(e)
        return err_handler(e)

@st.cache_data(show_spinner=False)
def get_all_blocks_for_preview():
    try:
        with db_session:
            data = select(
                (b.id,
                 b.pan_id.eq_id.equipment_tag,
                 b.pan_id.panel_tag,
                 b.block_tag,
                 b.descr,
                 b.notes,)

                for b in Block)[:]

            df = pd.DataFrame(data, columns=['ID', 'Equipment', 'Panel', 'Terminal Block', 'Description', 'Notes', ])
            return df
    except Exception as e:
        # st.toast(err_handler(e))
        return err_handler(e)


@st.cache_data(show_spinner=False)
def get_all_cables():
    try:
        with db_session:
            data = select(
                (c.id,
                 c.left_pan_id.eq_id.equipment_tag,
                 c.left_pan_id.panel_tag,
                 c.cable_tag,
                 c.purpose_id.circuit_descr,
                 c.type_id.cab_type,
                 c.wires_id.wire_num,
                 c.sect_id.section,
                 c.right_pan_id.eq_id.equipment_tag,
                 c.right_pan_id.panel_tag,
                 c.notes,)

                for c in Cable)[:]

            df = pd.DataFrame(data, columns=['ID', 'Left Equipment', 'Left Panel',
                                             'Cable Tag', 'Purpose', 'Type', 'Wires', 'Section',
                                             'Right Equipment', 'Right Panel', 'Notes', ])
            return df
    except Exception as e:
        # st.toast(err_handler(e))
        return err_handler(e)


@st.cache_data(show_spinner=False, ttl=600)
def get_cab_params():
    try:
        with db_session:
            purposes = select(cp.circuit_descr for cp in Cab_purpose)[:]
            types = select(ct.cab_type for ct in Cab_types)[:]
            wire_num = select(w.wire_num for w in Cab_wires)[:]
            wire_sect = select(s.section for s in Cab_sect)[:]
        return purposes, types, wire_num, wire_sect
    except Exception as e:
        return err_handler(e)


def get_block_terminals(bl):
    with db_session:
        terms = select(t.terminal_num for t in Terminal if t.block_id == bl and t.terminal_num != "isolated")[:]
    return terms

@st.cache_data(show_spinner=False)
def get_cable_wires(cable_tag):
    try:
        with db_session:
            cable = Cable.get(cable_tag=cable_tag)

            wires = select(
                (
                    w.id,
                    w.cable_id.cable_tag,
                    w.wire_num,
                    w.edit,
                    w.notes,
                )
                for w in Wire if w.cable_id == cable)[:]

        df = pd.DataFrame(data=wires, columns=['id', 'cable_tag', 'wire_num', 'edit', 'notes'])
        return df
    except Exception as e:
        return err_handler(e)
