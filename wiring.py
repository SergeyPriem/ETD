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
    design_sheets = ['drw', 'equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']
    design_sheets.sort()

    if doc_sheets != design_sheets:
        st.button('❗ Uploaded document is wrong...Upload another one')
        close_intercon_doc()
        st.stop()
    else:
        st.button("File uploaded successfully")

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


def open_intercon_google():
    try:
        for sh_name in ['equip', 'panel', 'block', 'terminal', 'cable', 'wire', 'cab_descr']:
            st.session_state.intercon[sh_name] = pd.DataFrame(
                st.session_state.intercon['doc'].worksheet(sh_name).get_all_records())
    except Exception as e:
        st.warning('It seems the uploaded file is wrong...')
        st.write(e)

    if len(st.session_state.intercon['wire']) == 0:
        st.session_state.intercon['wire'] = pd.DataFrame(columns=['wire_to_add', 'cab_tag', 'full_block_tag_left',
                                                                  'term_num_left', 'wire_num', 'term_num_right',
                                                                  'full_block_tag_right', 'wire_uniq', 'wire_to_del'])
        st.write(st.session_state.intercon['wire'])


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


def edit_cab_con():
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

            if st.button("Create Cable Connection", use_container_width=True):

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
                        }
                    ])

                    st.write(df2)

                    df1 = st.session_state.intercon['cable'].copy(deep=True)
                    st.session_state.intercon['cable'] = pd.concat([df1, df2],
                                                                   ignore_index=True)
                    st.button(f"New Cable {cab_tag} is Added. CLOSE")
                else:
                    st.button("❗ Enter the Cable Tag")
        else:
            st.warning('Some Panels not available...')
    else:
        st.warning('Equipment not available...')


def edit_equipment():
    with st.form('create_eq'):
        lc, rc = st.columns(2, gap='medium')
        eq_tag = lc.text_input('Equipment Tag')
        eq_descr = rc.text_input('Equipment Descr')
        add_eq_button = st.form_submit_button("Add equipment to Document")

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
                        }
                    ]
                )

                st.write(df2)

                df1 = st.session_state.intercon['equip'].copy(deep=True)
                st.session_state.intercon['equip'] = pd.concat([df1, df2], ignore_index=True)
                st.button(f"New Equipment {eq_tag} is Added. CLOSE")
        else:
            st.button('❗ Some fields are empty...')


def edit_panel():
    with st.form('create_pan'):
        lc, rc = st.columns(2, gap='medium')
        eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
        eq_tag = lc.selectbox('Equipment Tag', eq_list)
        pan_tag = rc.text_input('Panel Tag')
        pan_descr = lc.text_input('Panel Description')
        rc.text('')
        rc.text('')
        add_pan_button = rc.form_submit_button("Add Panel to Document", use_container_width=True)

    if add_pan_button:
        if all([eq_tag, pan_tag, pan_descr]):
            full_pan_tags = st.session_state.intercon['panel'].loc[:, 'full_pan_tag'].tolist()

            full_pan_tag = str(eq_tag) + ":" + str(pan_tag)

            if full_pan_tag in full_pan_tags:
                st.button(f'❗ Panel with Tag {full_pan_tag} already exists...CLOSE and try again')
                st.stop()

            else:
                df2 = pd.DataFrame.from_dict(
                    [
                        {
                            'eq_tag': eq_tag,
                            'pan_tag': pan_tag,
                            'pan_descr': pan_descr,
                            'full_pan_tag': full_pan_tag,
                        }
                    ]
                )

                st.write(df2)

                df1 = st.session_state.intercon['panel'].copy(deep=True)
                st.session_state.intercon['panel'] = pd.concat([df1, df2], ignore_index=True)
                st.button(f"New Panel {full_pan_tag} is Added. CLOSE")
        else:
            st.button('❗ Some fields are empty...')


def edit_block():
    lc, rc = st.columns(2, gap='medium')
    eq_list = st.session_state.intercon['equip'].loc[:, 'eq_tag'].tolist()
    if len(eq_list):
        equip = lc.selectbox("Select the Equipment", eq_list)
        panels = st.session_state.intercon['panel']
        pan_list = panels.loc[panels.eq_tag == equip, 'full_pan_tag'].tolist()

        if len(pan_list):

            full_pan_tag = rc.selectbox("Select the Panel", pan_list)
            block_tag = lc.text_input("Terminal Block\'s Tag")
            block_descr = rc.text_input('Block Description - optional', value="-")

            rc.text('')
            rc.text('')

            if st.button("Create Terminal Block"):
                if full_pan_tag and block_tag:
                    full_block_tags = st.session_state.intercon['block'].loc[:, 'ful_block_tag'].tolist()

                    full_block_tag = str(full_pan_tag) + ":" + block_tag

                    if full_block_tag in full_block_tags:
                        st.button(f"❗ Terminal Block with Tag {full_block_tag} already exist...CLOSE and try again")
                        st.stop()

                    df2 = pd.DataFrame.from_dict([
                        {
                            'full_pan_tag': full_pan_tag,
                            'block_tag': block_tag,
                            'block_descr': block_descr,
                            'full_block_tag': full_block_tag,
                        }
                    ])

                    st.write(df2)

                    df1 = st.session_state.intercon['block'].copy(deep=True)
                    st.session_state.intercon['block'] = pd.concat([df1, df2], ignore_index=True)
                    st.button(f"New Terminal Block {full_block_tag} is Added. CLOSE")
                else:
                    st.button('❗ Some fields are empty...')
        else:
            st.warning('Panels not available...')
    else:
        st.warning('Equipment not available...')


def delete_wires(wires_to_del):
    st.session_state.intercon['wire'] = \
        st.session_state.intercon['wire'][~st.session_state.intercon['wire'].wire_uniq.isin(wires_to_del)]
    st.experimental_rerun()


def add_wires(act_cable, wires_to_add):

    wire_df = st.session_state.intercon['wire']

    df2 = pd.DataFrame()
    last_ind = 0
    last_num = wire_df.loc[wire_df.cab_tag == act_cable, 'wire_num'].max()

    st.write("last_num_before=", last_num)

    if not last_num or not isinstance(last_num, int):
        last_num = 1

    st.write("last_num_after=", last_num)

    for w in range(0, wires_to_add):
        wire_num = last_num + w
        df2.loc[last_ind + w, ["cab_tag", 'wire_num', 'wire_uniq', 'wire_to_del']] = \
            [act_cable, wire_num, str(act_cable)+":"+str(wire_num), False]

    st.session_state.intercon['wire'] = pd.concat([st.session_state.intercon['wire'], df2])
    st.session_state.intercon['wire'] = st.session_state.intercon['wire'].reset_index(drop=True)
    st.experimental_rerun()


def edit_wires():
    # st.markdown("""1 Select Cable
    # 2 Create wires by filling dataframe
    # 3 Make LEFT dataframe with selection of terminal block and necessary terminals quantity
    # 4 Mach one wire with one terminal AND PUSH CONNECT
    # 5 Make RIGHT dataframe with selection of terminal block and necessary terminals quantity
    # 6 Mach one wire with one terminal  AND PUSH CONNECT""")

    lc1, lc2, cc, rc = st.columns(4, gap='medium')
    cab_list = st.session_state.intercon['cable'].loc[:, 'cab_tag'].tolist()
    wires_qty_list = st.session_state.intercon['cab_descr'].loc[:, 'wire_quant'].tolist()
    act_cable = cc.selectbox('Select Cable for wires connection', cab_list)

    # wire_num = rc.radio('Select Wires Quantity', wires_qty_list, horizontal=True)

    if act_cable:
        st.subheader(f'Termination Table for Cable :blue[{act_cable}]')
        wire_df = st.session_state.intercon['wire']

        current_cable_wires_df = wire_df.loc[wire_df.cab_tag == act_cable]

        wires_to_del = []

        if len(current_cable_wires_df):
            upd_cable_wires_df = st.data_editor(current_cable_wires_df,
                                                column_config={
                                                    "wire_to_add": st.column_config.CheckboxColumn(
                                                        "Add Wire",
                                                        width="small"
                                                    ),
                                                    "full_block_tag_left": st.column_config.SelectboxColumn(
                                                        "Left Cable Terminal Block",
                                                        help="Available terminals at the Left Panel",
                                                        width="medium",
                                                        options=[1, 2, 3, ],
                                                    ),
                                                    "term_num_left": st.column_config.NumberColumn(
                                                        "Left Terminal Number",
                                                        help="Number of Terminal",
                                                        min_value=1,
                                                        max_value=250,
                                                        width="small",
                                                    ),
                                                    "wire_num": st.column_config.NumberColumn(
                                                        "Number of Wire",
                                                        min_value=1,
                                                        max_value=100,
                                                        width='small',
                                                    ),

                                                    "term_num_right": st.column_config.NumberColumn(
                                                        "Right Terminal Number",
                                                        help="Number of Terminal",
                                                        min_value=1,
                                                        max_value=250,
                                                        width="small",
                                                    ),

                                                    "full_block_tag_right": st.column_config.SelectboxColumn(
                                                        "Right Cable Terminal Block",
                                                        help="Available terminals at the Right Panel",
                                                        width="medium",
                                                        options=[4, 5, 6, ],
                                                    ),
                                                    "wire_to_del": st.column_config.CheckboxColumn(
                                                        "Delete Wire",
                                                        width="small"
                                                    )
                                                },
                                                hide_index=True, num_rows='dynamic', use_container_width=True)

            wires_to_del = upd_cable_wires_df.loc[upd_cable_wires_df.wire_to_del, 'wire_uniq'].tolist()
            st.write(f"wires_te_del={wires_to_del}")

        rc.text('')
        rc.text('')
        lc2.text('')
        lc2.text('')

        wires_to_add = lc1.number_input(f'Add new wires', min_value=1, max_value=37)

        if lc2.button("Add wires"):
            add_wires(act_cable, wires_to_add)

        if rc.button(f'Delete selected wires {wires_to_del}', use_container_width=True):
            delete_wires(wires_to_del)

    else:
        st.subheader(f'Select the Cable for Termination')

