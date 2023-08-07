# -*- coding: utf-8 -*-
import streamlit as st
from pony.orm import db_session, select
import pandas as pd

from inter_db.read_all_tabs import get_all_blocks
from models import Panel, Block, Terminal, Equip
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
                        p.panel_un,
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
                        p.panel_un,
                    )
                    for p in Panel
                    if equip_tag == p.eq_id.equipment_tag)[:]

        df = pd.DataFrame(data, columns=['id', 'equipment_tag', 'panel_tag', 'description',
                                         'edit', 'notes', 'panel_un'])
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
                    # t.terminal_un
                )
                for t in Terminal if t.block_id == block)[:]

        df = pd.DataFrame(data, columns=['id', 'block_id', 'terminal_num', 'int_circuit', 'int_link',
                                         'edit', 'notes', ])  # 'terminal_un'
        return df
    except Exception as e:
        st.toast(err_handler(e))



def create_terminals(selected_equip, selected_panel, selected_block, terminals):
    i = 0
    # try:
    with db_session:
        equip = Equip.get(equipment_tag=selected_equip)
        panel = select(p for p in Panel if p.panel_tag == selected_panel and p.eq_id == equip).first()
        block = select(b for b in Block if b.pan_id == panel and b.block_tag == selected_block).first()
        exist_terminals = select(te.terminal_num for te in Terminal if te.block_id == block)[:]

        for t in terminals:
            t = str(t)
            if t in exist_terminals :
                st.toast(f"##### :red[Terminal {t} already exists...]")
                continue

            Terminal(
                block_id=block,
                terminal_num=t,
                int_circuit="",
                int_link="",
                edit=False,
                notes='',
                # terminal_un=str(block_un) + ":" + t,
            )
            i += 1

        if '999' in exist_terminals or '999' in terminals:
            pass
        else:
            Terminal(
                block_id=block,
                terminal_num='999',
                int_circuit="SPARE",
                int_link="SPARE",
                edit=False,
                notes='',
                # terminal_un=str(block_un) + ":" + t,
            )

    st.toast(f"##### :green[{i} terminals added]")

    # except Exception as e:
    #     st.toast(err_handler(e))
    # finally:
    # get_selected_block_terminals.clear()
    # get_panel_terminals.clear()
    # st.experimental_rerun()


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
        st.experimental_rerun()


def add_block_to_db(equip_tag, panel_tag, block_tag, block_descr, block_notes):
    if all([len(panel_tag), len(block_tag)]):
        # try:
        with db_session:
            # equip = Equip.get(equipment_tag=equip_tag)
            panel = select(p for p in Panel
                           if p.eq_id.equipment_tag == equip_tag and p.panel_tag == panel_tag).first()

            added_block = Block(pan_id=panel, block_tag=block_tag, descr=block_descr, edit=False, notes=block_notes)

        st.toast(f"""#### :green[Block {block_tag} added!]""")

        # except Exception as e2:
        #     st.toast(f"""#### :red[Seems, such Terminal Block already exists!]""")
        #     st.toast(err_handler(e2))
        # finally:
        get_all_blocks.clear()
        get_selected_block.clear()
        get_blocks_list_by_eq_pan.clear()
        # st.button("OK")
        return added_block
    else:
        st.toast(f"""#### :red[Please fill all required (*) fields!]""")


@st.cache_data(show_spinner=False)
def get_block_terminals(equip_tag, panel_tag, source_block_tag):
    ...
