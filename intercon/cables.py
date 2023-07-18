# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st


def delete_cable(cab_to_del_list):
    st.session_state.intercon['cable'] = \
        st.session_state.intercon['cable'][~st.session_state.intercon['cable'].cab_tag.isin(cab_to_del_list)]
    st.experimental_rerun()


def edit_cab_con():
    lc1, lc2, rc1, rc2 = st.columns(4, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        left_eq = lc1.selectbox("Select the Left Equipment", eq_list)
        right_eq = rc1.selectbox("Select the Right Equipment", eq_list)

        panels = st.session_state.intercon['panel']
        left_pan_list = panels.loc[panels.eq_tag == left_eq, 'full_pan_tag'].tolist()
        right_pan_list = panels.loc[panels.eq_tag == right_eq, 'full_pan_tag'].tolist()

        if len(left_pan_list) and len(right_pan_list):
            left_pan = lc2.selectbox("Select the Left Panel", left_pan_list)
            right_pan = rc2.selectbox("Select the Right Panel", right_pan_list)

            cab_tag = lc1.text_input("Cable Tag")

            cab = st.session_state.intercon['cab_descr']

            cab_purposes = cab['cab_purpose'].tolist()
            cab_types = cab['cab_type'].tolist()
            cab_sects = cab['cab_sect'].tolist()
            cab_wire_qtys = cab['wire_quant'].tolist()
            cab_tags = st.session_state.intercon['cable']['cab_tag'].tolist()

            cab_purpose = lc2.selectbox("Select Cable Purpose", cab_purposes)
            cab_type = rc1.selectbox("Select Cable Type", cab_types)
            cab_sect = rc2.selectbox("Select Wire Section", cab_sects)

            lc, rc = st.columns(2, gap='medium')

            if lc.button("Create Cable Connection", use_container_width=True):

                if cab_tag:
                    if cab_tag in cab_tags:
                        st.button(f"❗ Cable with Tag {cab_tag} already exist...CLOSE and try again")
                        st.stop()

                    df2 = pd.DataFrame.from_dict([
                        {
                            'full_pan_tag_left': left_pan,
                            'full_pan_tag_right': right_pan,
                            'cab_tag': cab_tag,
                            'cab_purpose': cab_purpose,
                            'cab_type': cab_type,
                            'cab_sect': cab_sect,
                            'wire_quant': 0,
                            'cab_to_del': False
                        }
                    ])

                    df1 = st.session_state.intercon['cable'].copy(deep=True)
                    st.session_state.intercon['cable'] = pd.concat([df1, df2],
                                                                   ignore_index=True)
                    st.experimental_rerun()
                else:
                    st.button("❗ Enter the Cable Tag")

            cab_df = st.session_state.intercon['cable']
            cab_to_edit_df = cab_df[(cab_df.full_pan_tag_left == left_pan) & (cab_df.full_pan_tag_right == right_pan)]

            if len(cab_to_edit_df):
                edited_cab_df = st.data_editor(
                    cab_to_edit_df,
                    column_config={
                        "full_pan_tag_left": st.column_config.TextColumn(
                            "Left Panel Tag",
                            width="small",
                            disabled=True
                        ),
                        "cab_tag": st.column_config.TextColumn(
                            "Cable Tag",
                            width="medium",
                        ),
                        "full_pan_tag_right": st.column_config.TextColumn(
                            "Right Panel Tag",
                            width="small",
                            disabled=True
                        ),
                        "cab_purpose": st.column_config.SelectboxColumn(
                            "Cable Purpose",
                            options=cab_purposes,
                            width='small',
                        ),
                        "cab_type": st.column_config.SelectboxColumn(
                            "Cable Type",
                            options=cab_types,
                            width='small',
                        ),
                        "cab_sect": st.column_config.SelectboxColumn(
                            "Wire Section",
                            options=cab_sects,
                            width='small',
                        ),
                        "wire_quant": st.column_config.SelectboxColumn(
                            "Wires Quantity",
                            options=cab_wire_qtys,
                            width='small',
                        ),
                        "cab_to_del": st.column_config.CheckboxColumn(
                            "Cable to delete",
                            default=False
                        )
                    },
                    use_container_width=True, hide_index=True
                )

                cab_to_del_list = edited_cab_df.loc[edited_cab_df.cab_to_del.astype('str') == "True", "cab_tag"].tolist()

                if rc.button(f'Delete selected {cab_to_del_list}', use_container_width=True):

                    delete_cable(cab_to_del_list)
            else:
                st.write("#### :blue[No cables between selected panels]")
        else:
            st.warning('Some Panels not available...')
    else:
        st.warning('Equipment not available...')
