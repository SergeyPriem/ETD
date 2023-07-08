# -*- coding: utf-8 -*-
import streamlit as st


def create_new_doc():
    st.session_state.inter_doc = True
    st.write("Doc Created")


def add_equip_to_doc(tag, descr):
    if st.session_state.inter_doc:
        st.write(f"Saved To Doc: {tag}:{descr}")
    else:
        st.write(":red[New Document will be created!]")
        create_new_doc()


def create_equipment():
    with st.form('create_eq'):
        eq_tag = st.text_input('Equipment Tag')
        eq_descr = st.text_input('Equipment Descr')
        add_eq_button = st.form_submit_button("Add equipment to Document")

        if add_eq_button:
            add_equip_to_doc(eq_tag, eq_descr)
