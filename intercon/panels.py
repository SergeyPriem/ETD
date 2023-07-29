# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select

from models import Equip, Panel




def edit_panel():
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()

    if len(eq_list):
        lc1, lc2, rc1, rc2 = st.columns([2, 1, 1, 2], gap='medium')
        eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
        eq_tag = lc1.selectbox('Equipment Tag', eq_list)
        pan_to_add = lc2.number_input('Quantity of Panels to add', step=1, min_value=1, max_value=50)

        rc1.text('')
        rc1.text('')
        add_pan_button = rc1.button("Add Panel to Document", use_container_width=True)

        if eq_tag:
            if add_pan_button:
                add_panels(eq_tag, pan_to_add)

            pan_df = st.session_state.intercon['panel']
            pan_filtered_df = pan_df[pan_df.eq_tag == eq_tag]

            if len(pan_filtered_df):

                upd_pan_df = st.data_editor(
                    pan_filtered_df,
                    column_config={
                        "eq_tag": st.column_config.TextColumn(
                            "Equipment Tag",
                            disabled=True,
                            width='small',
                        ),
                        "pan_tag": st.column_config.TextColumn(
                            "Panel Tag",
                            width='small',
                        ),
                        "pan_descr": st.column_config.TextColumn(
                            "Panel Description",
                            width="medium",
                        ),
                        "full_pan_tag": st.column_config.TextColumn(
                            "Full Panel Tag",
                            width='small',
                            disabled=True,
                        ),
                        "pan_to_del": st.column_config.CheckboxColumn(
                            "Panel to delete",
                            width="small",
                            default=False,
                        ),
                    },
                    hide_index=True, num_rows='fixed', use_container_width=True)

                rc2.text('')
                rc2.text('')

                # st.write(upd_pan_df.pan_to_del)

                pan_to_del = upd_pan_df.loc[upd_pan_df.pan_to_del.astype('str') == 'True', "full_pan_tag"].tolist()
                pan_to_show = upd_pan_df.loc[upd_pan_df.pan_to_del.astype('str') == 'True', "pan_tag"].tolist()
                del_pan_button = rc2.button(f"Delete selected Panels {pan_to_show}", use_container_width=True)

                if del_pan_button:
                    delete_panels(pan_to_del)

                if st.button('SAVE PANELS'):
                    check_panels(upd_pan_df)
                    save_panels(upd_pan_df, eq_tag)

            else:
                st.write("#### :blue[No panels for this equipment]")
    else:
        st.warning("Equipment not available...")
