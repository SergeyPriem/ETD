# -*- coding: utf-8 -*-

import streamlit as st


def transmittal_close(trans_col):
    trans_col.header('Close Transmittal')
    with trans_col.form('confirm_trans'):
        out_num = st.text_input('Number of reply Transmittal')
        out_date = st.date_input('Date of reply Transmittal')

        conf_but = st.form_submit_button('Close')

        if conf_but:
            st.info(f"{out_num} by {out_date}")
