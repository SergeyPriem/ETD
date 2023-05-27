# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import ezdxf
import sys, re
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Vec2

from utilities import err_handler


def kill_comma(value):
    value = float(str(value).replace(',', '.'))
    return value


def find_duplicates(df: pd.DataFrame, column_name: str) -> None:
    duplic_df = df.loc[df.duplicated(keep='last')]
    for elem in duplic_df[column_name]:
        st.write(f":red[!!! Dulicated: {elem}")


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
            print()
            print(f":red[Trouble with tag: {tag}]")
            print()

            # section_sect_df
    return section_sect_df


def arrange_section(sect_df, section_tag):
    sect_list = set(sect_df.sect)

    control_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "C")]
    control_df = control_df.sort_values(by='layout_len', ascending=False)

    lv_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "L")]
    lv_df = lv_df.sort_values(by='layout_len', ascending=False)

    mv_df = sect_df.loc[(sect_df.sect == section_tag) & (sect_df.cab_purpose == "M")]
    mv_df = mv_df.sort_values(by='layout_len', ascending=False)

    cur_sect_df = pd.concat([control_df, lv_df, mv_df], ignore_index=True)

    return cur_sect_df


def to_dxf(df, dxf_path, p_x, msp, vertical_trays_gap):
    p_y = 0
    shift = 0
    p_x_tr = p_x + 160
    p_y_tr = 0  # 10

    # p_x_cab = p_x + 160
    p_y_cab = 0  # 40

    print_scale = 10
    vertical_trays_gap /= print_scale

    sect_tag_block = msp.add_blockref('sect_num', insert=(p_x + 65, 20))

    try:
        att_values = {
            'SECT_TAG': df.sect[0]
        }
    except:
        st.write(f"Problem with 'df.sect[0]'")
        return

    sect_tag_block.add_auto_attribs(att_values)

    msp.add_blockref('tab_header', insert=(p_x, p_y))

    level_quantity = df.chan_level.max()

    chan_width = df.chan_size[0] / print_scale
    tray_width = int(df.chan_size[0])

    msp.add_text(df.sect[0], height=4, dxfattribs={"style": "ГОСТ"}
                 ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 21), align=TextEntityAlignment.CENTER)

    for support in range(1, level_quantity + 1):

        points = [(p_x_tr - 5, p_y_tr), (p_x_tr + chan_width + 5, p_y_tr),
                  (p_x_tr + chan_width + 5, p_y_tr - 5), (p_x_tr - 5, p_y_tr - 5),
                  (p_x_tr - 5, p_y_tr)]  # полка

        msp.add_lwpolyline(points)

        points = [(p_x_tr, p_y_tr + 10, 0.3, 0.3),
                  (p_x_tr, p_y_tr, 0.3, 0.3),
                  (p_x_tr + chan_width, p_y_tr, 0.35, 0.35),
                  (p_x_tr + chan_width, p_y_tr + 10, 0.5, 0.3)]  # лоток

        msp.add_lwpolyline(points)

        tray_type = str(df.loc[df.chan_level == support, 'cab_purpose'].head(1).values[0])

        if tray_type == 'C' or tray_type == 'С':
            tray_type = 'Cont.Cab.'
        else:
            tray_type += 'V'

        msp.add_text('level ' + str(support) + ' - ' + str(tray_type), height=3, dxfattribs={"style": "ГОСТ"}
                     ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 12), align=TextEntityAlignment.CENTER)

        msp.add_text('T' + str(tray_width) + "x100", height=3, dxfattribs={"style": "ГОСТ"}
                     ).set_placement((p_x_tr + chan_width / 2, p_y_tr - 4), align=TextEntityAlignment.CENTER)

        p_y_tr -= vertical_trays_gap

    msp.add_text("Vertical step", height=3, dxfattribs={"style": "ГОСТ"}
                 ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 6), align=TextEntityAlignment.CENTER)

    msp.add_text("of trays: " + str(int(vertical_trays_gap) * 10) + " mm", height=3, dxfattribs={"style": "ГОСТ"}
                 ).set_placement((p_x_tr + chan_width / 2, p_y_tr + 2), align=TextEntityAlignment.CENTER)

    level_prev = 1

    for k, v in df.iterrows():

        if level_prev < v.chan_level:
            shift = 0
            level_prev += 1

        p_x_cab = p_x + 160
        ins_block = msp.add_blockref('tab_row', insert=(p_x, p_y))
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

        if v.cab_purpose == 'M' or v.cab_purpose == 'М':
            center_point = ((p_x_cab + cab_radius + shift + 2),
                            (p_y_cab - (vertical_trays_gap * (v.chan_level - 1)) + cab_radius + 0.2))
            msp.add_circle(center_point, cab_radius)
            shift += 4 * cab_radius

        if v.cab_purpose == 'L':
            center_point = ((p_x_cab + cab_radius + shift + 2),
                            (p_y_cab - (vertical_trays_gap * (v.chan_level - 1)) + cab_radius + 0.2))
            msp.add_circle(center_point, cab_radius)
            shift += 2 * cab_radius

        if level_prev < v.chan_level:
            shift = 0
            level_prev += 1


class CrossTray():
    def __init__(self, section):
        '''
        :param section: [section number: int, channel_width: int]
        '''
        self.tray_type = None  # 'C', L, M
        self.tray_width = section[1]
        self.tray_height = 100
        self.tag = section[0]
        self.level = 0
        self.init_width = self.tray_width * 0.8
        self.init_area = self.tray_width * self.tray_height * 0.4
        self.remain_width = section[1] * 0.8
        self.remain_area = self.tray_width * self.tray_height * 0.4
        self.tray_dict = {1: [[], []]}
        self.sect_df = pd.DataFrame({'sect': pd.Series(dtype='str'),
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
                                     })
        self.spacer = 1

    def add_power_cab(self, cable):
        """
        :param cable: [cable tag, cable diameter]
        :return: None
        """
        if cable[1] > self.init_width:
            st.write('')
            st.write(f"Need to increase tray width: cable diam={cable[1]} mm")
            st.write(f"Available tray width: {self.init_width}. Cable with tag {cable[0]} is not located")
            st.write()
        else:
            if self.tray_type == None and cable[0][0] == "L":
                self.level += 1
                self.remain_width = self.init_width
                self.tray_type = "L"
                self.spacer = 1

            if self.tray_type == "C" and cable[0][0] == "L":
                self.level += 1
                self.remain_width = self.init_width
                self.tray_type = "L"
                self.spacer = 1

            if self.tray_type == None and (cable[0][0] == "M" or cable[0][0] == "М"):
                self.level += 1
                self.remain_width = self.init_width
                self.tray_type = "M"
                self.spacer = 2

            if (self.tray_type == "C" or self.tray_type == "L") and (cable[0][0] == "M" or cable[0][0] == "М"):
                self.level += 1
                self.remain_width = self.init_width
                self.tray_type = "M"
                self.spacer = 2

            if self.remain_width < cable[1]:
                self.level += 1
                self.remain_width = self.init_width

            self.sect_df.loc[len(self.sect_df.index)] = [self.tag, cable[0], cable[1], '-', 0, 0, self.level, 'TRAY',
                                                         self.tray_width, self.tray_type, '-']
            self.remain_width -= cable[1] * self.spacer

    def add_c_cab(self, cable):
        """
        :param cable: [cable tag, cable diameter]
        :return: None
        """
        if 3.142 / 4 * cable[1] ** 2 > self.init_area:
            st.write(f"Need to increase tray width: cable diam={cable[1]} mm")
            st.write(f"Available tray width: {self.init_width}. Cable with tag {cable[0]} is not located")
            st.write()
        else:
            if self.tray_type == None and cable[0][0] == "C":
                self.remain_width = self.init_width
                self.level += 1
                self.tray_type = "C"
                self.spacer = 1

            if self.remain_area < (3.142 / 4 * cable[1] ** 2):  # not enough room
                self.level += 1
                self.remain_area = self.init_area

            self.sect_df.loc[len(self.sect_df.index)] = [self.tag, cable[0], cable[1], '-', 0, 0, self.level, 'TRAY',
                                                         self.tray_width, 'С', '-']
            self.remain_area -= (3.142 / 4 * cable[1] ** 2)


# Get Tags from Cable List

def replace_cyrillic(text):
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

    if bool(re.search('[а-яА-Я]', text)):
        st.write(f':yellow[! Cyrillic Symbols in the tag {text}]')
        for letter in letter_dict.keys():
            if letter in text:
                st.write(f'Cyrillic Symbol: {letter}')
                text = text.replace(letter, letter_dict[letter])
    return text


def get_cable_df(cl_path):
    try:
        xl = pd.ExcelFile(cl_path)
    except FileNotFoundError as e:
        st.write(e, '\n')
        sys.exit(0)

    sheet_name_list = xl.sheet_names

    if len(sheet_name_list) == 1:
        sheet_name = sheet_name_list[0]
    else:
        for index, sheet_name in enumerate(sheet_name_list):
            st.write(f"{index + 1}: {sheet_name}")

        sheet_number = int(input(f'File has multiple sheets Enter the required sheet number: '))

        try:
            sheet_name = sheet_name_list[sheet_number - 1]
        except:
            st.write('Sheet with this number not available. Try again')
            return
        return xl.parse(sheet_name)


# main2
def get_tags_from_cablist(cablist_df, from_unit, to_unit, all_chb):

    try:
        cablist_df.cableTag = cablist_df.cableTag.apply(replace_cyrillic)
        cablist_df.cableTag.replace(r'\s+', '', regex=True, inplace=True)
        cablist_df.cableTag.replace(r'--', '-', regex=True, inplace=True)
        st.write()
        st.write(f":blue[-- Begin of Selected List --]")

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

        st.write(f":blue[-- End of Selected List --]")
    except Exception as e:
        st.write(f':red[!!! Data from selected sheet are not valid. Try again, {err_handler(e)}')


# PROCESS CABLE LAYOUT
def make_vec2(cell):
    # st.write([Vec2(i) for i in cell])
    return [Vec2(i) for i in cell]


def print_duplicates(cables_df, col_name):
    dup_cab_df = cables_df.loc[cables_df.duplicated(subset=[col_name], keep='first')]
    if len(dup_cab_df) > 0:
        st.write(f":red[Duplicated '{col_name}': \n{dup_cab_df[col_name]}")
    else:
        st.write(f":green[Check for '{col_name}' duplicates - OK!]")


def get_data_from_cab_list(cables_df, cablist_df):

    st.experimental_show(cablist_df)

    cablist_reduced_df = cablist_df[['cableTag', 'length', 'wires', 'section', 'compos', 'diam', 'bus']]
    cables_df = pd.merge(cables_df, cablist_reduced_df, how='left', left_on='cab_tag', right_on='cableTag')
    return cables_df


def gener_section(cablist_df, p_x, df_b, section, sect_df, sections_template_path, msp, vertical_trays_gap, reply):
    for k, v in df_b.iterrows():
        if v.cab_purpose == "C":
            section.add_c_cab([v.cab_tag, v.cab_diam])
        else:
            section.add_power_cab([v.cab_tag, v.cab_diam])

    sect_final_df = get_cab_data(cablist_df, section.sect_df)
    sect_final_df = get_layout_length(sect_df, sect_final_df)
    find_duplicates(sect_final_df, 'cab_tag')

    if sect_final_df.shape[0] > 0:
        to_dxf(sect_final_df, sections_template_path, p_x, msp, vertical_trays_gap)
        st.write(f":green[Section {sect_final_df.sect[0]} is added to the drawing]")
        p_x += 350
    else:
        st.write(reply)


# main3
def process_cable_layout(layout_path, cablist_df):  # main3
    try:
        doc = ezdxf.readfile(layout_path)
    except IOError:
        st.write(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        st.write(f"Invalid or corrupted DXF file.")
        sys.exit(2)

    # getting modelspace layout
    msp = doc.modelspace()

    p_lines = msp.query('*[layer=="power_layout"]')

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
            st.write('sect=', xd_section) ###
            st.write('sect_vertices=',tuple(s.vertices())) ###
            row_num = len(layout_sect_df)
            layout_sect_df.at[row_num, 'sect'] = xd_section[0][1].split(": ")[1]
            channel = xd_section[1][1].split(": ")[1]
            layout_sect_df.at[row_num, 'chan_type'] = str(channel[:1])
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

    cables_df = get_data_from_cab_list(cables_df, cablist_df)

    final_sect_df = pd.DataFrame({'sect': pd.Series(dtype='str'),
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
                row = len(final_sect_df)
                final_sect_df.at[row, 'sect'] = v1.sect
                final_sect_df.at[row, 'chan_size'] = v1.chan_size
                final_sect_df.at[row, 'cab_tag'] = v2.cab_tag
                final_sect_df.at[row, 'layout_len'] = v2.layout_len
                final_sect_df.at[row, 'cab_purpose'] = v2.cab_tag[0]


    st.write('cablist_df')
    st.write(type(cablist_df))

    sect_df = get_data_from_cab_list(final_sect_df, cablist_df)

    sect_df.rename(columns={"length": "cab_list_len"}, inplace=True)

    sect_df['delta'] = abs(round(sect_df.layout_len.astype('float64') - sect_df.cab_list_len.astype('float64'), 0))
    sect_df.sort_values(by=['delta'], ascending=False, inplace=True)

    if len(sect_df) > 0:
        st.write(f":yellow[The table below represents the sections extracted from cable layout]")
        st.write("Column 'delta' represents the difference in cable length taken from 'cable list' and 'power_layout'")
        st.write("Please adjust your cable list or check/update the routing at the layout")
        st.write("Info: during cable routing script uses cable length taken from the 'power_layout'")

    st.write(sect_df[['sect', 'cab_tag', 'compos', 'wires', 'section', 'layout_len', 'cab_list_len', 'delta',
                      'diam', 'chan_size',
                      'bus']])


# main4
def generate_dxf(sect_df, sections_template_path, cablist_df):
    vertical_trays_gap = 300

    sect_set = set(sect_df.sect)

    p_x = 0
    sect_list = sorted(sect_set)

    try:
        doc = ezdxf.readfile(sections_template_path)
    except IOError:
        st.write(f"Not a DXF file or a generic I/O error.")
        sys.exit(1)
    except ezdxf.DXFStructureError:
        st.write(f"Invalid or corrupted DXF file.")
        sys.exit(2)

    # getting modelspace layout
    msp = doc.modelspace()

    sect_final_df = pd.DataFrame()
    # df = pd.DataFrame()

    for section_tag in sect_list:

        df = arrange_section(sect_df, section_tag)
        df = get_cab_data(cablist_df, df)

        df_a = df.loc[df.cab_bus == "A"].reset_index(drop=True)

        if len(df_a) > 0:
            section = CrossTray([section_tag + ": bus A", int(df_a.chan_size.min())])

            for k, v in df_a.iterrows():
                if v.cab_purpose == "C":
                    section.add_c_cab([v.cab_tag, v.cab_diam])
                else:
                    section.add_power_cab([v.cab_tag, v.cab_diam])

            sect_final_df = get_cab_data(cablist_df, section.sect_df)
            sect_final_df = get_layout_length(sect_df, sect_final_df)
            find_duplicates(sect_final_df, 'cab_tag')

            if sect_final_df.shape[0] > 0:
                to_dxf(sect_final_df, sections_template_path, p_x, msp, vertical_trays_gap)
                st.write(f":green[Section {sect_final_df.sect[0]} is added to the drawing]")
                p_x += 350
            else:
                st.write(f":red[Empty table of cables for {section_tag}: bus A]")

        df_b = df.loc[df.cab_bus == "B"].reset_index(drop=True)
        if len(df_b) > 0:
            section = CrossTray([section_tag + ": bus B", int(df_b.chan_size.min())])

            for k, v in df_b.iterrows():
                if v.cab_purpose == "C":
                    section.add_c_cab([v.cab_tag, v.cab_diam])
                else:
                    section.add_power_cab([v.cab_tag, v.cab_diam])

                sect_final_df = get_cab_data(cablist_df, section.sect_df)
                sect_final_df = get_layout_length(sect_df, sect_final_df)
                find_duplicates(sect_final_df, 'cab_tag')

            if sect_final_df.shape[0] > 0:
                to_dxf(sect_final_df, sections_template_path, p_x, msp, vertical_trays_gap)
                st.write(f":green[Section {sect_final_df.sect[0]} is added to the drawing")
                p_x += 350
            else:
                st.write(f":red[Empty table of cables for {section_tag}: bus B]")

        df_c = df.loc[df.cab_bus == "C"].reset_index(drop=True)
        if len(df_c) > 0:
            section = CrossTray([section_tag + ": bus C", int(df_c.chan_size.min())])

            reply = f":red[Empty table of cables for {section_tag}: bus C]"

            gener_section(cablist_df, df_b, section, sect_df, sections_template_path, msp, vertical_trays_gap, reply)

        df_un = df.loc[(df.cab_bus == "-")].reset_index(drop=True)

        if len(df_un) > 0:
            section = CrossTray([section_tag + ": unknown bus!", int(df_un.chan_size.min())])

            reply = f":red[Empty table of cables for {section_tag}: : unknown bus!]"

            gener_section(p_x, df_b, section, sect_df, sections_template_path, msp, vertical_trays_gap, reply)

    doc.saveas('/content/SECTIONS.dxf')

    st.write("+----------------------------------------------+")
    st.write("| Please, download file: /content/SECTIONS.dxf |")
    st.write("+----------------------------------------------+")
