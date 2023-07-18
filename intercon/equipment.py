# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd


def delete_equipment(equip_to_del):
    st.session_state.intercon['equip'] = \
        st.session_state.intercon['equip'][~st.session_state.intercon['equip'].eq_tag.isin(equip_to_del)]
    st.experimental_rerun()


def save_equipment(df):

    if True in df.eq_tag.duplicated():
        st.write(":[Duplicates in Equipment Tags. Please fix and save]")
        st.button("OK", key='eq_duplicates')

    st.session_state.intercon['equip'] = df
    st.session_state.intercon['equip'].reset_index(drop=True, inplace=True)


def edit_equipment():
    # with st.form('create_eq'):
    lc1, lc2, rc1, rc2 = st.columns(4, gap='medium')
    eq_tag = lc1.text_input('Equipment Tag')
    eq_descr = lc2.text_input('Equipment Descr')
    rc1.text('')
    rc1.text('')
    add_eq_button = rc1.button("Add Equipment to Document")

    equip_df = st.session_state.intercon['equip']

    if len(equip_df):
        upd_equip_df = st.data_editor(
            equip_df,
            column_config={
                'eq_tag': st.column_config.TextColumn(
                    'Equipment Tag',
                    width='medium',
                ),
                'eq_descr': st.column_config.TextColumn(
                    'Equipment Description',
                    width='large'
                ),
                'eq_to_del': st.column_config.CheckboxColumn(
                    'Delete Equipment',
                    default=False,
                    width='small'
                )
            },
            hide_index=True, num_rows='fixed', use_container_width=True
        )

        eq_to_del = upd_equip_df.loc[upd_equip_df.eq_to_del == "True", 'eq_tag'].tolist()
        #
        rc2.text('')
        rc2.text('')
        del_eq_button = rc2.button(f"Delete Equipment {eq_to_del}")
        if del_eq_button:
            delete_equipment(eq_to_del)

        if st.button("SAVE EQUIPMENT TABLE"):
            save_equipment(upd_equip_df)

    if add_eq_button:
        if eq_tag and eq_descr:
            eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()

            if eq_tag in eq_list:
                st.button(f"❗ Equipment with Tag {eq_tag} already exists...Close and try again")
                st.stop()
            else:
                df2 = pd.DataFrame.from_dict(
                    [
                        {
                            'eq_tag': eq_tag,
                            'eq_descr': eq_descr,
                            'eq_to_del': False
                        }
                    ]
                )

                st.write(df2)

                df1 = st.session_state.intercon['equip'].copy(deep=True)
                st.session_state.intercon['equip'] = pd.concat([df1, df2], ignore_index=True)
                st.button(f"New Equipment {eq_tag} is Added. CLOSE")
        else:
            st.button('❗ Some fields are empty...')
