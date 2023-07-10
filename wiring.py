# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd


def open_inercon_doc():
    st.session_state.intercon['equip'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='equip')
    st.session_state.intercon['panel'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='panel')
    st.session_state.intercon['block'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='block')
    st.session_state.intercon['terminal'] = pd.read_excel(st.session_state.intercon['doc'],
                                                          sheet_name='terminal')
    st.session_state.intercon['cable'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='cable')
    st.session_state.intercon['wire'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='wire')
    st.session_state.intercon['cab_types'] = pd.read_excel(st.session_state.intercon['doc'],
                                                           sheet_name='cab_types')


def create_new_doc():
    st.session_state.inter_doc = True
    st.write("Doc Created")


def add_equip_to_doc(tag, descr):
    st.text(descr)
    if st.session_state.inter_doc:
        st.write(f"Saved To Doc: {tag}:{descr}")
        st.header(descr)
    else:
        st.write(":red[New Document will be created!]")
        create_new_doc()
        st.write(f"Saved To Doc after doc creation: {tag}:{descr}")


def create_equipment():
    with st.form('create_eq'):
        eq_tag = st.text_input('Equipment Tag')
        eq_descr = st.text_input('Equipment Descr')
        add_eq_button = st.form_submit_button("Add equipment to Document")

    if add_eq_button:
        add_equip_to_doc(eq_tag, eq_descr)


def create_cab_con(pan_list):
    lc, rc = st.columns(2, gap='medium')
    left_eq = lc.selectbox("Select the Left Equipment", pan_list)
    right_eq = rc.selectbox("Select the Right Equipment", pan_list)

    left_pan = lc.selectbox("Select the Left Panel", pan_list)
    right_pan = rc.selectbox("Select the Right Panel", pan_list)

    cab_tag = st.text_input("Cable Tag")

    rc.text('')
    if rc.button("Create Cable Connection", use_container_width=True):

        st.session_state.inter_doc['cable'] = \
            st.session_state.inter_doc['cable'].append(
                {
                    'full_pan_tag_left': left_pan,
                    'full_pan_tag_right': right_pan,
                    'cab_tag': cab_tag,
                    'cab_type': cab_type,
                    'cab_constr': cab_constr,
                    'cab_sect': cab_sect
                }, ignore_index=True)
