# -*- coding: utf-8 -*-

import streamlit as st

def transmittal_close(trans_col):
    trans_col.header('Close Transmittal')
    with trans_col.form('confirm_trans'):
        out_num = trans_col.text_input('Number of outgoing')
        out_date = trans_col.date_input('Number of outgoing')

        conf_but = trans_col.form_submit_button('Close')

        if conf_but:
            st.info(f"{out_num} by {out_date}")



