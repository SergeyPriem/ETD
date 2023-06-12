# -*- coding: utf-8 -*-
import datetime

import streamlit as st
import numpy as np
import pandas as pd
import sys, re
from ezdxf.enums import TextEntityAlignment
import ezdxf
from ezdxf import zoom
from ezdxf.math import Vec2

from utilities import open_dxf_file


def kill_comma(value):
    value = float(str(value).replace(',', '.'))
    return value


def find_duplicates(df: pd.DataFrame, column_name: str) -> None:
    duplic_df = df.loc[df.duplicated(subset=['cableTag'], keep='first')]
    if duplic_df.shape[0]:
        st.write(f':red[!!! Duplicated Tag Numbers Found. Please check Cable List]')
        duplic_df.drop_duplicates(subset=['cableTag'], inplace=True)
        for elem in duplic_df[column_name]:
            st.write(f":red[!!! Dulicated: {elem}]")


def get_layout_length(sect_df, sect_final_df):
    for tag in sect_final_df.cab_tag:
        sect_final_df.loc[sect_final_df.cab_tag == tag, 'layout_len'] = kill_comma(
            sect_df.loc[sect_df.cab_tag == tag, 'layout_len'].head(1).values[0])
    return sect_final_df


def get_cab_data(cablist_df, section_sect_df):
    for tag in section_sect_df.cab_tag:
        try:
            section_sect_df.loc[section_sect_df.cab_tag == tag, 'cab_list_len'] = kill_comma(
                cablist_df.loc[cablist_df.cableTag == tag, 'length'].head(1).values[0])
            section_sect_df.loc[section_sect_df.cab_tag == tag, 'cab_diam'] = kill_comma(
                cablist_df.loc[cablist_df.cableTag == tag, 'diam'].head(1).values[0])
            section_sect_df.loc[section_sect_df.cab_tag == tag, 'cab_type'] = str(
                cablist_df.loc[cablist_df.cableTag == tag, 'compos'].head(1).values[0]) + "-" \
                                                                              + str(
                cablist_df.loc[cablist_df.cableTag == tag, 'wires'].head(1).values[0]) + 'x' \
                                                                              + str(
                cablist_df.loc[cablist_df.cableTag == tag, 'section'].head(1).values[0])
            section_sect_df.loc[section_sect_df.cab_tag == tag, 'cab_bus'] = str(
                cablist_df.loc[cablist_df.cableTag == tag, 'bus'].head(1).values[0])
        except:
            st.write()
            st.write(f":red[Trouble with tag: {tag}]")
            st.write()

            # section_sect_df
    return section_sect_df


def arrange_section(sect_df, section_tag):
    control_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "C")]
    control_df = control_df.sort_values(by='layout_len', ascending=False)

    lv_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "L")]
    lv_df = lv_df.sort_values(by='layout_len', ascending=False)

    mv_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "M")]
    mv_df = mv_df.sort_values(by='layout_len', ascending=False)

    cur_sect_df = pd.concat([control_df, lv_df, mv_df], ignore_index=True)

    return cur_sect_df


def to_dxf(df_int, dxf_path, msp, vertical_trays_gap, chan_height, lv_horis_gap, mv_horis_gap):
    p_y = 0
    shift = 0
    p_x_tr = st.session_state.p_x + 160
    p_y_tr = 0  # 10

    p_x_cab = st.session_state.p_x + 160
    p_y_cab = 0  # 40

    print_scale = 10
    vertical_trays_gap /= print_scale

    sect_tag_block = msp.add_blockref('sect_num', insert=(st.session_state.p_x + 65, 20))

    try:
        att_values = {
            'SECT_TAG': df_int.sect[0]
        }
    except:
        st.write(f"Problem with 'df.sect[0]'")
        return

    sect_tag_block.add_auto_attribs(att_values)

    msp.add_blockref('tab_header', insert=(st.session_state.p_x, p_y))

    level_quantity = df_int.chan_level.max()

    chan_width = df_int.chan_size[0] / print_scale
    tray_width = int(df_int.chan_size[0])
    chan_height /= print_scale

    msp.add_text(
        df_int.sect[0], height=4, dxfattribs={"style": "ГОСТ"}
    ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 21), align=TextEntityAlignment.CENTER)

    for support in range(1, level_quantity + 1):

        points = [(p_x_tr - 5, p_y_tr), (p_x_tr + chan_width + 5, p_y_tr),
                  (p_x_tr + chan_width + 5, p_y_tr - 5), (p_x_tr - 5, p_y_tr - 5),
                  (p_x_tr - 5, p_y_tr)]  # полка

        msp.add_lwpolyline(points)

        points = [(p_x_tr, p_y_tr + chan_height, 0.3, 0.3),
                  (p_x_tr, p_y_tr, 0.3, 0.3),
                  (p_x_tr + chan_width, p_y_tr, 0.35, 0.35),
                  (p_x_tr + chan_width, p_y_tr + chan_height, 0.5, 0.3)]  # лоток

        msp.add_lwpolyline(points)

        tray_type = str(df_int.loc[df_int.chan_level == support, 'cab_purpose'].head(1).values[0])

        if tray_type == 'C' or tray_type == 'С':
            tray_type = 'Contr.'
        else:
            tray_type += 'V'

        msp.add_text('Tray ' + str(support) + ' - ' + str(tray_type), height=3, dxfattribs={"style": "ГОСТ"}
                     ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 12), align=TextEntityAlignment.CENTER)

        msp.add_text('T' + str(tray_width) + "x100", height=3, dxfattribs={"style": "ГОСТ"}
                     ).set_placement((p_x_tr + chan_width / 2, p_y_tr - 4), align=TextEntityAlignment.CENTER)

        p_y_tr -= vertical_trays_gap

    msp.add_text("Vertical step", height=3, dxfattribs={"style": "ГОСТ"}
                 ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 6), align=TextEntityAlignment.CENTER)

    msp.add_text("of trays: " + str(int(vertical_trays_gap) * 10) + " mm", height=3, dxfattribs={"style": "ГОСТ"}
                 ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 2), align=TextEntityAlignment.CENTER)

    level_prev = 1

    for k, v in df_int.iterrows():

        if level_prev < v.chan_level:
            shift = 0
            level_prev += 1

        p_x_cab = st.session_state.p_x + 160
        ins_block = msp.add_blockref('tab_row', insert=(st.session_state.p_x, p_y))
        att_values = {
            'LEVEL_TAG': v.chan_level,
            'CABLE_TAG': v.cab_tag,
            'DIAM_TAG': v.cab_diam,
            'TYPE_TAG': v.cab_type,
            'LEN_TAG': str(v.layout_len) + " | " + str(v.cab_list_len)
        }

        ins_block.add_auto_attribs(att_values)
        p_y -= 6

        cab_radius = v.cab_diam / 2 / print_scale
        cab_diam = v.cab_diam / print_scale

        if v.cab_purpose == 'M' or v.cab_purpose == 'М':
            center_point = ((p_x_cab + cab_radius + shift + 2),
                            (p_y_cab - (vertical_trays_gap * (v.chan_level - 1)) + cab_radius + 0.2))
            msp.add_circle(center_point, cab_radius)
            shift += (1 + mv_horis_gap / 100) * cab_diam

        if v.cab_purpose == 'L':
            center_point = ((p_x_cab + cab_radius + shift + 2),
                            (p_y_cab - (vertical_trays_gap * (v.chan_level - 1)) + cab_radius + 0.2))
            msp.add_circle(center_point, cab_radius)
            shift += (1 + lv_horis_gap / 100) * cab_diam

        if level_prev < v.chan_level:
            shift = 0
            level_prev += 1


def change_cyrillic(text):
    letter_dict = {
        # RUS: ENG
        'А': 'A',
        'В': 'B',
        'С': 'C',
        'Е': 'E',
        'Н': 'H',
        'І': 'I',
        'К': 'K',
        'М': 'M',
        'О': 'O',
        'Р': 'P',
        'Т': 'T',
        'Х': 'X'
    }
    if text == '???' or text == '-':
        st.write(f"!!! Empty field, find the '???' in the row and adjust")
        return '???'

    if bool(re.search('[а-яА-Я]', text)):
        for letter in letter_dict.keys():
            if letter in text:
                st.write(f":yellow[Cyrillic Symbol: '{letter}' in the Tag: '{text}']")
                text = text.replace(letter, letter_dict[letter])
    return text


def get_cable_df(cl_path):
    try:
        xl = pd.ExcelFile(cl_path)
    except FileNotFoundError as e:
        print(e, '\n')
        sys.exit(0)

    sheet_name_list = xl.sheet_names

    if len(sheet_name_list) == 1:
        sheet_name = sheet_name_list[0]
    else:
        for index, sheet_name in enumerate(sheet_name_list):
            print(f"{index + 1}: {sheet_name}")

        sheet_number = int(input(f'File has multiple sheets Enter the required sheet number: '))
        try:
            sheet_name = sheet_name_list[sheet_number - 1]
        except:
            print('Sheet with this number not available. Try again')
            return
        return xl.parse(sheet_name)


def get_tags_from_cablist(cablist_df, from_unit, to_unit, all_chb):  # script 2

    col_names = list(cablist_df.columns)

    if "cableTag" not in col_names:
        st.warning('Seems you loaded wrong Table for Cable List...')
        st.write(col_names)


    find_duplicates(cablist_df, 'cableTag')
    cablist_df.drop_duplicates(subset=['cableTag'], inplace=True)
    cablist_df.bus.replace(np.nan, '???', inplace=True)
    cablist_df.bus.replace('-', '???', inplace=True)

    try:
        cablist_df.cableTag = cablist_df.cableTag.apply(change_cyrillic)
        cablist_df.bus = cablist_df.bus.apply(change_cyrillic)
        cablist_df.cableTag.replace(r'\s+', '', regex=True, inplace=True)
        cablist_df.cableTag.replace(r'--', '-', regex=True, inplace=True)

        # find_duplicates(cablist_df, 'cableTag')
        st.write(":blue[-- Begin of Selected List --]")

        if all_chb:
            for tag in cablist_df.cableTag:
                st.write(f":green[{tag}]")
        else:

            filtered_df = cablist_df.copy()

            if len(from_unit):
                filtered_df = cablist_df.loc[cablist_df.fromUnit.str.contains(from_unit, na=False)]

            if len(to_unit):
                filtered_df = filtered_df.loc[filtered_df.toUnit.str.contains(to_unit, na=False)]

            for tag in filtered_df.cableTag:
                st.write(f":green[{tag}]")

        st.write(":blue[-- End of Selected List --]")
    except:
        st.write(':red[!!! Data from selected sheet are not valid. Try again]')


#############################

def make_vec2(cell):
    # print([Vec2(i) for i in cell])
    return [Vec2(i) for i in cell]


def print_duplicates(cables_df, col_name):
    dup_cab_df = cables_df.loc[cables_df.duplicated(subset=[col_name], keep='first')]
    if len(dup_cab_df) > 0:
        st.write(f":red[Duplicated '{col_name}': \n{dup_cab_df[col_name]}]")
    else:
        st.write(f":green[Check for '{col_name}' duplicates - PASSED!]")


def get_data_from_cab_list(cables_df, cablist_df):
    cablist_reduced_df = cablist_df[['cableTag', 'length', 'wires', 'section', 'compos', 'diam', 'bus']]
    cables_df = pd.merge(cables_df, cablist_reduced_df, how='left', left_on='cab_tag', right_on='cableTag')
    return cables_df


# layout_path = "/content/Drawing41.dxf"  # @param {type:"string"}

def get_sect_from_layout(cablist_df, layout_path):  ### 3

    doc = open_dxf_file(layout_path)
    msp = doc.modelspace()

    p_lines = msp.query('*[layer=="power_layout"]')

    if len(p_lines) == 0:
        st.write(f":red[It seems there are no CableWays and Sections at the 'power_layout']")
        st.stop()

    layout_sect_df = pd.DataFrame({'sect': pd.Series(dtype='str'),
                                   'cab_tag': pd.Series(dtype='str'),
                                   'cab_diam': pd.Series(dtype='object'),
                                   'cab_type': pd.Series(dtype='str'),
                                   'cab_list_len': pd.Series(dtype='object'),
                                   'layout_len': pd.Series(dtype='object'),
                                   'chan_level': pd.Series(dtype='object'),
                                   'chan_type': pd.Series(dtype='str'),
                                   'chan_size': pd.Series(dtype='object'),
                                   'cab_purpose': pd.Series(dtype='str'),
                                   'cab_bus': pd.Series(dtype='str'),
                                   'sect_vertices': pd.Series(dtype='object'),
                                   })

    ways_df = pd.DataFrame({'cab_tag': pd.Series(dtype='str'),
                            'layout_len': pd.Series(dtype='object'),
                            'way_vertices': pd.Series(dtype='object'),
                            })

    for s in p_lines:
        if s.has_xdata("section"):
            xd_section = s.get_xdata("section")
            # print('sect=', xd_section)
            # print('sect_vertices=',tuple(s.vertices()))
            row_num = len(layout_sect_df)
            curr_sect = xd_section[0][1].split(": ")[1]
            layout_sect_df.at[row_num, 'sect'] = curr_sect
            channel = xd_section[1][1].split(": ")[1]
            chan_type = str(channel[:1])

            if chan_type not in 'TP':
                print(f":red[!!! Wrong channel type '{chan_type}' in Section {curr_sect}. Should be Txxx or Pxxx]")
                sys.exit()

            chan_size = int((channel[1:]))

            if chan_size < 20:
                st.write(":[!!! Wrong channel size '{chan_size}' in Section {curr_sect}. Should be at least 20]")
                st.stop()

            layout_sect_df.at[row_num, 'chan_type'] = chan_type
            layout_sect_df.at[row_num, 'chan_size'] = int((channel[1:]))
            layout_sect_df.at[row_num, 'sect_vertices'] = tuple(s.vertices())

        if s.has_xdata("cable_tag"):
            xd_way = s.get_xdata("cable_tag")
            row_num = len(ways_df)
            cab_tag_list = tuple(i[1] for i in xd_way[:-1])
            ways_df.at[row_num, 'cab_tag'] = cab_tag_list
            ways_df.at[row_num, 'layout_len'] = float(xd_way[-1][1].split(": ")[1])
            ways_df.at[row_num, 'way_vertices'] = tuple(s.vertices())

    cables_df = pd.DataFrame({'cab_tag': pd.Series(dtype='str'),
                              'layout_len': pd.Series(dtype='object'),
                              'way_vertices': pd.Series(dtype='object'),
                              })

    for k, v in ways_df.iterrows():
        for i in v.cab_tag:
            row = len(cables_df)
            cables_df.at[row, 'cab_tag'] = i
            cables_df.at[row, 'layout_len'] = v.layout_len
            cables_df.at[row, 'way_vertices'] = v.way_vertices

    print_duplicates(cables_df, 'cab_tag')

    all_sect_df = pd.DataFrame({'sect': pd.Series(dtype='str'),
                                'cab_tag': pd.Series(dtype='str'),
                                'layout_len': pd.Series(dtype='str'),
                                'cab_purpose': pd.Series(dtype='str'),
                                })

    for k1, v1 in layout_sect_df.iterrows():
        for k2, v2 in cables_df.iterrows():
            p1 = make_vec2(v1.sect_vertices)
            p2 = make_vec2(v2.way_vertices)
            int_point = ezdxf.math.intersect_polylines_2d(p1, p2, abs_tol=0.01)
            if int_point:
                row = len(all_sect_df)
                all_sect_df.at[row, 'sect'] = v1.sect
                all_sect_df.at[row, 'chan_size'] = v1.chan_size
                all_sect_df.at[row, 'chan_type'] = v1.chan_type
                all_sect_df.at[row, 'cab_tag'] = v2.cab_tag
                all_sect_df.at[row, 'layout_len'] = v2.layout_len
                all_sect_df.at[row, 'cab_purpose'] = v2.cab_tag[0]

    all_sect_df = get_data_from_cab_list(all_sect_df, cablist_df)

    all_sect_df.rename(columns={'length': 'cab_list_len', 'diam': 'cab_diam', 'bus': 'cab_bus'}, inplace=True)

    all_sect_df['chan_level'] = 0

    all_sect_df['cab_type'] = all_sect_df.compos + '-' + all_sect_df.wires.astype(
        'str') + 'x' + all_sect_df.section.astype('str')

    all_sect_df['delta'] = abs(
        round(all_sect_df.layout_len.astype('float64') - all_sect_df.cab_list_len.astype('float64'), 0))
    all_sect_df.sort_values(by=['delta'], ascending=False, inplace=True)

    if len(all_sect_df) > 0:
        st.write(":green[The table below represents the sections extracted from cable layout. Column 'delta' " \
                       "represents the difference in cable length taken from 'cable list' and 'power_layout'.]")
        st.write(":green[Please adjust your Cable List or check/update the Cable Layout if the delta is significant.]")
        st.write(":blue[Info: during cable routing script uses cable length taken from the 'power_layout']")

    st.experimental_data_editor(
        all_sect_df[['sect', 'cab_tag', 'cab_type', 'layout_len', 'cab_list_len', 'delta', 'cab_diam', 'chan_type',
                     'chan_size', 'cab_bus']], use_container_width=True)

    return all_sect_df

def distrib_cables(df_x, trays_height, volume_percent, width_percent, lv_horis_gap, mv_horis_gap):
    initial_volume = df_x.chan_size.head(1).values[0] * trays_height * volume_percent / 100
    initial_width = df_x.chan_size.head(1).values[0] * width_percent / 100
    current_volume = df_x.chan_size.head(1).values[0] * trays_height * volume_percent / 100
    current_purpose = None  # df_x.cab_purpose.head(1).values[0]
    current_level = 0

    df_x.chan_level = 0
    df_x_C = df_x.loc[df_x.cab_purpose == 'C']

    for k, v in df_x_C.iterrows():
        if current_purpose is None:
            current_purpose = 'C'
            current_level = df_x.chan_level.max() + 1
            current_volume = initial_volume

        if current_volume < v.cab_diam ** 2:
            current_level += 1
            current_volume = initial_volume

        df_x.at[k, 'chan_level'] = current_level
        current_volume -= (v.cab_diam ** 2)
        df_x.at[k, 'free_vol'] = round(current_volume, 1)

    df_x_L = df_x.loc[df_x.cab_purpose == 'L']
    current_width = None
    for k, v in df_x_L.iterrows():
        if current_purpose != 'L':
            current_purpose = 'L'
            current_level = df_x.chan_level.max() + 1
            current_width = initial_width

        if current_width < v.cab_diam:
            current_level = df_x.chan_level.max() + 1
            current_width = initial_width

        df_x.at[k, 'chan_level'] = current_level
        current_width -= v.cab_diam * (1 + lv_horis_gap / 100)
        df_x.at[k, 'free_width'] = round(current_width, 1)

    df_x_M = df_x.loc[df_x.cab_purpose == 'M']
    for k, v in df_x_M.iterrows():

        if current_purpose != 'M':
            current_purpose = 'M'
            current_level = df_x.chan_level.max() + 1
            current_width = initial_width

        if current_width < v.cab_diam:
            current_level = df_x.chan_level.max() + 1
            current_width = initial_width

        df_x.at[k, 'chan_level'] = current_level
        current_width -= v.cab_diam * (1 + mv_horis_gap / 100)
        df_x.at[k, 'free_width'] = round(current_width, 1)

    return df_x


def generate_dxf(all_sect_df, vertical_trays_gap, trays_height, volume_percent, width_percent,
                 lv_horis_gap, mv_horis_gap, sections_template_path):

    st.session_state.p_x = 0

    all_sect_df['tray_vol'] = all_sect_df.chan_size * trays_height

    doc = open_dxf_file(sections_template_path)

    msp = doc.modelspace()

    all_sect_df['free_vol'] = all_sect_df.chan_size * trays_height * volume_percent / 100
    all_sect_df['free_width'] = all_sect_df.chan_size * width_percent / 100
    sect_set = set(all_sect_df.sect)
    sect_list = sorted(sect_set)

    for section_tag in sect_list:

        df = arrange_section(all_sect_df, section_tag)

        for cur_bus in "ABCDEF-???":
            df_x = df.loc[df.cab_bus == cur_bus].reset_index(drop=True)

            if len(df_x) > 0:
                df_x = distrib_cables(df_x, trays_height, volume_percent, width_percent, lv_horis_gap, mv_horis_gap)
                to_dxf(df_x, sections_template_path, msp, vertical_trays_gap, trays_height,
                       lv_horis_gap, mv_horis_gap)
                print(f":green[Bus {cur_bus} for Section {df_x.sect[0]} is added to the drawing]")
                st.session_state.p_x += 350

    zoom.extents(msp)
    save_path = f"temp_dxf/SECTIONS_by_{st.session_state.user['login']}_" \
                f"{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')}.dxf"
    doc.saveas(save_path)

    return save_path
