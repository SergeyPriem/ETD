# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st


def add_blocks(act_pan, q_ty):

    df2 = pd.DataFrame()
    for i in range(q_ty):
        df2.loc[i, [
            'full_pan_tag', 'block_tag', 'block_decr', 'full_block_tag', 'block_to_del'
        ]
        ] = [act_pan, "XT", "-", None, False]

    st.session_state.intercon['block'] = pd.concat([st.session_state.intercon['block'], df2])



def edit_block():
    c1, c2, c3, c4 = st.columns(4, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        equip = c1.selectbox("Select the Equipment", eq_list)
        panels = st.session_state.intercon['panel']
        pan_list = panels.loc[panels.eq_tag == equip, 'full_pan_tag'].tolist()

        if len(pan_list):

            full_pan_tag = c2.selectbox("Select the Panel", pan_list)
            block_tag = c3.text_input("Terminal Block\'s Tag")
            block_descr = c4.text_input('Block Description - optional', value="-")

            lc, cc, rc = st.columns(3, gap='medium')
            cc.text('')
            cc.text('')
            rc.text('')
            rc.text('')

            blocks_q_ty = lc.number_input("Quantity of Blocks to Add", min_value=1, max_value=50, step=1)
            if cc.button("Add Blocks"):
                add_blocks(full_pan_tag, blocks_q_ty)

            rc.button('Delete selected')

            blocks_df = st.session_state.intercon['block']

            blocks_to_edit_df = blocks_df[blocks_df.full_pan_tag == full_pan_tag]

            blocks_edited_df = st.data_editor(
                blocks_to_edit_df,
                column_config = {
                    "full_pan_tag": st.column_config.TextColumn(
                        "Full Panel Tag",
                        width="small"
                    ),

                    "block_tag": st.column_config.TextColumn(
                        "Block Tag",
                        width="small"
                    ),
                    "block_descr": st.column_config.TextColumn(
                        "Block Description",
                        width="medium"
                    ),
                    "block_to_del": st.column_config.CheckboxColumn(
                        "Delete Block",
                        width="small",
                        default=False
                    ),
                    "full_block_tag": st.column_config.TextColumn(
                        "Full Block Tag",
                        width="small"
                    ),
                }, hide_index=True, use_container_width=True, num_rows='fixed'
            )

            # if st.button("Create Terminal Block"):
            #     if full_pan_tag and block_tag:
            #         full_block_tags = st.session_state.intercon['block'].loc[:, 'ful_block_tag'].tolist()
            #
            #         full_block_tag = str(full_pan_tag) + ":" + block_tag
            #
            #         if full_block_tag in full_block_tags:
            #             st.button(f"❗ Terminal Block with Tag {full_block_tag} already exist...CLOSE and try again")
            #             st.stop()
            #
            #         df2 = pd.DataFrame.from_dict([
            #             {
            #                 'full_pan_tag': full_pan_tag,
            #                 'block_tag': block_tag,
            #                 'block_descr': block_descr,
            #                 'full_block_tag': full_block_tag,
            #             }
            #         ])
            #
            #         st.write(df2)
            #
            #         df1 = st.session_state.intercon['block'].copy(deep=True)
            #         st.session_state.intercon['block'] = pd.concat([df1, df2], ignore_index=True)
            #         st.button(f"New Terminal Block {full_block_tag} is Added. CLOSE")
            #     else:
            #         st.button('❗ Some fields are empty...')
        else:
            st.warning('Panels not available...')
    else:
        st.warning('Equipment not available...')
