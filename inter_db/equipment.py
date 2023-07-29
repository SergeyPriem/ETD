# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
from pony.orm import db_session, select, IntegrityError
from streamlit_option_menu import option_menu

from inter_db.read_all_tabs import get_all_equip
from models import Equip
from utilities import err_handler


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
                    edit_row = Equip[row.id]
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
    st.write(df)


    eq_to_del = df[df.edit.astype('str') == "True"]
    if len(eq_to_del):
        with db_session:
            try:
                for ind, row in eq_to_del.iterrows():
                    del_row = Equip[row.id]
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


def equipment_main(act=None, prev_dict=None, prev_sel=None):



    if act == 'Create':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show)
        else:
            st.write(f"#### :blue[Equipment not available...]")
        create_equipment()

    if act == 'View':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            st.data_editor(df_to_show)
        else:
            st.write(f"#### :blue[Equipment not available...]")

    if act == 'Delete':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show)
            c1, c2, c3 = st.columns(3, gap='medium')
            c1.write("#### :red[Warning! If you delete the Equipment - all related, panels, blocks, terminals will be deleted!!!]")
            c3.write("#### :red[Warning! If you delete the Equipment - all related, panels, blocks, terminals will be deleted!!!]")
            c2.text('')

            if c2.button("Delete Equipment"):
                st.session_state.confirmation = True

            c1, c2, c3 = st.columns([5, 2, 5])
            with c2:
                if st.session_state.confirmation:

                    yes_no = option_menu('Are you sure?', options=['Yes - Delete', 'No - Return'],
                                         menu_icon="exclamation-triangle", icons=['-', '-'], default_index=1)



                    if yes_no == 'Yes - Delete':

                        st.write(edited_df)
                        # delete_equipment(edited_df)
                    st.session_state.confirmation = False
        else:
            st.write(f"#### :blue[Equipment not available...]")

    if act == 'Edit':
        df_to_show = prev_dict[prev_sel]()
        if isinstance(df_to_show, pd.DataFrame):
            edited_df = st.data_editor(df_to_show)
            if st.button("Edit Selected Equipment"):
                edit_equipment(edited_df)
        else:
            st.write(f"#### :blue[Equipment not available...]")
