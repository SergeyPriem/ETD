# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st


def edit_block():
    lc, rc = st.columns(2, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        equip = lc.selectbox("Select the Equipment", eq_list)
        panels = st.session_state.intercon['panel']
        pan_list = panels.loc[panels.eq_tag == equip, 'full_pan_tag'].tolist()

        if len(pan_list):

            full_pan_tag = rc.selectbox("Select the Panel", pan_list)
            block_tag = lc.text_input("Terminal Block\'s Tag")
            block_descr = rc.text_input('Block Description - optional', value="-")

            rc.text('')
            rc.text('')

            if st.button("Create Terminal Block"):
                if full_pan_tag and block_tag:
                    full_block_tags = st.session_state.intercon['block'].loc[:, 'ful_block_tag'].tolist()

                    full_block_tag = str(full_pan_tag) + ":" + block_tag

                    if full_block_tag in full_block_tags:
                        st.button(f"❗ Terminal Block with Tag {full_block_tag} already exist...CLOSE and try again")
                        st.stop()

                    df2 = pd.DataFrame.from_dict([
                        {
                            'full_pan_tag': full_pan_tag,
                            'block_tag': block_tag,
                            'block_descr': block_descr,
                            'full_block_tag': full_block_tag,
                        }
                    ])

                    st.write(df2)

                    df1 = st.session_state.intercon['block'].copy(deep=True)
                    st.session_state.intercon['block'] = pd.concat([df1, df2], ignore_index=True)
                    st.button(f"New Terminal Block {full_block_tag} is Added. CLOSE")
                else:
                    st.button('❗ Some fields are empty...')
        else:
            st.warning('Panels not available...')
    else:
        st.warning('Equipment not available...')
