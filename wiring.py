# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd


def close_intercon_doc():
    st.session_state.intercon['doc'] = None
    st.session_state.intercon['equip'] = None
    st.session_state.intercon['panel'] = None
    st.session_state.intercon['block'] = None
    st.session_state.intercon['terminal'] = None
    st.session_state.intercon['cable'] = None
    st.session_state.intercon['wire'] = None
    st.session_state.intercon['cab_descr'] = None


def open_inercon_doc():
    doc_sheets = list(pd.read_excel(st.session_state.intercon['doc'], sheet_name=None).keys())
    doc_sheets.sort()
    st.write(f"doc_sheets={doc_sheets}")
    design_sheets = ['equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']
    design_sheets.sort()
    st.write(f"ddesign_sheets={design_sheets}")

    st.stop()
    if doc_sheets != design_sheets:
        st.warning('Uploaded document is wrong...Upload another one')
        if st.button('Uploaded document is wrong...Upload another one'):
            close_intercon_doc()
    else:
        st.button("File uploaded successfully")
        st.stop()

    try:
        st.session_state.intercon['equip'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='equip')
        st.session_state.intercon['panel'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='panel')
        st.session_state.intercon['block'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='block')
        st.session_state.intercon['terminal'] = pd.read_excel(st.session_state.intercon['doc'],
                                                              sheet_name='terminal')
        st.session_state.intercon['cable'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='cable')
        st.session_state.intercon['wire'] = pd.read_excel(st.session_state.intercon['doc'], sheet_name='wire')
        st.session_state.intercon['cab_descr'] = pd.read_excel(st.session_state.intercon['doc'],
                                                               sheet_name='cab_descr')
    except Exception as e:
        st.warning('It seems the uploaded file is wrong...')
        st.write(e)


def create_new_doc():
    st.session_state.inter_doc = True
    st.write("Doc Created")


# def add_equip_to_doc(tag, descr):
#     st.text(descr)
#     if st.session_state.inter_doc:
#         st.write(f"Saved To Doc: {tag}:{descr}")
#         st.header(descr)
#     else:
#         st.write(":red[New Document will be created!]")
#         create_new_doc()
#         st.write(f"Saved To Doc after doc creation: {tag}:{descr}")


def create_equipment():
    with st.form('create_eq'):
        eq_tag = st.text_input('Equipment Tag')
        eq_descr = st.text_input('Equipment Descr')
        add_eq_button = st.form_submit_button("Add equipment to Document")

    # if add_eq_button:
        # add_equip_to_doc(eq_tag, eq_descr)


def create_cab_con():
    lc, rc = st.columns(2, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        left_eq = lc.selectbox("Select the Left Equipment", eq_list)
        right_eq = rc.selectbox("Select the Right Equipment", eq_list)

        panels = st.session_state.intercon['panel']
        left_pan_list = panels.loc[panels.eq_tag == left_eq, 'full_pan_tag'].tolist()
        right_pan_list = panels.loc[panels.eq_tag == right_eq, 'full_pan_tag'].tolist()

        if len(left_pan_list) and len(right_pan_list):
            left_pan = lc.selectbox("Select the Left Panel", left_pan_list)
            right_pan = rc.selectbox("Select the Right Panel", right_pan_list)

            cab_tag = lc.text_input("Cable Tag")

            cab = st.session_state.intercon['cab_descr']

            cab_purposes = cab['cab_purpose'].tolist()
            cab_types = cab['cab_type'].tolist()
            cab_sects = cab['cab_sect'].tolist()
            cab_tags = st.session_state.intercon['cable']['cab_tag'].tolist()

            cab_purpose = rc.selectbox("Select Cable Purpose", cab_purposes)
            cab_type = lc.selectbox("Select Cable Type", cab_types)
            cab_sect = rc.selectbox("Select Wire Section", cab_sects)

            if cab_tag and st.button("Create Cable Connection", use_container_width=True):
                if cab_tag in cab_tags:
                    st.button("Cable with such tag already exist...CLOSE and try again", type='primary')
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
                    }
                ])

                st.write(df2)

                df1 = st.session_state.intercon['cable'].copy(deep=True)
                st.session_state.intercon['cable'] = pd.concat([df1, df2],
                                                               ignore_index=True)
                # st.session_state.intercon['cable'].reset_index(inplace=True)

                st.button(f"New Cable {cab_tag} is Added. CLOSE")


        else:
            st.warning('Some Panels not available...')
    else:
        st.warning('Equipment not available...')
