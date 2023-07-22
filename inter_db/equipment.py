# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from pony.orm import db_session, select
from models import Equip
from utilities import err_handler


def delete_equipment(df):
    tag_list = df.loc[df.to_del.astype('str') == "True", 'equipment_tag'].tolist()
    if tag_list:
        with db_session:
            try:
                for tag in tag_list:
                    del_row = Equip.get(equipment_tag=tag)
                    if not del_row:
                        st.toast(f"#### :red[Fail, equipment {tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Equipment: {tag} is deleted]")
            except Exception as e:
                st.toast(f"Can't delete {tag}")
                st.toast(f"##### {err_handler(e)}")
            finally:
                if st.button("OK", key='eq_deleted'):
                    st.session_state.inter_stat['equipment'] += 1
                    st.toast("RERUN")
                    st.experimental_rerun()




def create_equipment():
    with st.form('add_eq'):
        lc, cc, rc, bc = st.columns(4, gap='medium')
        eq_tag = lc.text_input('Equipment Tag')
        eq_descr = cc.text_input('Equipment Description')
        eq_notes = rc.text_input('Notes')
        bc.text('')
        bc.text('')
        eq_but = bc.form_submit_button("Add")

    if all([eq_but, len(eq_tag), len(eq_descr)]):
        with db_session:
            if eq_tag in select(eq.equipment_tag for eq in Equip)[:]:
                st.toast(f"""#### :red[Equipment {eq_tag} already in DataBase]""")
                return
            try:
                Equip(
                    equipment_tag=eq_tag,
                    descr=eq_descr,
                    to_del=False,
                    notes=eq_notes
                )
                st.toast(f"""#### :orange[Equipment {eq_tag}: {eq_descr} added!]""")
                st.session_state.inter_stat['equipment'] +=1
                if st.button("OK", key='eq_added'):
                    st.experimental_rerun()

            except Exception as e:
                st.toast(err_handler(e))

# def delete_equipment(equip_to_del):
#     st.session_state.intercon['equip'] = \
#         st.session_state.intercon['equip'][~st.session_state.intercon['equip'].eq_tag.isin(equip_to_del)]
#     st.experimental_rerun()


def save_equipment(df):

    df_check = df.loc[df.eq_tag.duplicated(), 'eq_tag']
    if len(df_check):
        st.write(f"#### :red[Duplicates in Equipment Tags {df_check.tolist()}. Please fix and save]")
        st.button("OK", key='eq_duplicates')
        st.stop()

    st.session_state.intercon['equip'] = df
    st.session_state.intercon['equip'].reset_index(drop=True, inplace=True)
    st.write("#### :green[Equipment saved successfully]")
    st.button("OK", key='eq_saved')


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
                    disabled=True,
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

        eq_to_del = upd_equip_df.loc[upd_equip_df.eq_to_del.astype('str') == "True", 'eq_tag'].tolist()
        #
        rc2.text('')
        rc2.text('')
        del_eq_button = rc2.button(f"Delete Equipment {eq_to_del}")
        if del_eq_button:
            delete_equipment(eq_to_del)

        if st.button("SAVE EQUIPMENT TABLE"):
            save_equipment(upd_equip_df)

    else:
        st.warning("Equipment not available...")

    if add_eq_button:
        if eq_tag and eq_descr:
            eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()

            if eq_tag in eq_list:
                st.write(f"#### :red[❗ Equipment with Tag {eq_tag} already exists...Close and try again]")
                st.button("OK", key="equip_duplicates")
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


                df1 = st.session_state.intercon['equip'].copy(deep=True)
                st.session_state.intercon['equip'] = pd.concat([df1, df2], ignore_index=True)
                st.experimental_rerun()
        else:
            st.button('❗ Some fields are empty...')
