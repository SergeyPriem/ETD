# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st


def add_blocks(act_pan, q_ty):

    df2 = pd.DataFrame()
    for i in range(q_ty):
        df2.loc[i,['full_pan_tag', 'block_tag', 'block_descr', 'block_to_del', 'full_block_tag', ]] \
            = [str(act_pan), "XT", "-", False, str(act_pan)+":XT"]

    st.session_state.intercon['block'] = pd.concat([st.session_state.intercon['block'], df2])


def delete_block(blocks_to_del):
    st.session_state.intercon['block'] = \
        st.session_state.intercon['block'][~st.session_state.intercon['block'].full_block_tag.isin(blocks_to_del)]
    st.experimental_rerun()


def edit_block():
    c1, c2, c3, c4, c5 = st.columns(5, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        equip = c1.selectbox("Select the Equipment", eq_list)
        panels = st.session_state.intercon['panel']
        pan_list = panels.loc[panels.eq_tag == equip, 'full_pan_tag'].tolist()

        if len(pan_list):

            full_pan_tag = c2.selectbox("Select the Panel", pan_list)

            c4.text('')
            c4.text('')
            c5.text('')
            c5.text('')

            blocks_q_ty = c3.number_input("Quantity of Blocks to Add", min_value=1, max_value=50, step=1)

            if c4.button("Add Blocks"):
                add_blocks(full_pan_tag, blocks_q_ty)

            blocks_df = st.session_state.intercon['block']

            blocks_to_edit_df = blocks_df[blocks_df.full_pan_tag == full_pan_tag]

            if len(blocks_to_edit_df):

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

                blocks_to_del = \
                    blocks_edited_df.loc[blocks_edited_df.block_to_del.astype('str') == "True", "full_block_tag"].tolist()

                blocks_to_show = \
                    blocks_edited_df.loc[blocks_edited_df.block_to_del.astype('str') == "True", "block_tag"].tolist()

                if c5.button(f'Delete selected {blocks_to_show}'):
                    delete_block(blocks_to_del)

                if st.button("SAVE TERMINAL BLOCKS"):

                    def check_blocks(df):

                        df.full_block_tag = df.full_pan_tag.astype('str')+":"+df.block_tag.astype('str')

                        # st.write(df)

                        check_list = df[df.full_block_tag.duplicated(), "full_block_tag"]
                        if len(check_list):
                            st.write(f"#### :red[Dulicated Terminal Blocks {check_list}. Please fix and save]")
                            st.button("OK", key='duplicated_blocks')
                            st.stop()

                    check_blocks(blocks_edited_df)

                    def save_blocks(df, act_panel):
                        temp_df = st.session_state.intercon['block'].copy(deep=True)
                        temp_df = temp_df[temp_df.full_pan_tag != act_panel]

                        st.session_state.intercon['block'] = pd.concat([temp_df, df])
                        st.session_state.intercon['block'].reset_index(drop=True, inplace=True)
                        st.write("#### :green[Blocks saved successfully]")
                        st.button("OK", key='blocks_saved')

                    save_blocks(blocks_edited_df, full_pan_tag)
            else:
                st.write("#### :blue[No terminal blocks in selected panel]")

        else:
            st.warning('Panels not available...')
    else:
        st.warning('Equipment not available...')
