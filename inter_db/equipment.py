# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select, IntegrityError
from inter_db.read_all_tabs import get_all_equip
from models import Equip
from utilities import err_handler, act_with_warning


@st.cache_data(show_spinner=False)
def get_eqip_tags():
    try:
        with db_session:
            eq_tags = select(eq.equipment_tag for eq in Equip)[:]
        return eq_tags
    except Exception as e:
        st.toast(err_handler(e))


def edit_equipment(df):
    eq_df = df[df.edit.astype('str') == "True"]
    if len(eq_df):
        try:
            with db_session:
                for ind, row in eq_df.iterrows():
                    edit_row = Equip[ind]
                    if not edit_row:
                        st.toast(f"#### :red[Fail, equipment {str(row.equipment_tag)} not found]")
                        continue

                    edit_row.set(equipment_tag=row.equipment_tag, descr=row.descr, notes=row.notes)
                    st.toast(f"#### :green[Equipment: {str(row.equipment_tag)} is updated]")
        except Exception as e:
            st.toast(f"Can't update {str(row.equipment_tag)}")
            st.toast(f"##### {err_handler(e)}")
        except IntegrityError as e2:
            st.toast(f"#### :red[Equipment {str(row.equipment_tag)} already exists...]")
            st.toast(f"##### {err_handler(e2)}")
        finally:
            get_all_equip.clear()
            get_eqip_tags.clear()
            st.button("OK")


def delete_equipment(df):
    eq_to_del = df[df.edit.astype('str') == "True"]
    if len(eq_to_del):
        with db_session:
            try:
                for ind, row in eq_to_del.iterrows():
                    del_row = Equip[ind]
                    if not del_row:
                        st.toast(f"#### :red[Fail, equipment {row.equipment_tag} not found]")
                        continue
                    del_row.delete()
                    st.toast(f"#### :green[Equipment: {row.equipment_tag} is deleted]")
            except Exception as e:
                st.toast(f"Can't delete {row.equipment_tag}")
                st.toast(f"##### {err_handler(e)}")
            finally:
                st.cache_data.clear()
                st.button("OK")


def copy_equipment(df):
    st.write("SUKA")
    eq_df = df[df.edit.astype('str') == "True"]
    st.write(eq_df)
    st.write(len(eq_df))
    if len(eq_df) == 1:
        with st.form('copy_eq'):
            lc, cc, rc, bc = st.columns([1, 1, 1.5, 0.5], gap='medium')
            eq_tag = lc.text_input('Equipment Tag *', key='copy_eq')
            eq_descr = cc.text_input('Equipment Description *', value=eq_df.descr.to_numpy()[0])
            eq_notes = rc.text_input('Notes', value=eq_df.notes.to_numpy()[0])
            bc.text('')
            bc.text('')
            copy_but = bc.form_submit_button("Copy Selected", use_container_width=True)

        if copy_but:
            st.write(eq_tag)
            if all([len(eq_tag), len(eq_descr)]):
                with db_session:
                    if eq_tag in select(eq.equipment_tag for eq in Equip)[:]:
                        st.toast(f"""#### :red[Equipment {eq_tag} already in DataBase]""")
                        return
                    # try:
                    st.write(eq_tag, eq_descr, eq_notes)
                    Equip(equipment_tag=eq_tag, descr=eq_descr, edit=False, notes=eq_notes)
                    st.toast(f"""#### :orange[Equipment {eq_tag}: {eq_descr} added!]""")

                    # except Exception as e:
                    #     st.toast(err_handler(e))
                    # finally:
                    get_all_equip.clear()
                    get_eqip_tags.clear()
                    st.button("OK")
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
                    st.toast(f"""#### :orange[Equipment {eq_tag}: {eq_descr} added!]""")

                except Exception as e:
                    st.toast(err_handler(e))
                finally:
                    get_all_equip.clear()
                    get_eqip_tags.clear()
                    st.button("OK")
        else:
            st.toast(f"""#### :red[Please fill all required (*) fields!]""")


def equipment_main(act):
    df_to_show = get_all_equip()

    if isinstance(df_to_show, pd.DataFrame):
        edited_df = st.data_editor(df_to_show)
    else:
        st.write(f"#### :blue[Equipment not available...]")
        st.stop()

    if act == 'Create':
        create_equipment()

    if act == 'Delete':
        if st.button("Delete Equipment"):
            act_with_warning(left_function=delete_equipment, left_args=edited_df,
                             header_message="All related panels, terminal blocks, terminals will be deleted!")

    if act == 'Edit':
        if st.button("Edit Selected Equipment"):
            edit_equipment(edited_df)

    if act == 'Copy':
        if st.button("Copy Selected Equipment"):
            copy_equipment(edited_df)
