# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

def check_panels(df):

    df.full_pan_tag = df.eq_tag.astype('str')  + ":" +df.pan_tag.astype('str')
    check_list = df.loc[df.full_pan_tag.duplicated(), 'full_pan_tag'].tolist()

    if len(check_list):
        st.write(f"#### :red[Duplicated Panel Tags {check_list}. Please fix and save]")
        st.button('OK', key='duplicated_panels')
        st.stop()



def delete_panels(pan_to_del):
    st.session_state.intercon['panel'] = \
        st.session_state.intercon['panel'][~st.session_state.intercon['panel'].full_pan_tag.isin(pan_to_del)]
    st.experimental_rerun()


def save_panels(upd_panels_df, act_equip):
    temp_df = st.session_state.intercon['panel'].copy(deep=True)
    temp_df = temp_df[temp_df.eq_tag != act_equip]

    st.session_state.intercon['panel'] = pd.concat([temp_df, upd_panels_df])
    st.session_state.intercon['panel'].reset_index(drop=True, inplace=True)


def add_panels(act_equip, q_ty):

    df2 = pd.DataFrame()

    for w in range(0, q_ty):
        df2.loc[w, ["eq_tag", 'pan_to_del']] = [act_equip, False]

    st.session_state.intercon['panel'] = pd.concat([st.session_state.intercon['panel'], df2])
    st.session_state.intercon['panel'] = st.session_state.intercon['panel'].reset_index(drop=True)
    st.experimental_rerun()


def edit_panel():
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()

    if len(eq_list):
        lc1, lc2, rc1, rc2 = st.columns([2, 1, 1, 2], gap='medium')
        eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
        eq_tag = lc1.selectbox('Equipment Tag', eq_list)
        # pan_tag = lc2.text_input('Panel Tag')
        # pan_descr = lc3.text_input('Panel Description')
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
                pan_to_show = upd_pan_df.loc[upd_pan_df.pan_to_del.astype('str') == 'True', "full_pan_tag"].tolist()
                del_pan_button = rc2.button(f"Delete selected Panels {pan_to_show}", use_container_width=True)

                if del_pan_button:
                    delete_panels(pan_to_del)
            else:
                st.write(":blue[No panels for this equipment]")

            if st.button('SAVE PANELS'):
                check_panels(upd_pan_df)
                save_panels(upd_pan_df, eq_tag)

    else:
        st.write("Equipment not available...")
