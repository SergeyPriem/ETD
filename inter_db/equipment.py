# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select, IntegrityError
from streamlit_option_menu import option_menu

from inter_db.read_all_tabs import get_equip_by_tag
from models import Equip
from utilities import err_handler
from inter_db.utils import get_eqip_tags


def edit_equipment(df):
    eq_df = df[df.edit.astype('str') == "True"]
    try:
        with db_session:
            if len(eq_df):
                for ind, row in eq_df.iterrows():
                    edit_row = Equip[row.id]
                    edit_row.set(equipment_tag=row.equipment_tag, descr=row.descr, notes=row.notes)
                    st.toast(f"#### :green[Equipment: {str(row.equipment_tag)} is updated]")
    except Exception as e:
        st.toast(f"Can't update {str(row.equipment_tag)} with id {ind}")
        st.toast(f"##### {err_handler(e)}")
    except IntegrityError as e2:
        st.toast(f"#### :red[Equipment {str(row.equipment_tag)}  with id {ind} already exists...]")
        st.toast(f"##### {err_handler(e2)}")
    finally:
        st.cache_data.clear()
        st.button('OK')


def delete_equipment(df):
    eq_to_del = df[df.edit.astype('str') == "True"]

    if len(eq_to_del):
        try:
            with db_session:
                for ind, row in eq_to_del.iterrows():

                    if row.id == 0:
                        st.warning("ID can't be 0")
                        continue

                    Equip[row.id].delete()
                    st.toast(f"#### :green[Equipment: {row.equipment_tag}  with id {ind} is deleted]")

        except Exception as e:
            st.toast(f"Can't delete {row.equipment_tag} with id {ind}")
            st.toast(f"##### {err_handler(e)}")

        finally:
            st.cache_data.clear()
            st.button('OK')


def copy_equipment(df):
    eq_df = df[df.edit.astype('str') == "True"]
    if len(eq_df) == 1:
        with st.form('copy_eq'):
            lc, cc, rc, bc = st.columns([1, 1, 1.5, 0.5], gap='medium')
            eq_tag = lc.text_input('Equipment Tag *', key='copy_eq', value=eq_df.equipment_tag.to_numpy()[0][:-1])
            eq_descr = cc.text_input('Equipment Description *', value=eq_df.descr.to_numpy()[0])
            eq_notes = rc.text_input('Notes', value=eq_df.notes.to_numpy()[0])
            bc.text('')
            bc.text('')
            copy_but = bc.form_submit_button("Copy Selected", use_container_width=True)

        if copy_but:
            if all([len(eq_tag), len(eq_descr)]):
                with db_session:
                    if eq_tag in select(eq.equipment_tag for eq in Equip)[:]:
                        st.toast(f"""#### :red[Equipment {eq_tag} already in DataBase]""")
                        return
                    try:
                        st.write(eq_tag, eq_descr, eq_notes)
                        Equip(equipment_tag=eq_tag, descr=eq_descr, edit=False, notes=eq_notes)
                        st.toast(f"""#### :green[Equipment {eq_tag}: {eq_descr} added!]""")

                    except Exception as e:
                        st.toast(err_handler(e))
                    finally:
                        st.cache_data.clear()
                        st.button('OK')
            else:
                st.toast(f"""#### :red[Please fill all required (*) fields!]""")
    else:
        st.toast("##### :orange[Select only one Equipment]")


def create_equipment():
    with st.form('add_eq'):
        lc, cc, rc, bc = st.columns([1, 1, 1.5, 0.5], gap='medium')
        eq_tag = lc.text_input('Equipment Tag *')
        eq_descr = cc.text_input('Equipment Description *')
        eq_notes = rc.text_input('Notes')
        bc.text('')
        bc.text('')
        eq_but = bc.form_submit_button("Add", use_container_width=True)

    if eq_but:
        if all([len(eq_tag), len(eq_descr)]):
            with db_session:
                if eq_tag in select(eq.equipment_tag for eq in Equip)[:]:
                    st.toast(f"""#### :red[Equipment {eq_tag} already in DataBase]""")
                    return
                try:
                    Equip(equipment_tag=eq_tag, descr=eq_descr, edit=False, notes=eq_notes)
                    st.toast(f"""#### :green[Equipment {eq_tag}: {eq_descr} added!]""")

                except Exception as e:
                    st.toast(err_handler(e))
                finally:
                    get_equip_by_tag.clear()
                    get_eqip_tags.clear()
                    st.button("OK")
        else:
            st.toast(f"""#### :red[Please fill all required (*) fields!]""")


def equipment_main(act):
    eq_tag_list = list(get_eqip_tags())

    if len(eq_tag_list) == 0:
        eq_tag_list = ['No equipment available']
    else:
        if len(eq_tag_list) > 1:
            eq_tag_list.append("ALL")

    selected_equip = option_menu('Select the Equipment',
                                 options=eq_tag_list,
                                 icons=['-'] * len(eq_tag_list),
                                 orientation='horizontal',
                                 menu_icon='1-square')

    df_to_show = get_equip_by_tag(selected_equip)



    if not isinstance(df_to_show, pd.DataFrame) or len(df_to_show) == 0:
        st.write(f"#### :blue[Equipment not available...]")
        st.stop()

    edited_df = st.data_editor(df_to_show, use_container_width=True, hide_index=True)

    if act == 'Create':
        create_equipment()

    if act == 'Delete':
        st.subheader(f":warning: :red[All nested panels, terminal blocks, terminals will be deleted!]")
        if st.button("Delete Selected"):
            # act_with_warning(left_function=delete_equipment, left_args=edited_df,
            #                  header_message="All related panels, terminal blocks, terminals will be deleted!",
            #                  warning_message="Are you sure?")
            delete_equipment(edited_df)

    if act == 'Edit':
        if st.button("Save edited Equipment"):
            edit_equipment(edited_df)

    if act == 'Copy':
        copy_equipment(edited_df)
