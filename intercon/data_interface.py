# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd


def close_intercon_doc():
    st.session_state.intercon['doc'] = None
    st.session_state.intercon['equip'] = None
    st.session_state.intercon['panel'] = None
    st.session_state.intercon['block'] = None
    st.session_state.intercon['terminal'] = None
    st.session_state.intercon['cable'] = None
    st.session_state.intercon['wire'] = None
    st.session_state.intercon['cab_descr'] = None
    st.write("#### Wires Doc Closed")


def open_inercon_doc():
    doc_sheets = list(pd.read_excel(st.session_state.intercon['doc'], sheet_name=None).keys())
    doc_sheets.sort()
    design_sheets = ['drw', 'equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']
    design_sheets.sort()

    if doc_sheets != design_sheets:
        st.button('❗ Uploaded document is wrong...Upload another one')
        close_intercon_doc()
        st.stop()
    else:
        st.button("File uploaded successfully")

    try:
        st.session_state.intercon['equip'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='equip')
        st.session_state.intercon['panel'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='panel')
        st.session_state.intercon['block'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='block')
        st.session_state.intercon['terminal'] = pd.read_excel(st.session_state.intercon['doc'],
                                                              sheet_name='terminal')
        st.session_state.intercon['cable'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='cable')
        st.session_state.intercon['wire'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='wire')
        st.session_state.intercon['cab_descr'] = pd.read_excel(st.session_state.intercon['doc'],
                                                               sheet_name='cab_descr')
    except Exception as e:
        st.warning('It seems the uploaded file is wrong...')
        st.write(e)


def open_intercon_google():
    try:
        for sh_name in ['equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']:
            st.session_state.intercon[sh_name] = pd.DataFrame(
                st.session_state.intercon['doc'].worksheet(sh_name).get_all_records())
    except Exception as e:
        st.warning('It seems the uploaded file is wrong...')
        st.write(e)

    if len(st.session_state.intercon['wire']) == 0:
        st.session_state.intercon['wire'] = pd.DataFrame(columns=['cab_tag', 'full_block_tag_left',
                                                                  'term_num_left', 'wire_num', 'term_num_right',
                                                                  'full_block_tag_right', 'wire_to_del',
                                                                  'full_term_tag_left', 'wire_uniq',
                                                                  'full_term_tag_right'])
    if len(st.session_state.intercon['equip']) == 0:
        st.session_state.intercon['equip'] = pd.DataFrame(columns=['eq_tag', 'eq_descr', 'eq_to_del'])

    if len(st.session_state.intercon['panel']) == 0:
        st.session_state.intercon['panel'] = pd.DataFrame(columns=['eq_tag', 'pan_tag',
                                                                   'pan_descr', 'full_pan_tag', 'pan_to_del'])

    if len(st.session_state.intercon['block']) == 0:
        st.session_state.intercon['block'] = pd.DataFrame(columns=['full_pan_tag', 'block_tag',
                                                                   'block_descr', 'full_block_tag', 'block_to_del'])




