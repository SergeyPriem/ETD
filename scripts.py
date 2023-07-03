# -*- coding: utf-8 -*-
import datetime
import io
import streamlit as st
import pandas as pd
import numpy as np
import math
import os

from create_xml import add_main_bus, add_feeder
from section_generator import get_tags_from_cablist, generate_dxf, get_sect_from_layout
from users import err_handler, reg_action
from utilities import center_style, open_dxf_file, check_df

# p_rat_a = 0
# p_rat_b = 0
# p_rat_em = 0

cab_dict = {
    1.5: 1.5, 2.5: 2.5, 4: 4,
    6: 6, 10: 10, 16: 16,
    25: 25, 35: 25, 50: 25,
    70: 35, 95: 70, 120: 70,
    150: 95, 185: 95, 240: 150,
    300: 150, 400: 240
}

cableTagList = []
loadRatList = []
voltsList = []
fromUnitList = []
fromTagList = []
columnList = []
fromDescrList = []
toUnitList = []
toTagList = []
toDescrList = []
refList = []
wiresList = []
sectionList = []
uList = []
composList = []
configList = []
lengthList = []
diamList = []
weightList = []
glandTypeList = []
glandSizeList = []
accList = []
mcsTypeList = []
conduitSizeList = []
conduitLengthList = []
busList = []

compositDic = {
    1: 'PH',
    2: 'PHN',
    3: 'PHNG',
    4: '3PHG',
    5: '3PHNG'
}


def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("temp_dxf", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return uploaded_file.name
    except Exception as e:
        st.warning(f"Can't save file to temp. folder: {err_handler(e)}")
        st.stop()


def max_nearest(target: int) -> int:
    lst = [4, 6, 10, 16, 25, 32, 40, 63, 80, 100, 125, 160, 250, 320,
           400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000,
           6300, 8000, 10000, 12500, 16000, 20000, 25000, 32000, 40000]
    for a in lst:
        if a >= target:
            return int(a)
    return 63000


def cab_diam(purpose: str, composition: str, wires: int, section: float, diam_df) -> float:
    if composition.find('SWA') != -1:
        constr = 'SWA'
    else:
        constr = 'NOT-SWA'

    diameter = diam_df.loc[(diam_df['purpose'] == purpose) &
                           (diam_df['altConstr'] == constr) &
                           (diam_df['section'] == str(wires) + 'x' + str(section))]['outerDiam'].values[0]
    return round(diameter, 1)


def cab_weight(purpose: str, composition: str, wires: int, section: float, diam_df, ex_df):
    try:
        if composition.find('SWA') != -1:
            constr = 'SWA'
        else:
            constr = 'NOT-SWA'
        weight = diam_df.loc[(diam_df['purpose'] == purpose) &
                             (diam_df['altConstr'] == constr) &
                             (diam_df['section'] == str(wires)
                              + 'x' + str(section))]['weight'].values[0]
        return weight
    except:
        return "Нет данных"


def gland_type(site_tag: str, ex_df) -> str:
    hazValue = ex_df.loc[ex_df.tagNoCut == site_tag]['hazard']
    try:
        if hazValue.values[0] == 'Hazardous':
            return 'Ex d'
        else:
            return 'normal'
    except:
        return "Нет данных"


def gland_size(diam: float, cab_type: str, glands_df) -> str:
    if cab_type.find('SWA') != -1:
        cab_typeM = 'armoured'
    else:
        cab_typeM = 'unarmoured'
    try:
        gl_diam = \
            glands_df.loc[(glands_df['type'] == cab_typeM) & (glands_df.overMin <= diam) & (glands_df.overMax >= diam)][
                'metric']
        return gl_diam.values[0]
    except:
        return 'Нет данных'


def num_list(num: int) -> str:
    ret_list = ''
    for i in range(num):
        ret_list = ret_list + str(i + 1) + ","
    return str(ret_list[:-1])


def round5(val: float) -> int:
    return math.ceil(val / 5) * 5


def incom_sect_cb_calc(loads_df: pd.DataFrame) -> pd.DataFrame:

    loads_df.loc[(loads_df.load_duty == 'C') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 'c_kw'] = loads_df.abs_power / loads_df.eff

    loads_df.loc[(loads_df.load_duty == 'I') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 'i_kw'] = loads_df.abs_power / loads_df.eff

    loads_df.loc[(loads_df.load_duty == 'S') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 's_kw'] = loads_df.abs_power / loads_df.eff

    loads_df.loc[(loads_df.load_duty == 'C') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 'c_kvar'] = \
        loads_df.abs_power / loads_df.eff * np.tan(np.arccos(loads_df.power_factor))

    loads_df.loc[(loads_df.load_duty == 'I') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 'i_kvar'] = \
        loads_df.abs_power / loads_df.eff * np.tan(np.arccos(loads_df.power_factor))

    loads_df.loc[(loads_df.load_duty == 'S') & (loads_df.equip != 'INCOMER') & (
            loads_df.equip != 'SECT_BREAKER'), 's_kvar'] = \
        loads_df.abs_power / loads_df.eff * np.tan(np.arccos(loads_df.power_factor))

    c_kw_a = loads_df.loc[loads_df.bus == 'A', 'c_kw'].sum()
    c_kw_b = loads_df.loc[loads_df.bus == 'B', 'c_kw'].sum()
    i_kw_a = loads_df.loc[loads_df.bus == 'A', 'i_kw'].sum()
    i_kw_b = loads_df.loc[loads_df.bus == 'B', 'i_kw'].sum()
    # if A
    c_kvar_a = loads_df.loc[loads_df.bus == 'A', 'c_kvar'].sum()
    c_kvar_b = loads_df.loc[loads_df.bus == 'B', 'c_kvar'].sum()
    i_kvar_a = loads_df.loc[loads_df.bus == 'A', 'i_kvar'].sum()
    i_kvar_b = loads_df.loc[loads_df.bus == 'B', 'i_kvar'].sum()
    s_kvar_a = loads_df.loc[loads_df.bus == 'A', 's_kvar'].sum()
    s_kvar_b = loads_df.loc[loads_df.bus == 'B', 's_kvar'].sum()
    max_i_kw_a = loads_df.loc[(loads_df.bus == 'A') & (loads_df.equip == 'MOTOR'), 'i_kw'].max()
    max_i_kw_b = loads_df.loc[(loads_df.bus == 'B') & (loads_df.equip == 'MOTOR'), 'i_kw'].max()
    max_i_kvar_a = loads_df.loc[(loads_df.bus == 'A') & (loads_df.equip == 'MOTOR'), 'i_kvar'].max()
    max_i_kvar_b = loads_df.loc[(loads_df.bus == 'B') & (loads_df.equip == 'MOTOR'), 'i_kvar'].max()
    rated_power_kw_a = round(c_kw_a + max(i_kw_a * 0.3, max_i_kw_a), 1)
    rated_power_kw_b = round(c_kw_b + max(i_kw_b * 0.3, max_i_kw_b), 1)
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'A'), 'rated_power'] = rated_power_kw_a
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_power'] = rated_power_kw_b
    rated_power_kvar_a = round(c_kvar_a + max(i_kvar_a * 0.3, max_i_kvar_a), 1)  ####
    rated_power_kvar_b = round(c_kvar_b + max(i_kvar_b * 0.3, max_i_kvar_b), 1)
    power_factor_a = round(rated_power_kw_a / math.sqrt(rated_power_kw_a ** 2 + rated_power_kvar_a ** 2), 2)
    power_factor_b = round(rated_power_kw_b / math.sqrt(rated_power_kw_b ** 2 + rated_power_kvar_b ** 2), 2)
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'A'), 'power_factor'] = power_factor_a
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'power_factor'] = power_factor_b
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'A'), 'rated_current'] = round(
        rated_power_kw_a / 1.732 / 0.4 / power_factor_a, 1)
    loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_current'] = round(
        rated_power_kw_b / 1.732 / 0.4 / power_factor_b, 1)
    sect_br_rated_current = round(
        max(rated_power_kw_a / 1.732 / 0.4 / power_factor_a, rated_power_kw_b / 1.732 / 0.4 / power_factor_b), 1)
    loads_df.loc[(loads_df.equip == 'INCOMER'), 'eff'] = 1
    #########################################
    # -------------------------------- POST-EMERGENCY MODE ---------------------------------
    c_kw_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 'c_kw'].sum()
    i_kw_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 'i_kw'].sum()
    s_kw_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 's_kw'].sum()
    c_kvar_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 'c_kvar'].sum()
    i_kvar_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 'i_kvar'].sum()
    s_kvar_pe = loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER'), 's_kvar'].sum()
    max_i_kw_pe = loads_df.loc[(loads_df.equip == 'MOTOR'), 'i_kw'].max()
    max_i_kvar_pe = loads_df.loc[(loads_df.equip == 'MOTOR'), 'i_kvar'].max()
    max_s_kw_pe = loads_df.loc[(loads_df.equip == 'MOTOR'), 's_kw'].max()
    max_s_kvar_pe = loads_df.loc[(loads_df.equip == 'MOTOR'), 's_kvar'].max()
    rated_power_kw_pe = c_kw_pe + max(i_kw_pe * 0.3, max_i_kw_pe) + max(s_kw_pe * 0.1, max_s_kw_pe)
    rated_power_kvar_pe = c_kvar_pe + max(i_kvar_pe * 0.3, max_i_kvar_pe) + max(s_kvar_pe * 0.1, max_s_kvar_pe)
    loads_df.loc[(loads_df.equip == 'INCOMER'), 'peak_kw_pe'] = rated_power_kw_pe
    loads_df.loc[(loads_df.equip == 'INCOMER'), 'peak_kvar_pe'] = rated_power_kvar_pe
    power_factor_pe = rated_power_kw_pe / math.sqrt(rated_power_kw_pe ** 2 + rated_power_kvar_pe ** 2)
    loads_df.loc[(loads_df.equip == 'INCOMER'), 'power_factor_pe'] = power_factor_pe
    rated_current_pe = rated_power_kw_pe / 1.732 / 0.4 / power_factor_pe
    loads_df.loc[(loads_df.equip == 'INCOMER'), 'rated_current_pe'] = rated_current_pe
    loads_df.loc[(loads_df.equip == 'SECT_BREAKER'), 'rated_current_pe'] = (
            rated_current_pe * (loads_df.loc[(loads_df.equip == 'INCOMER'), 'rated_current'].max()
                                ) / (loads_df.loc[(loads_df.equip == 'INCOMER'), 'rated_current'].sum()))

    if (loads_df.loc[(loads_df.bus == 'B') & (loads_df.equip != 'INCOMER')]).shape[0] == 0:
        st.write("ATTENTION: We are working with singe-bus panel!")
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_power'] = rated_power_kw_a
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'power_factor'] = power_factor_a
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_current'] = round(
            rated_power_kw_a / 1.732 / 0.4 / power_factor_a, 1)

        loads_df = loads_df.loc[loads_df.equip != "SECT_BREAKER"].reset_index(drop=True)
    return loads_df


def bus_loads(loads_df):
    p_rat_a = round(loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER') & (
            loads_df.bus == 'A'), 'rated_power'].sum(), 1)

    p_rat_b = round(loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER') & (
            loads_df.bus == 'B'), 'rated_power'].sum(), 1)

    p_rat_em = round(
        loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != "SECT_BREAKER"), 'rated_power'].sum(), 1)

    if (loads_df.loc[(loads_df.bus == 'B') & (loads_df.equip != 'INCOMER')]).shape[0] == 0:
        p_rat_b = p_rat_a
        p_rat_em = p_rat_a

    return p_rat_a, p_rat_b, p_rat_em


def tags_for_control_cab(row: int, loads_df: pd.DataFrame, load_tag_short) -> pd.DataFrame:
    if loads_df.rated_power[row] >= 30:
        loads_df.loc[row, 'LCS1-CABLE_TAG1'] = "C-" + loads_df['panel_tag'][row] + loads_df['bus'][
            row] + "-" + load_tag_short + "LCS1-1"
        loads_df.loc[row, 'LCS1-CABLE_TAG2'] = "C-" + loads_df['panel_tag'][row] + loads_df['bus'][
            row] + "-" + load_tag_short + "LCS1-2"
        loads_df.loc[row, 'LCS1-CABLE_TYPE1'] = loads_df['control_type'][row] + '-10x1.5mm2, L=' + str(
            loads_df['length'][row]) + 'm'
        loads_df.loc[row, 'LCS1-CABLE_TYPE2'] = loads_df['control_type'][row] + '-3x2.5mm2, L=' + str(
            loads_df['length'][row]) + 'm'
    else:
        loads_df.loc[row, 'LCS1-CABLE_TAG1'] = "C-" + loads_df['panel_tag'][row] + loads_df['bus'][
            row] + "-" + load_tag_short + "LCS1"
        loads_df.loc[row, 'LCS1-CABLE_TYPE1'] = loads_df['control_type'][row] + '-10x1.5mm2, L=' + str(
            loads_df['length'][row]) + 'm'

    return loads_df


def fill_lists(i: int, panelDescr, loads_df) -> None:
    accList.append(pd.NA)
    busList.append(loads_df.bus[i])
    columnList.append(pd.NA)
    conduitLengthList.append(pd.NA)
    conduitSizeList.append(pd.NA)
    diamList.append(pd.NA)
    fromDescrList.append(panelDescr)
    fromTagList.append(loads_df.panel_tag[i])
    fromUnitList.append(str(loads_df.panel_tag[i])[:6])
    glandSizeList.append(pd.NA)
    glandTypeList.append(pd.NA)
    mcsTypeList.append(pd.NA)
    refList.append(pd.NA)
    toUnitList.append(loads_df.load_tag[i][:6])
    uList.append('0.6/1kV')
    voltsList.append(400)
    weightList.append(pd.NA)


def check_loads(loads_df):

    checkLoads_df = loads_df.iloc[:, 0:27].copy()


    null_df = checkLoads_df.isnull()

    # st.experimental_show(null_df)

    row_with_null = null_df.any(axis=1)

    # st.experimental_show(row_with_null)

    with_null_df = checkLoads_df[row_with_null]

    # st.experimental_show(with_null_df)

    if len(with_null_df) > 0:
        st.warning("Some cells are empty...Script Aborted")
        st.experimental_show(with_null_df)
        st.stop()


    if (checkLoads_df.isnull().sum()).sum() > 0:
        st.warning(f'Load List has {(checkLoads_df.isnull().sum()).sum()} empty fields...Update Load List')
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.eff.min() == 0:
        st.warning("Nulls in 'efficiency' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.power_factor.min() == 0:
        st.warning("Nulls in 'power factor' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.abs_power[3:].min() == 0:
        st.warning("Nulls in 'abs_power' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.rated_power[3:].min() == 0:
        st.warning("Nulls in 'rated_power' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.usage_factor[3:].min() == 0:
        st.warning("Nulls in 'usage_factor' column")
        st.write('Script aborted')
        st.stop()

    dup_ser = checkLoads_df.loc[checkLoads_df.duplicated(subset=['load_tag'], keep=False), 'load_tag']
    if len(dup_ser):
        st.write('<h4 style="color:red;">Duplicates in Load Tags!!!</h4>', unsafe_allow_html=True)
        # st.write(dup_ser)
        for ind, val in dup_ser.items():
            st.write(f"<h5 style='color:orange;''>Tag '{val}' in row '{ind+2}'</h5>", unsafe_allow_html=True)

        st.write('<h4 style="color:red;">Remove Duplicates and Reload File</h4>', unsafe_allow_html=True)
        st.stop()

    st.text('')
    st.success('Loads Data are Valid')


def prepare_loads_df(loads_df):
    loads_df['length'] = round(loads_df['length'] / 5, 0) * 5

    loads_df['VFD_AMPACITY'] = '-'
    loads_df['VFD_TAG'] = '-'

    loads_df[
        ['CONT_AMPACITY', 'HEATER-CABLE_TAG', 'HEATER-CABLE_TYPE', 'LCS1-CABLE_TAG1', 'LCS1-CABLE_TYPE1',
         'LCS1-CABLE_TAG2', 'LCS1-CABLE_TYPE2', 'LCS2-CABLE_TAG', 'LCS2-CABLE_TYPE']] = '-'

    loads_df[['c_kw', 'i_kw', 's_kw', 'c_kvar', 'i_kvar', 's_kvar', 'peak_kw_pe', 'peak_kvar_pe', 'power_factor_pe',
              'rated_current_pe']] = 0

    return loads_df


    #  NORMAL MODE

def sect_calc(cab_df, row: int, u_c: int, power: float, rated_current: float, derat_factor: float,
              cos_c: float, k_start: float, len_c: float, min_sect: object, u_drop_al: float, busduct: bool,
              cos_start: float, sin_start: float, loads_df) -> tuple:

    if busduct:
        return 1, 1000, 1000, 0
    global section, voltage_drop, pe_sect

    par = 0
    cab = 0

    for par in range(1, 25):

        checker = True
        section = 0
        pe_sect = 0
        voltage_drop = 0

        start_sect = 1 if min_sect == '2.5' else 0

        for cab in range(start_sect, 15):
            r_c = cab_df.R0[cab]
            x_c = cab_df.X0[cab]
            sin_c = math.sin(math.acos(cos_c))
            voltage_drop = (((r_c * cos_c + x_c * sin_c) / (10 * u_c * u_c * cos_c)) * power * len_c * 1000 / par)

            if k_start > 1:
                voltage_drop_start = (((r_c * cos_start + x_c * sin_start) / (
                        10 * u_c * u_c * cos_c)) * power * len_c * 1000 * k_start / par)
            else:
                voltage_drop_start = voltage_drop

            volt_start_check = voltage_drop_start > 20
            volt_check = voltage_drop > u_drop_al  # voltage drop mare than applicable
            current_c = rated_current * 1.3  # ток кабеля должен быть больше тока автомата

            cab_current = cab_df.rat_current[cab] * derat_factor * par


            cur_check = current_c >= cab_current  # load more than applicable curent of cable
            checker = not (not cur_check and not volt_check and not volt_start_check)

            if checker:
                continue
            else:
                break

        if checker:
            continue
        else:
            section = cab_df.section[cab]
            voltage_drop = round(voltage_drop, 1)

            if loads_df['pe_num'][row] == 1:
                pe_sect = cab_dict[section]
            else:
                pe_sect = section

            break
    return par, section, pe_sect, voltage_drop


def sc_rating_polarity(max_sc, loads_df, row):
    if loads_df.starter_type[row] != 'CB':
        loads_df.loc[row, 'RAT_POL'] = str(max_sc) + 'kA, 3P'
    else:
        loads_df.loc[row, 'RAT_POL'] = str(max_sc) + 'kA, 4P'

    if loads_df.CB_AMPACITY[row] < 100:
        loads_df.loc[row, 'CB_RATING'] = 100
    else:
        loads_df.loc[row, 'CB_RATING'] = max_nearest(loads_df.CB_AMPACITY[row])

    return loads_df


def create_cab_list(contr_but_len, loads_df, panelDescr, diam_df, ex_df, glands_df):
    for i in range(len(loads_df.index)):
        if not pd.isnull(loads_df['CONSUM-CABLE_TAG'][i]):
            if loads_df.parallel[i] > 1:
                for k in range(int(loads_df.parallel[i])):
                    fill_lists(i, panelDescr, loads_df)

                    lengthList.append(loads_df.length[i])
                    wiresList.append(loads_df.ph_num[i] + loads_df.pe_num[i])
                    toDescrList.append(loads_df.load_service[i].strip() + '. ' + loads_df.equip[i])
                    toTagList.append(loads_df.load_tag[i])
                    configList.append(compositDic[loads_df.ph_num[i] + loads_df.pe_num[i]])
                    loadRatList.append(str(round(loads_df.rated_power[i], 1)) + '/' + str(loads_df.parallel[i]))
                    cableTagList.append(loads_df['CONSUM-CABLE_TAG'][i] + '-' + str(k + 1))
                    compos_int = str(loads_df['CONSUM-CABLE_TYPE'][i]).split('-')[0]
                    composList.append(compos_int.split('x')[1])

                    if loads_df['section'][i] == loads_df.pe_sect[i]:
                        finSection = str(loads_df['section'][i]).replace('.0', '')
                    else:
                        finSection = str(loads_df['section'][i]).replace('.0', '') + '/' + str(
                            loads_df.pe_sect[i]).replace(
                            '.0', '')
                    sectionList.append(finSection)

            else:
                fill_lists(i, panelDescr, loads_df)

                wiresList.append(loads_df.ph_num[i] + loads_df.pe_num[i])
                lengthList.append(loads_df.length[i])
                toDescrList.append(loads_df.load_service[i].strip() + '. ' + loads_df.equip[i])
                toTagList.append(loads_df.load_tag[i])
                configList.append(compositDic[loads_df.ph_num[i] + loads_df.pe_num[i]])
                loadRatList.append(str(round(loads_df.rated_power[i], 1)))
                cableTagList.append(loads_df['CONSUM-CABLE_TAG'][i])
                composList.append(str(loads_df['CONSUM-CABLE_TYPE'][i]).split('-')[0])
                if loads_df['section'][i] == loads_df.pe_sect[i]:
                    finSection = str(loads_df['section'][i]).replace('.0', '')
                else:
                    finSection = str(loads_df['section'][i]).replace('.0', '') + '/' + str(loads_df.pe_sect[i]).replace(
                        '.0', '')
                sectionList.append(finSection)

        if not pd.isnull(loads_df['HEATER-CABLE_TAG'][i]):
            fill_lists(i, panelDescr, loads_df)

            lengthList.append(loads_df.length[i])
            wiresList.append(3)
            loadRatList.append('-')
            cableTagList.append(loads_df['HEATER-CABLE_TAG'][i])
            toTagList.append(loads_df.load_tag[i][:-1] + "SH")
            configList.append('PHNG')
            sectionList.append('2.5')
            toDescrList.append(loads_df.load_service[i].strip() + '. SPACE HEATER')
            composList.append(str(loads_df['HEATER-CABLE_TYPE'][i]).split('-')[0])

        if not pd.isnull(loads_df['LCS1-CABLE_TAG1'][i]):
            fill_lists(i, panelDescr, loads_df)

            lengthList.append(loads_df.length[i])
            wiresList.append(10)
            sectionList.append('1.5')
            configList.append('MC')
            loadRatList.append('-')
            toTagList.append(loads_df.load_tag[i][:-1] + "LCS1")
            composList.append(str(loads_df['LCS1-CABLE_TYPE1'][i]).split('-')[0])
            toDescrList.append(loads_df.load_service[i].strip() + '. LOCAL CONTROL STATION. PUSHBUTTONS')
            cableTagList.append(loads_df['LCS1-CABLE_TAG1'][i])

        if not pd.isnull(loads_df['LCS1-CABLE_TAG2'][i]):
            fill_lists(i, panelDescr, loads_df)

            lengthList.append(loads_df.length[i])
            wiresList.append(3)
            cableTagList.append(loads_df['LCS1-CABLE_TAG2'][i])
            composList.append(str(loads_df['LCS1-CABLE_TYPE2'][i]).split('-')[0])
            sectionList.append('2.5')
            toDescrList.append(loads_df.load_service[i].strip() + '. LOCAL CONTROL STATION. AMMETER')
            configList.append('MC')
            loadRatList.append('-')
            toTagList.append(loads_df.load_tag[i][:-1] + "LCS1")

        if not pd.isnull(loads_df['LCS2-CABLE_TAG'][i]):
            fill_lists(i, panelDescr, loads_df)

            lengthList.append(contr_but_len)
            wiresList.append(3)
            sectionList.append('1.5')
            cableTagList.append(loads_df['LCS2-CABLE_TAG'][i])
            composList.append(str(loads_df['LCS2-CABLE_TYPE'][i]).split('-')[0])
            toDescrList.append(loads_df.load_service[i].strip() + '. EMERGENCY PUSHBUTTON')
            configList.append('MC')
            loadRatList.append('-')
            toTagList.append(loads_df.load_tag[i][:-1] + "LCS2")

    cab_dic = {
        'cableTag': cableTagList,
        'loadRat': loadRatList,
        'volts': voltsList,
        'fromUnit': fromUnitList,
        'fromTag': fromTagList,
        'bus': busList,
        'fromDescr': fromDescrList,
        'toUnit': toUnitList,
        'toTag': toTagList,
        'toDescr': toDescrList,
        'ref': refList,
        'wires': wiresList,
        'section': sectionList,
        'u': uList,
        'compos': composList,
        'config': configList,
        'length': lengthList,
        'diam': diamList,
        'weight': weightList,
        'glandType': glandTypeList,
        'glandSize': glandSizeList,
        'acc': accList,
        'mcsType': mcsTypeList,
        'conduitSize': conduitSizeList,
        'conduitLength': conduitLengthList,
    }

    cl_df = pd.DataFrame(cab_dic)

    cl_df = cl_df.query("toDescr != 'INCOMER TO SECT. A. INCOMER' and toDescr != 'INCOMER TO SECT. B. INCOMER'")
    cl_df = cl_df.query("bus != 'A_B'")
    cl_df = cl_df.query('cableTag != "-"')

    cl_df.reset_index(drop=True, inplace=True)
    #
    cl_df.section = cl_df.section.str.replace('/.0', '', regex=True)

    for y in range(len(cl_df.compos)):
        if cl_df.cableTag[y][:1] == 'L':
            purpose = 'power'
        else:
            purpose = 'control'
        try:
            cl_df.loc[y, 'diam'] = cab_diam(purpose, cl_df.compos[y], cl_df.wires[y], cl_df.section[y], diam_df)
            cl_df.loc[y, 'weight'] = cab_weight(purpose, cl_df.compos[y], cl_df.wires[y], cl_df.section[y],
                                                diam_df, ex_df)

            # cab_weight(purpose, composition, wires, section, diam_df, ex_df)

            cl_df.loc[y, 'glandType'] = gland_type(cl_df.toUnit[y], ex_df)
            cl_df.loc[y, 'glandSize'] = gland_size(cl_df.diam[y], cl_df.compos[y], glands_df)
        except Exception as e:
            st.warning('Ошибка определения диаметра кабеля: ', cl_df.cableTag[y])
            e_str = f"{cl_df.cableTag[y]} > {err_handler(e)}"
            st.write(e_str)

    for i in range(len(loads_df.parallel)):
        if loads_df.parallel[i] > 1:
            loads_df.loc[i, 'CONSUM-CABLE_TAG'] += '-(' + num_list(int(loads_df.parallel[i])) + ')'

    cl_df.cableTag = cl_df.cableTag.str.replace('710-', '', regex=True)
    cl_df.cableTag = cl_df.cableTag.str.replace('715-', '', regex=True)

    loads_df.set_index('load_tag', inplace=True)

    cl_df.loadRat = cl_df.loadRat.astype(str).replace('\.0', '', regex=True)

    cl_df = cl_df.query('cableTag != "-"')

    cl_df.set_index('cableTag', inplace=True)

    return cl_df

def replace_zero(loads_df):
    loads_df['CONSUM-CABLE_TYPE'] = loads_df['CONSUM-CABLE_TYPE'].astype(str).str.replace('\.0mm2', 'mm2', regex=True)
    loads_df['CONSUM-CABLE_TYPE'] = loads_df['CONSUM-CABLE_TYPE'].astype(str).str.replace('\.0/', '/', regex=True)
    loads_df['CONT_AMPACITY'] = loads_df['CONT_AMPACITY'].astype(str).str.replace('\.0A', 'A', regex=True)
    loads_df['CB_AMPACITY'] = loads_df['CB_AMPACITY'].astype(str).str.replace('\.0', '', regex=True)
    loads_df['CB_RATING'] = loads_df['CB_RATING'].astype(str).str.replace('\.0', '', regex=True)
    loads_df['CB_SET'] = loads_df['CB_SET'].astype(str).str.replace('\.0A', 'A', regex=True)
    loads_df['rated_current'] = round(loads_df['rated_current'], 1)

    return loads_df


def making_cablist(loads_df, incom_margin, cab_df, show_settings, min_sect, contr_but_len, sin_start, cos_start,
                   max_sc):
    for row in range(len(loads_df)):
        # select cable by rated current
        derat_factor = loads_df['instal_derat'][row] * loads_df['temp_derat'][row]
        u_drop_al = loads_df['u_drop_appl'][row]
        busduct = False

        if loads_df['equip'][row] in ('INCOMER', 'SECT_BREAKER'):
            rated_current = float(loads_df['rated_current_pe'][row])

            if 'MCC' in loads_df['load_tag'][row] and float(incom_margin) != 1.1:
                st.warning(f"Margin for incomer isn't equal to 10%, please adjust")
                st.stop()

            if 'LVS' in loads_df['load_tag'][row] and float(incom_margin) != 1.2:
                st.warning(f"Margin for incomer isn't equal to 20%, please adjust")
                st.stop()

            L = round5(rated_current * float(incom_margin))
            loads_df.loc[row, 'CB_AMPACITY'] = max_nearest(L)  # ном ток расцепителя
            cos_c = loads_df['power_factor_pe'][row]
            power = loads_df['peak_kw_pe'][row]
        else:
            rated_current = loads_df['rated_current'][row]
            L = round5(rated_current * 1.2)
            loads_df.loc[row, 'CB_AMPACITY'] = max_nearest(L)  # ном ток расцепителя
            cos_c = loads_df['power_factor'][row]
            power = loads_df['abs_power'][row] / loads_df['eff'][row]

        k_start = loads_df['start_ratio'][row]
        u_c = loads_df['rated_voltage'][row]
        len_c = loads_df['length'][row]

        if loads_df['equip'][row] == 'SECT_BREAKER':
            busduct = True

        cab_params = sect_calc(cab_df, row, u_c, power, rated_current, derat_factor, cos_c, k_start, len_c, min_sect,
                               u_drop_al, busduct, cos_start, sin_start, loads_df)
        loads_df.loc[row, 'parallel'] = cab_params[0]
        par = cab_params[0]
        loads_df.loc[row, 'section'] = cab_params[1]
        section = cab_params[1]

        if section == 0 or section == "0":
            print("Нулевое сечение для потребителя: ", loads_df.iloc[row, 0])

        loads_df.loc[row, 'pe_sect'] = cab_params[2]
        loads_df.loc[row, 'calc_drop'] = round(cab_params[3], 1)

        if par > 6 and loads_df.loc[row, 'equip'] != 'INCOMER':
            alarm_tag = str(loads_df.iloc[row, 0])
            st.warning(f'!!!У потребителя {alarm_tag} расчетное количество параллельных кабелей составило {par}. '
                       f'Все {par} кабелей внесены в кабельный журнал и отражены на SLD. '
                       f'При переходе на шинопровод удалите кабели потребителя {alarm_tag} из кабельного журнала '
                       f'и поправьте таговые номера и описание линии на SLD')

        S = str(round5(L * 1.5 * k_start)) + 'A/0.2s'
        I = str(round5(L * 2 * k_start))  # ПРОВЕРИТЬ!!!
        N = str(round5(L * 0.5))
        G = str(round5(loads_df['rated_current'][row] * 0.7))

        ''' "N" - подбирается исходя из длит. допустимого тока N-провода.
            "G" - А. В. Беляев Выбор аппаратуры, защит и кабелей в сетях 0,4 кВ, 2008 г., стр. 132.'''

        # ОКОНЧАНИЕ МОДУЛЯ ВЫБОРА КАБЕЛЯ

        if par > 1:
            par_cab = str(par) + "x"
        else:
            par_cab = " "
        if loads_df.pe_num[row] == 1 and section > 25:
            loads_df.loc[row, 'CONSUM-CABLE_TYPE'] = (
                    par_cab + loads_df['power_type'][row] + "-" + str(loads_df['ph_num'][row]) + "C+Ex" + str(section)
                    + '/' + str(loads_df['pe_sect'][row]) + "mm2, L=" + str(loads_df['length'][row]) + "m, dU="
                    + str(loads_df['calc_drop'][row]) + "%")
        else:
            loads_df.loc[row, 'CONSUM-CABLE_TYPE'] = (
                    str(par_cab) + str(loads_df['power_type'][row]) + "-" + str(loads_df['ph_num'][row]
                                                                                + loads_df['pe_num'][row]) + "x" + str(
                section) + "mm2, L=" + str(loads_df['length'][row])
                    + "m, dU=" + str(loads_df['calc_drop'][row]) + "%")

        if loads_df['load_tag'][row][-1] == 'M':
            load_tag_short = loads_df['load_tag'][row][:-1]
        else:
            load_tag_short = loads_df['load_tag'][row] + '-'

        # CB feeder***************************************************************************************************
        if loads_df['starter_type'][row] == "CB":
            loads_df.loc[row, 'CONSUM-CABLE_TAG'] = "L-" + loads_df['panel_tag'][row] + loads_df['bus'][row] + "-" + \
                                                    loads_df['load_tag'][row]
            if loads_df.equip[row] != 'INCOMER' and loads_df.equip[row] != 'SECT_BREAKER':
                loads_df.loc[row, 'CB_SET'] = 'L:' + str(
                    L) + 'A; \nS:' + S + '; \nI:' + I + 'A; \nN:' + N + 'A; \nG:' + G + 'A' if show_settings else 'LSING'
            if loads_df['equip'][row] == "INCOMER" or loads_df['equip'][row] == "SECT_BREAKER":

                if "LVS" in loads_df['load_tag'][row]:
                    loads_df.loc[row, 'CB_SET'] = 'L:' + str(
                        L) + 'A; \nS:' + S + '; \nI:' + I + 'A; \nN:' + N + 'A' if show_settings else 'LSIN'
                else:
                    loads_df.loc[row, 'CB_SET'] = 'L:' + str(
                        L) + 'A; \nS:' + S + '; \nI:' + I + 'A' if show_settings else 'LSI'

        if loads_df.CB_AMPACITY[row] < 630:
            loads_df.loc[row, 'SCHEME_TYPE'] = 'F1'
        else:
            loads_df.loc[row, 'SCHEME_TYPE'] = 'F2'

        # DOL feeder****************************************************************************************************
        if loads_df['starter_type'][row] == "DOL":
            loads_df.loc[row, 'CONSUM-CABLE_TAG'] = "L-" + str(loads_df['panel_tag'][row]) + str(
                loads_df['bus'][row]) + "-" + str(loads_df['load_tag'][row])

            loads_df.loc[row, 'HEATER-CABLE_TAG'] = "L-" + loads_df['panel_tag'][row] + loads_df['bus'][
                row] + "-" + load_tag_short + "SH"

            loads_df.loc[row, 'HEATER-CABLE_TYPE'] = loads_df['power_type'][row] + "-3x2.5mm2, L=" + str(
                loads_df['length'][row]) + 'm, dU=HOLD'

            loads_df = tags_for_control_cab(row, loads_df, load_tag_short)

            if loads_df.addBut[row] == 1:
                loads_df.loc[row, 'LCS2-CABLE_TAG'] = "C-" + load_tag_short + "LCS1" "-" + load_tag_short + "LCS2"
                loads_df.loc[row, 'LCS2-CABLE_TYPE'] = loads_df['control_type'][row] + '-3x1.5mm2, L=' + str(
                    contr_but_len) + 'm'
            else:
                loads_df.loc[row, 'starter_type'] = "DOL"

            loads_df.loc[row, 'CONT_AMPACITY'] = str(max_nearest(loads_df.CB_AMPACITY[row] * 1.1)) + 'A'
            loads_df.loc[row, 'CB_SET'] = 'I:' + I + 'A' if show_settings else 'I'
            loads_df.loc[row, 'SCHEME_TYPE'] = 'MH1'

        # VFD feeder ***************************************************************************************************
        if loads_df['starter_type'][row] == "VFD":
            loads_df.loc[row, 'VFD_TAG'] = load_tag_short[:7] + ' ' + load_tag_short[7:] + "VFD"
            loads_df.loc[row, 'CONSUM-CABLE_TAG'] = "L-" + str(loads_df['VFD_TAG'][row]) + "-" \
                                                    + str(loads_df['load_tag'][row])

            loads_df.loc[row, 'HEATER-CABLE_TAG'] = \
                "L-" + str(loads_df['panel_tag'][row]) + loads_df['bus'][row] + "-" + load_tag_short + "SH"
            loads_df.loc[row, 'HEATER-CABLE_TYPE'] = \
                str(loads_df['power_type'][row]) + "-3x2.5mm2, L=" + str(loads_df['length'][row]) + 'm'
            loads_df.loc[row, 'LCS1-CABLE_TAG'] = \
                "C-" + str(loads_df['panel_tag'][row]) + loads_df['bus'][row] + "-" + load_tag_short + "LCS1"

            loads_df = tags_for_control_cab(row, loads_df, load_tag_short)

            if loads_df.addBut[row] == 1:
                loads_df.loc[row, 'LCS2-CABLE_TAG'] = "C-" + load_tag_short + "LCS1" "-" + load_tag_short + "LCS2"
                loads_df.loc[row, 'LCS2-CABLE_TYPE'] = loads_df['control_type'][row] + '-3x1.5mm2, L=' + str(
                    contr_but_len) + 'm'
            else:
                loads_df.loc[row, 'starter_type'] = "VFD"  # "VFD_1but"
                loads_df.loc[row, 'VFD-CABLE_TAG'] = "L-" + str(loads_df['panel_tag'][row]) + str(
                    loads_df['bus'][row]) + "-" + load_tag_short + "VFD"

            loads_df.loc[row, 'VFD_AMPACITY'] = str(max_nearest(loads_df['rated_current'][row] * 1.2)) + 'A'
            loads_df.loc[row, 'CONT_AMPACITY'] = str(max_nearest(loads_df.CB_AMPACITY[row] * 1.1)) + 'A'
            loads_df.loc[row, 'CB_SET'] = 'L:' + str(L) + 'A; \nI:' + I + 'A' if show_settings else 'LI'
            if loads_df.rated_power[row] < 7.5:
                loads_df.loc[row, 'SCHEME_TYPE'] = 'F1-VFD'
            else:
                loads_df.loc[row, 'SCHEME_TYPE'] = 'F2-VFD'

        # SC RATING & POLARITY

        loads_df = sc_rating_polarity(max_sc, loads_df, row)


def add_gen_data(msp, loads_df, loads_df_new, point, max_sc, peak_sc):
    p_rat_a, p_rat_b, p_rat_em = bus_loads(loads_df)
    ins_block = msp.add_blockref('NORM_MODE_A', insert=(0, -4689))
    att_values = {
        'P_RATED_A': f"Prat.sec.A={p_rat_a} kW",
        'P_DEMAND_A': f"Pdem.sec.A={round(loads_df['rated_power'][0], 1)} kW",
        'I_CALC_A': f"Icalc.sec.A={round(loads_df['rated_current'][0], 1)} A",
        'COS_A': f"Cos f.sec.A={round(loads_df.power_factor[0], 2)}"
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('EMERG_MODE', insert=(0, -4689))
    att_values = {
        'P_RATED_EM': f"Prat.em.={p_rat_em} kW",
        'P_DEMAND_EM': f"Pdem.em.={round(loads_df.peak_kw_pe[0], 1)} kW",
        'I_CALC_EM': f"Icalc.em.={round(loads_df.rated_current_pe[0], 1)} A",
        'COS_EM': f"Cos f.em.={round(loads_df_new.power_factor_pe[0], 2)}"
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('EMERG_MODE', insert=(point - 230, -4689))
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('NORM_MODE_B', insert=(point, -4689))
    att_values = {
        'P_RATED_B': f"Prat.sec.B={p_rat_b} kW",
        'P_DEMAND_B': f"Pdem.sec.B={loads_df.rated_power[1]} kW",
        'I_CALC_B': f"Icalc.sec.B={loads_df.rated_current[1]} A",
        'COS_B': f"Cos f.sec.B={loads_df.power_factor[1]}"
    }
    ins_block.add_auto_attribs(att_values)

    ins_block = msp.add_blockref('BUS_DATA', insert=(0, -4689))
    att_values = {
        'BUS_DATA_RU': f'400/230В, TN-S, 50Гц, {loads_df.CB_RATING[0]}A, {max_sc}кА/1с, {peak_sc}кА',
        'BUS_DATA_EN': f'400/230В, TN-S, 50Гц, {loads_df.CB_RATING[0]}A, {max_sc}кА/1с, {peak_sc}кА'
    }
    ins_block.add_auto_attribs(att_values)


def scripts_tab():
    COS_START = 0.4
    SIN_START = math.sin(math.acos(COS_START))

    col_1, col_content, col_2 = st.columns([1, 9, 1])
    with col_1:
        st.empty()
    with col_2:
        st.empty()
    with col_content:

        center_style()

        if st.session_state.user['script_acc'] == 0:
            st.title(':red[	⚠️ Access Denied]')
            st.write('Request for Access by sergey.priemshiy@uzliti-en.com or telegram +998 90 959 80 30')
            st.stop()
        else:
            st.title(":orange[Let's speed up the Design 🏎️️]")
            st.write('Select the required Script')

        with st.expander("CREARE CABLE LIST | SLD FROM LOAD LIST | XML FOR ETAP"):
            st.title(':orange[Create Cable List | SLD from Load List | Creare XML for ETAP]')
            st.text("", help="Each action is available through corresponding tab")
            st.divider()
            st.write("Please find required templates in folder below  👇 You can update SLD template "
                     "according to your Project Requirements, but keep blocks attributes' names")
            st.code(r'\\uz-fs\Uzle\Work\Отдел ЭЛ\01 Малая Автоматизация\Шаблоны\CABLE_LIST_SLD')
            st.write("")

            loads_df = pd.DataFrame()

            p_l, p_c, p_r = st.columns(3, gap='medium')

            load_list = p_l.file_uploader("LOAD LIST", type='xlsx')

            cab_data = p_c.file_uploader("CABLE CATALOG", type='xlsx')

            dxf_template = p_r.file_uploader("SLD template", type='dxf')

            tab_cl, tab_sld, tab_xml = st.tabs(['Create Cable List', 'Create SLD in DXF', 'Greate XML for ETAP'])



            with tab_cl:

                with st.form("cab_list"):
                    lc, rc = st.columns(2, gap='medium')
                    panelDescr = lc.text_input("Panel Description ('Motor Control Center')", max_chars=20,
                                               help="Will be used to fill Cable List Column 'From'")
                    max_sc = lc.number_input('Initial Short Circuit Current at the Panel',
                                             value=65, min_value=6, max_value=150)
                    peak_sc = lc.number_input('Peak Short Circuit Current at the Panel',
                                              value=125, min_value=10, max_value=300)
                    contr_but_len = rc.number_input('Length of cable for Emergency PushButton',
                                                    value=25, min_value=10, max_value=300)

                    min_sect = rc.selectbox('Min. Cross_section of Power Cable wire', ['1.5', '2.5', '4'], index=1)

                    incom_margin = rc.selectbox("Margin for Incomer's Rated Current",
                                                ['1.0', '1.05', '1.1', '1.15', '1.2'],
                                                help="Usually 1.1 for Incomers and 1.2 for Feeders",
                                                index=2)

                    show_settings = lc.checkbox("Show CB settings at SLD", help="L, S, I, N, G")

                    make_cablist_but = rc.form_submit_button("Make Cable List", type='primary',
                                                             disabled=False if load_list and cab_data else True,

                                                             help="Cable List will be created, "
                                                                  "after you can download it",
                                                             use_container_width=True,
                                                             )

                if load_list and cab_data and make_cablist_but:
                    if len(panelDescr) < 2:
                        st.warning('Panel Description is too short')
                        st.stop()

                    cab_df = pd.read_excel(cab_data, sheet_name='cab_data')
                    diam_df = pd.read_excel(cab_data, sheet_name='PRYSMIAN')
                    glands_df = pd.read_excel(cab_data, sheet_name='GLANDS')
                    ex_df = pd.read_excel(cab_data, sheet_name='ExZones')

                    loads_df = pd.read_excel(load_list, sheet_name='loads')

                if len(loads_df):
                    loads_df = prepare_loads_df(loads_df)

                    check_loads(loads_df)

                    loads_df = incom_sect_cb_calc(loads_df)

                    making_cablist(loads_df, incom_margin, cab_df, show_settings, min_sect, contr_but_len,
                                   SIN_START, COS_START, max_sc)

                    loads_df = replace_zero(loads_df)

                    cl_df = create_cab_list(contr_but_len, loads_df, panelDescr, diam_df, ex_df, glands_df)

                    for tag in ['CONSUM-CABLE_TAG', 'HEATER-CABLE_TAG', 'LCS1-CABLE_TAG1', 'LCS1-CABLE_TAG2',
                                'LCS2-CABLE_TAG']:

                        loads_df[tag] = loads_df[tag].astype(str).str.replace('710-', '', regex=True)
                        loads_df[tag] = loads_df[tag].astype(str).str.replace('715-', '', regex=True)

                    st.session_state.loads_df = loads_df

                    st.subheader("Cable List is Ready", help='Only 7 rows in preview (for brief check)')
                    st.write(cl_df.head(7))

                    buffer = io.BytesIO()

                    with pd.ExcelWriter(buffer) as writer:
                        cl_df.to_excel(writer)

                    st.download_button(
                        label='Get Cable List here', data=buffer,
                        file_name=f'Cable List {datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")}.xlsx'
                    )

            with tab_sld:

                with st.form('create_sld'):
                    lc, cc, rc = st.columns(3, gap='medium')
                    order = lc.radio("Order of SLD creation", ('By Feeder Type', 'By Load List Order'), horizontal=True)

                    sld_file_name = cc.text_input('Enter the Name for resulting SLD (without extension)',
                                                  value="MCCxxx")
                    rc.text('')
                    rc.text('')

                    disable_sld_but = check_df(st.session_state.loads_df)

                    create_sld_but = rc.form_submit_button('Create SLD', type='primary',
                                                           disabled=False if dxf_template and
                                                                             disable_sld_but else True,
                                                           use_container_width=True)


                if create_sld_but:

                    lo_df = st.session_state.loads_df
                    dxf_temp_file = save_uploaded_file(dxf_template)
                    doc = open_dxf_file(f'temp_dxf/{dxf_temp_file}')

                    msp = doc.modelspace()

                    point = 0

                    lo_df_A = lo_df.loc[
                        (lo_df['bus'] != 'B') & (lo_df['equip'] != 'INCOMER') & (lo_df['equip'] != 'SECT_BREAKER')]
                    len_A = lo_df_A.shape[0]
                    lo_df_A.loc[:, 'CB_TAG'] = range(1, len_A + 1)
                    lo_df_A.loc[:, 'BUS_NUMBER'] = 'A'

                    lo_df_B = lo_df.loc[
                        (lo_df['bus'] == 'B') & (lo_df['equip'] != 'INCOMER') & (lo_df['equip'] != 'SECT_BREAKER')]

                    len_B = lo_df_B.shape[0]

                    if len_B > 0:
                        lo_df_B.loc[:, 'CB_TAG'] = range(1, len_B + 1)
                        lo_df_B.loc[:, 'BUS_NUMBER'] = 'B'

                    lo_df_inc1 = lo_df.loc[(lo_df['equip'] == 'INCOMER') & (lo_df['bus'] == 'A')]
                    lo_df_inc1.loc[:, 'CB_TAG'] = 1
                    lo_df_inc1.loc[:, 'starter_type'] = 'INCOMER'
                    lo_df_inc1.loc[:, 'BUS_NUMBER'] = 'A'

                    lo_df_inc2 = lo_df.loc[(lo_df['equip'] == 'INCOMER') & (lo_df['bus'] == 'B')]
                    lo_df_inc2.loc[:, 'CB_TAG'] = 1
                    lo_df_inc2.loc[:, 'starter_type'] = 'INCOMER'
                    lo_df_inc2.loc[:, 'BUS_NUMBER'] = 'B'

                    lo_df_sb = pd.DataFrame()

                    if lo_df.loc[(lo_df['equip'] == 'SECT_BREAKER')].shape[0] == 1:
                        lo_df_sb = lo_df.loc[(lo_df['equip'] == 'SECT_BREAKER')]
                        lo_df_sb.loc[:, 'CB_TAG'] = 1000
                        lo_df_sb.loc[:, 'BUS_NUMBER'] = 'A/B'
                        lo_df_sb.loc[:, 'starter_type'] = 'SECT_BREAKER'

                    if order == "By Feeder Type":
                        lo_df_A = lo_df_A.sort_values(by='starter_type', ascending=False)
                        lo_df_A.loc[:, 'CB_TAG'] = range(2, len_A + 2)

                        lo_df_B = lo_df_B.sort_values(by='starter_type', ascending=False)
                        lo_df_B.loc[:, 'CB_TAG'] = range(2, len_B + 2)

                    lo_df_new = pd.concat([lo_df_inc1, lo_df_A, lo_df_sb, lo_df_B, lo_df_inc2])

                    lo_df_new.loc[:, 'app_num'] = lo_df_new.CB_TAG.astype('str') + lo_df_new.BUS_NUMBER

                    for i in range(lo_df_new.shape[0]):
                        ins_block = msp.add_blockref(lo_df_new.starter_type[i], insert=(point, -5000))

                        if lo_df_new.CB_TAG[i] < 10:
                            feeder_num = '0' + str(lo_df_new.CB_TAG[i])
                        else:
                            feeder_num = str(lo_df_new.CB_TAG[i])

                        if lo_df_new.CB_TAG[i] == 1000:
                            feeder_num = ''

                        bus_num = lo_df_new.BUS_NUMBER[i]

                        att_values = {
                            'CB_RATING': str(lo_df_new.CB_RATING[i]) + 'A',
                            'CB_NUM': str(bus_num) + str(feeder_num),
                            'CB_AMPACITY': str(lo_df_new.CB_AMPACITY[i]) + 'A',
                            'CB_TRIP-UNIT': lo_df_new.CB_SET[i],
                            'CB_SC-RATING_POLARITY': lo_df_new.RAT_POL[i],
                            'CONSUM-CABLE_TAG': lo_df_new['CONSUM-CABLE_TAG'][i],
                            'CONSUM-CABLE_TYPE': lo_df_new['CONSUM-CABLE_TYPE'][i].replace('.0m', 'm').replace('.0/',
                                                                                                               '/'),
                            'CONSUMER_TAG': lo_df_new.index[i],
                            'CONSUMER_POWER': round(lo_df_new.rated_power[i], 1),
                            'CONSUMER_AMPACITY': round(lo_df_new.rated_current[i] * lo_df_new.eff[i], 1),
                            'CONSUMER_COS': round(lo_df_new.power_factor[i], 2),
                            'CONSUMER_EFFICIENCY': round(lo_df_new.eff[i], 2),
                            'CONSUMER_OPER-MODE': lo_df_new.load_duty[i],
                            'SCHEME_TYPE': lo_df_new.SCHEME_TYPE[i],
                            'CONT_NUM': 'C' + str(feeder_num) + str(bus_num),
                            'CONT_AMPACITY': lo_df_new.CONT_AMPACITY[i],
                            'VFD_AMPACITY': lo_df_new.VFD_AMPACITY[i],
                            'VFD_TAG': lo_df_new.VFD_TAG[i],
                            'HEATER-CABLE_TAG': lo_df_new['HEATER-CABLE_TAG'][i].replace('.0m', 'm'),
                            'HEATER-CABLE_TYPE': lo_df_new['HEATER-CABLE_TYPE'][i].replace('.0m', 'm').replace('.0/',
                                                                                                               '/'),
                            'LCS1-CABLE_TAG1': lo_df_new['LCS1-CABLE_TAG1'][i].replace('.0m', 'm'),
                            'LCS1-CABLE_TYPE1': lo_df_new['LCS1-CABLE_TYPE1'][i].replace('.0m', 'm'),
                            'LCS1-CABLE_TAG2': lo_df_new['LCS1-CABLE_TAG2'][i].replace('.0m', 'm'),
                            'LCS1-CABLE_TYPE2': lo_df_new['LCS1-CABLE_TYPE2'][i].replace('.m0', 'm'),
                            'LCS2-CABLE_TAG': lo_df_new['LCS2-CABLE_TAG'][i].replace('.0m', 'm'),
                            'LCS2-CABLE_TYPE': lo_df_new['LCS2-CABLE_TYPE'][i].replace('.0m', 'm'),
                            'CONSUMER_DESCR': lo_df_new['load_service'][i],
                            'MCU_TAG': 'MCU' + str(feeder_num) + str(bus_num)
                        }

                        ins_block.add_auto_attribs(att_values)

                        step = 73.25 if lo_df_new.starter_type[i] != 'CB' else 50.25

                        if lo_df_new.equip[i] == "INCOMER":
                            step = 52.215

                        if lo_df_new.equip[i] == "SECT_BREAKER":
                            step = 58.472

                        point += step

                    add_gen_data(msp, lo_df, lo_df_new, point, max_sc, peak_sc)
                    # msp, loads_df, loads_df_new, point, max_sc, peak_sc

                    saving_path = f"temp_dxf/{sld_file_name} by {st.session_state.user['login']}_" \
                                  f"{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')}.dxf"

                    doc.saveas(saving_path)

                    st.success('SLD is ready. Please Download')

                    with open(saving_path, 'rb') as f:
                        st.download_button('Get SLD here', data=f, file_name=saving_path)

                    reply2 = reg_action(saving_path.replace("temp_dxf/", ""))

                    if reply2['status'] == 200:
                        st.success(reply2['message'])
                    else:
                        st.warning(reply2['message'])

            with tab_xml:

                HOR_STEP = 4000


                disable_xml_but = not check_df(st.session_state.loads_df)

                xml_but = st.button("Create XML file", type='primary', disabled=disable_xml_but,
                                    use_container_width=True)

                if xml_but:
                    sld_df = st.session_state.loads_df

                    with open('xml_template.xml', 'r') as xml_file:
                        txt = xml_file.read()

                    SHIFT_FROM_EDGE = 5000
                    distr_bus_y = 10000
                    cb_y = 11000

                    start_id = 10000

                    sld_df = sld_df[(sld_df.equip != "INCOMER") & (sld_df.equip != "SECT_BREAKER")]

                    panel_list = sld_df.panel_tag.unique().tolist()

                    if len(panel_list) > 1:
                        st.warning("More than one panel in Load List. Now I can't generate XML for multiple panels")
                        st.stop()

                    bus_list = sld_df.bus.unique().tolist()

                    i = 1
                    for bus in bus_list:

                        bus_df = sld_df[sld_df.bus == bus]

                        if len(bus_df):
                            iid = start_id * i

                            distr_bus_len = (len(bus_df) + 1) * HOR_STEP

                            distr_bus_x = distr_bus_len / 2

                            cb_x = 3000 + SHIFT_FROM_EDGE

                            sect_tag = str(panel_list[0])+str(bus)

                            distr_bus_iid = f"ps{str(iid)}"

                            txt = add_main_bus(txt=txt, distr_bus_len=distr_bus_len,
                                               distr_bus_x=distr_bus_x + SHIFT_FROM_EDGE, distr_bus_y=distr_bus_y,
                                               distr_bus_id= sect_tag, distr_bus_iid=distr_bus_iid)

                            j = 1

                            for ind, row in bus_df.iterrows():
                                j += 1

                                cb_num = f"0{j}" if j < 10 else j

                                load_kw = row.rated_power
                                load_kva = load_kw / row.power_factor
                                load_kvar = math.sqrt(load_kva**2 - load_kw**2)

                                if "/" in str(row.section):
                                    st.experimental_show(row.section)
                                    parts = row.section.split("/")
                                    l_size = n_size = parts[0]
                                    pe_size = parts[1]
                                else:
                                    l_size = n_size = pe_size = row.section


                                txt = add_feeder(load_type=row.equip,
                                                 txt=txt,
                                                 cb_x=cb_x,
                                                 cb_y=cb_y,
                                                 cb_from_elem=sect_tag,
                                                 cb_id=f"{bus}{cb_num}",
                                                 cb_iid=f"ps{str(iid+j)}",
                                                 cb_to_elem=f"L-{ind}",
                                                 cab_id=f"L-{ind}",
                                                 cab_iid=f"ps{str(iid+j*100+1)}",
                                                 cab_len=row.length,
                                                 cab_to_bus=f"{ind}-bus",
                                                 load_bus_id=f"{ind}-bus",
                                                 load_bus_iid=f"ps{str(iid+j*100+2)}",
                                                 load_bus_tag=f"{ind}-bus",
                                                 motor_power=row.rated_power,
                                                 lrc=int(row.start_ratio) * 100,
                                                 cos_f=row.power_factor,
                                                 motor_id=ind,
                                                 motor_iid=f"ps{str(iid+j*100+3)}",
                                                 stat_load_id=ind,
                                                 stat_load_iid=f"ps{str(iid+j*100+4)}",
                                                 stat_load_kw=row.rated_power,
                                                 stat_load_kvar=load_kvar,
                                                 stat_load_kva=load_kva,
                                                 distr_bus_id=sect_tag,
                                                 distr_bus_iid=distr_bus_iid,
                                                 l_size=l_size,
                                                 n_size=n_size,
                                                 pe_size=pe_size
                                                 )

                                cb_x += HOR_STEP

                            i += 1
                            distr_bus_y = 20000
                            # cb_x = 11000
                            cb_y = 21000

                    saving_path = f"temp_dxf/XML by {st.session_state.user['login']}_" \
                                  f"{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')}.xml"

                    with open(saving_path, 'w') as ready_file:
                        ready_file.write(txt)

                    with open(saving_path, 'rb') as f:
                        st.download_button('Get XML file', data=f,file_name=saving_path.replace('temp_dxf/', ''))

        with st.expander('CREATE CABLEWAY SECTIONS'):
            st.title(':orange[Create Cableway Sections]')
            st.divider()
            st.write("Please find required templates in folder below  👇 ")
            st.code(r'\\uz-fs\Uzle\Work\Отдел ЭЛ\01 Малая Автоматизация\Шаблоны\CABLEWAYS')
            st.write("")

            p_l, p_c, p_r = st.columns(3, gap='medium')

            cable_list = p_l.file_uploader("CABLE LIST", type=['xlsx'])

            power_layout = p_c.file_uploader("CABLE ROUTING LAYOUT", type=['dxf'])

            sect_template = p_r.file_uploader("SECTIONS TEMPLATE", type=['dxf'])


            cab_tags, cab_layout, gen_sections = st.tabs(['Get Tags from Cable List', 'Process Cable Layout',
                                                          'Create Sections'])

            with cab_tags:

                if cable_list: # and st.session_state.user['access_level'] == 'dev'
                    with st.form('cablist_settings'):
                        lc, c1, c2, rc = st.columns(4, gap='medium')
                        sheet_name = lc.selectbox('Sheet Sheet', pd.read_excel(cable_list, sheet_name = None).keys())
                        from_unit = c1.text_input('From Unit')
                        to_unit = c2.text_input('To Unit')
                        rc.text('')
                        rc.text('')
                        all_chb = rc.checkbox('All Cable Tags')
                        get_cab_but = st.form_submit_button('Get Cable Tags for Routing', use_container_width=True)

                    if get_cab_but:
                        try:
                            st.session_state.cab_list_for_sect = pd.read_excel(cable_list, sheet_name=sheet_name)

                            get_tags_from_cablist(st.session_state.cab_list_for_sect, from_unit, to_unit, all_chb)

                        except Exception as e:

                            st.warning(err_handler(e))
                            st.stop()
                else:
                    st.write('Please Add a Cable List...')


            with cab_layout:
                if power_layout:
                    if st.button('Get Cables and Sections from Power Layout', use_container_width=True):
                        layout_path = f'temp_dxf/{save_uploaded_file(power_layout)}'
                        st.session_state.sect_df = get_sect_from_layout(st.session_state.cab_list_for_sect, layout_path)
                else:
                    st.write('Please Add Cable Routing Layout...')



            with gen_sections:

                if sect_template and check_df(st.session_state.sect_df):

                    with st.form('sect_settings'):
                        lc, rc = st.columns(2, gap='medium')
                        vertical_trays_gap = lc.slider("Vertical Gap between Trays, mm",
                                                       min_value=150, max_value=500, step=10, value=400)
                        trays_height = rc.radio('Tray Height, mm', [50, 60, 75, 80, 100, 150, 200],
                                                index=4, horizontal=True)

                        c1, c2, c3, c4 = st.columns(4, gap='medium')

                        volume_percent = c1.radio('Control Cable Tray filling (by Volume), %', [40, 50, 60],
                                                  index=1, horizontal=True)

                        width_percent = c2.radio('Power Cable Tray filling (by Width), %', [80, 90, 100],
                                                 index=0, horizontal=True)

                        lv_horis_gap = c3.radio('Horisontal Gap for LV cables, %', [0, 50, 100], index=2, horizontal=True)
                        mv_horis_gap = c4.radio('Horisontal Gap for MV cables, %', [0, 50, 100], index=2, horizontal=True)
                        form_conf_but = st.form_submit_button('Generate Sections', use_container_width=True)

                    if form_conf_but:

                        if vertical_trays_gap - trays_height < 100:
                            st.write(":red[Not enough vertical space to pull cables]")
                            st.write(":red[Please increase vertical gap or reduce tray height]")
                            st.stop()

                        st.session_state.p_x = 0

                        sections_template_path = f'temp_dxf/{save_uploaded_file(sect_template)}'

                        reply = generate_dxf(st.session_state.sect_df, vertical_trays_gap, trays_height,
                                             volume_percent, width_percent, lv_horis_gap, mv_horis_gap,
                                             sections_template_path)

                        with open(reply, 'rb') as f:
                            st.download_button('Get SECTIONS here', data=f,file_name=reply.replace("temp_dxf/", ""))

                        reply2 = reg_action(reply.replace("temp_dxf/", ""))

                        if reply2['status'] == 200:
                            st.success(reply2['message'])
                        else:
                            st.warning(reply2['message'])
                else:
                    st.write("Process Cable Layout and Add Sections' Template...")

        with st.expander('CREATE TERMINALS DIAGRAM'):
            st.title(':orange[Create Terminals Diagram - under development...]')
            st.write('Load List is required')
            st.write('Typical Diagrams is required')
            st.write('Settings form is required')
            st.write('Consider Options: typical Connection, manual creation...')


