# -*- coding: utf-8 -*-
import datetime
import io
import ezdxf
import streamlit as st
import pandas as pd
import numpy as np
import math


from users import err_handler

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


def p_green(text):  # Everything is OK
    st.write("\033[32m{}".format(text))


def p_red(text):  # attention
    st.write("\033[31m{}".format(text))


def p_white(text):  # information, request
    st.write("\033[37m{}".format(text))


def incom_sect_cb_calc(loads_df: pd.DataFrame) -> pd.DataFrame:
    # st.info('Loads DF')
    # st.write(loads_df)
    # st.stop()
    # try:
    #     if len(loads_df.loc[loads_df.abs_power == 0]) > 0:
    #         st.write(loads_df.loc[loads_df.abs_power == 0])
    #         st.warning("abs_power")
    #         st.stop()
    # except Exception as e:
    #     st.write(err_handler(e))
    #     st.stop()

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
    global p_rat_a, p_rat_b, p_rat_em
    p_rat_a = round(loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER') & (
            loads_df.bus == 'A'), 'rated_power'].sum(), 1)
    p_rat_b = round(loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != 'SECT_BREAKER') & (
            loads_df.bus == 'B'), 'rated_power'].sum(), 1)
    p_rat_em = round(
        loads_df.loc[(loads_df.equip != 'INCOMER') & (loads_df.equip != "SECT_BREAKER"), 'rated_power'].sum(), 1)

    if (loads_df.loc[(loads_df.bus == 'B') & (loads_df.equip != 'INCOMER')]).shape[0] == 0:
        print("ATTENTION: We are working with singe-bus panel!")
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_power'] = rated_power_kw_a
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'power_factor'] = power_factor_a
        loads_df.loc[(loads_df.equip == 'INCOMER') & (loads_df.bus == 'B'), 'rated_current'] = round(
            rated_power_kw_a / 1.732 / 0.4 / power_factor_a, 1)
        # loads_df['peak_kw_pe'][row]

        p_rat_b = p_rat_a
        p_rat_em = p_rat_a

        loads_df = loads_df.loc[loads_df.equip != "SECT_BREAKER"].reset_index(drop=True)
    return loads_df


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


# loads_path = input('Введите полный путь к файлу, с названием файла и расширением: ')

def check_loads(loads_df):
    checkLoads_df = loads_df.iloc[:, 0:27]

    if (checkLoads_df.isnull().sum()).sum() > 0:
        p_red(f'В Load List {(checkLoads_df.isnull().sum()).sum()} не заполненных обязательных полей')
        p_red('Подгрузите корректно заполненный Load List')
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.eff.min() == 0:
        p_red("Nulls in 'efficiency' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.power_factor.min() == 0:
        p_red("Nulls in 'power factor' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.abs_power[3:].min() == 0:
        p_red("Nulls in 'abs_power' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.rated_power[3:].min() == 0:
        p_red("Nulls in 'rated_power' column")
        st.write('Script aborted')
        st.stop()

    if checkLoads_df.usage_factor[3:].min() == 0:
        p_red("Nulls in 'usage_factor' column")
        st.write('Script aborted')
        st.stop()

    st.text('')
    st.success('Loads Data are Walid')


def prepare_loads_df(loads_df):
    loads_df['length'] = round(loads_df['length'] / 5, 0) * 5

    loads_df['VFD_AMPACITY'] = '-'
    loads_df['VFD_TAG'] = '-'

    loads_df[
        ['CONT_AMPACITY', 'HEATER-CABLE_TAG', 'HEATER-CABLE_TYPE', 'LCS1-CABLE_TAG1', 'LCS1-CABLE_TYPE1',
         'LCS1-CABLE_TAG2',
         'LCS1-CABLE_TYPE2', 'LCS2-CABLE_TAG', 'LCS2-CABLE_TYPE']] = '-'

    loads_df[['c_kw', 'i_kw', 's_kw', 'c_kvar', 'i_kvar', 's_kvar', 'peak_kw_pe', 'peak_kvar_pe', 'power_factor_pe',
              'rated_current_pe']] = 0

    return loads_df

    #  NORMAL MODE


def sect_calc(cab_df, row: int, u_c: int, power: float, rated_current: float, derat_factor: float,
              cos_c: float, k_start: float, len_c: float, min_sect: object, u_drop_al: float, busduct: bool,
              cos_start: float, sin_start: float, loads_df) -> tuple:
    # sect_calc(cab_df, row, u_c, power, rated_current, derat_factor, cos_c, k_start, len_c, min_sect,
    #                                u_drop_al, busduct, cos_start, sin_start, loads_df)
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

            # cab_df['rat_current'][cab] * derat_factor * par

            cur_check = current_c >= cab_current  # load more than applicable curent of cable
            checker = not (not cur_check and not volt_check and not volt_start_check)
            # p_green(('cur_check',cur_check,'volt_check',volt_check,'volt_start_check',volt_start_check))
            # p_red((par,'-',checker))

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
            print('Ошибка определения диаметра кабеля: ', cl_df.cableTag[y])
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
    # cl_df.to_excel(loads_path[:-8] + '-cabList.xlsx')

    # p_green(f'''КАБЕЛЬНЫЙ ЖУРНАЛ В ФОРМАТЕ .xlsx ГОТОВ
    # Открывать по ссылке:
    # {loads_path[:-8] + '-cabList.xlsx'}''')


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
            p_red('!!!')
            p_red(f'У потребителя {alarm_tag} расчетное количество параллельных кабелей составило {par}.')
            p_red(f'Все {par} кабелей внесены в кабельный журнал и отражены на SLD.')
            p_red(f'При переходе на шинопровод удалите кабели потребителя {alarm_tag} ')
            p_red('из кабельного журнала и поправьте таговые номера и описание линии на SLD')
            p_red('!!!')
            print('\033[0m')

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


def xl_to_sld():
    dxf_template = None
    COS_START = 0.4
    # K_START = 1
    SIN_START = math.sin(math.acos(COS_START))

    col_1, col_content, col_2 = st.columns([1, 9, 1])
    with col_1:
        st.empty()
    with col_2:
        st.empty()
    with col_content:

        st.markdown("""
            <style>
                div[data-testid="column"]:nth-of-type(1)
                {
                    text-align: center;
                } 

                div[data-testid="column"]:nth-of-type(2)
                {
                    text-align: center;
                } 

                div[data-testid="column"]:nth-of-type(3)
                {
                    text-align: center;
                } 
            </style>
            """, unsafe_allow_html=True)

        st.title(':orange[Create SLD from Load List] - under Development')
        st.divider()

        u_df = st.session_state.adb['users']

        user_script_acc = u_df.loc[u_df.login == st.session_state.user, 'script_acc'].to_numpy()[0]

        if user_script_acc:

            loads_df = pd.DataFrame()

            p_l, p_c, p_r = st.columns(3, gap='medium')

            load_list = p_l.file_uploader("Upload LOAD LIST in xlsx or xlsb", type=['xlsx', 'xlsb'],
                                          accept_multiple_files=False, key=None,
                                          help=None, on_change=None, args=None,
                                          kwargs=None, disabled=False, label_visibility="visible")

            cab_data = p_c.file_uploader("Upload CABLE CATALOG in xlsx or xlsb", type=['xlsx', 'xlsb'],
                                         accept_multiple_files=False, key=None,
                                         help=None, on_change=None, args=None,
                                         kwargs=None, disabled=False, label_visibility="visible")

            dxf_template = p_r.file_uploader("Upload SLD template in dxf (v.18.0)", type=['dxf'],
                                             accept_multiple_files=False, key=None,
                                             help=None, on_change=None, args=None,
                                             kwargs=None, disabled=False, label_visibility="visible")

            tab_cl, tab_sld = st.tabs(['Create Cable List', 'Create SLD'])

            with tab_cl:

                with st.form("cab_list"):
                    lc, rc = st.columns(2, gap='medium')
                    panelDescr = lc.text_input("Panel Description ('Motor Control Center')", max_chars=20)
                    max_sc = lc.number_input('Initial Short Circuit Current at the Panel',
                                             value=65, min_value=6, max_value=150)
                    peak_sc = lc.number_input('Peak Short Circuit Current at the Panel',
                                              value=125, min_value=10, max_value=300)
                    contr_but_len = rc.number_input('Length of cable for Emergency PushButton',
                                                    value=25, min_value=10, max_value=300)

                    min_sect = rc.selectbox('Min. Cross_section of Power Cable wire', ['1.5', '2.5', '4'], index=1)
                    incom_margin = rc.selectbox("Margin for Incomer's Rated Current", ['1.0', '1.05', '1.1', '1.15', '1.2'],
                                                index=1)

                    show_settings = lc.checkbox("Show CB settings at SLD")

                    make_cablist_but = rc.form_submit_button("Make Cable List", use_container_width=True)

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

                    st.subheader("Cable List is Ready")
                    st.write(cl_df.head(7))

                    buffer = io.BytesIO()

                    with pd.ExcelWriter(buffer) as writer:
                        cl_df.to_excel(writer)

                    st.download_button('Get Cable List here', data=buffer,
                                       file_name=f'Cable List {datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")}.xlsx',
                                       mime=None, key=None, help=None, on_click=None, args=None, kwargs=None,
                                       disabled=False, use_container_width=False)

            with tab_sld:
                with st.form('create_sld'):
                    lc, rc = st.columns(2, gap='medium')
                    order = lc.radio("Order od SLD creation", ('ПО ТИПУ ФИДЕРОВ', 'ПО LOAD LIST'), horizontal=True)
                    rc.text('')
                    create_sld_but = rc.form_submit_button('Create SLD', use_container_width=True)

                if dxf_template is not None:
                    # st.write(dir(dxf_template))
                    try:
                        # with open(dxf_template, 'r') as f:
                        text_data = dxf_template.read()
                        dxf_in_ram = io.BytesIO(text_data)
                        st.write(type(dxf_in_ram.readlines()))
                        st.divider()
                        st.write(type(dxf_in_ram))
                        st.divider()
                        st.write(dxf_template.getbuffer())
                    except Exception as e:
                        st.warning(err_handler(e))

                    # try:
                    #     doc = ezdxf.readfile(dxf_template.getbuffer())
                    # except IOError as e:
                    #     st.warning(f"Not a DXF file or a generic I/O error.")
                    #     st.write(err_handler(e))
                    #     st.stop()
                    #
                    # except ezdxf.DXFStructureError as (e):
                    #     st.warning(f"Invalid or corrupted DXF file.")
                    #     st.write(err_handler(e))
                    #     st.stop()

                    # st.write(doc)
                # #
                #     msp = doc.modelspace()
                #     point = 0
                #
                #     # .astype(str).str.replace('710-', '', regex=True)
                #
                #     loads_df['CONSUM-CABLE_TAG'] = loads_df['CONSUM-CABLE_TAG'].astype(str).str.replace('710-', '',
                #                                                                                         regex=True)
                #     loads_df['CONSUM-CABLE_TAG'] = loads_df['CONSUM-CABLE_TAG'].astype(str).str.replace('715-', '',
                #                                                                                         regex=True)
                #     loads_df['HEATER-CABLE_TAG'] = loads_df['HEATER-CABLE_TAG'].astype(str).str.replace('710-', '',
                #                                                                                         regex=True)
                #     loads_df['HEATER-CABLE_TAG'] = loads_df['HEATER-CABLE_TAG'].astype(str).str.replace('715-', '',
                #                                                                                         regex=True)
                #     loads_df['LCS1-CABLE_TAG1'] = loads_df['LCS1-CABLE_TAG1'].astype(str).str.replace('710-', '',
                #                                                                                       regex=True)
                #     loads_df['LCS1-CABLE_TAG1'] = loads_df['LCS1-CABLE_TAG1'].astype(str).str.replace('715-', '',
                #                                                                                       regex=True)
                #     loads_df['LCS1-CABLE_TAG2'] = loads_df['LCS1-CABLE_TAG2'].astype(str).str.replace('710-', '',
                #                                                                                       regex=True)
                #     loads_df['LCS1-CABLE_TAG2'] = loads_df['LCS1-CABLE_TAG2'].astype(str).str.replace('715-', '',
                #                                                                                       regex=True)
                #     loads_df['LCS2-CABLE_TAG'] = loads_df['LCS2-CABLE_TAG'].astype(str).str.replace('710-', '', regex=True)
                #     loads_df['LCS2-CABLE_TAG'] = loads_df['LCS2-CABLE_TAG'].astype(str).str.replace('715-', '', regex=True)
                #
                #     loads_df_A = loads_df.loc[
                #         (loads_df['bus'] != 'B') & (loads_df['equip'] != 'INCOMER') & (loads_df['equip'] != 'SECT_BREAKER')]
                #     len_A = loads_df_A.shape[0]
                #     loads_df_A.loc[:, 'CB_TAG'] = range(1, len_A + 1)
                #     loads_df_A.loc[:, 'BUS_NUMBER'] = 'A'
                #     # loads_df_A.loc[:, 'CB_TAG'] = str(loads_df_A.CB_TAG) + 'A'
                #
                #     loads_df_B = loads_df.loc[
                #         (loads_df['bus'] == 'B') & (loads_df['equip'] != 'INCOMER') & (loads_df['equip'] != 'SECT_BREAKER')]
                #     # loads_df_B.loc[:, 'CB_TAG'] = str(loads_df_B.CB_TAG) + 'B'
                #
                #     len_B = loads_df_B.shape[0]
                #     if len_B > 0:
                #         loads_df_B.loc[:, 'CB_TAG'] = range(1, len_B + 1)
                #         loads_df_B.loc[:, 'BUS_NUMBER'] = 'B'
                #
                #     loads_df_inc1 = loads_df.loc[(loads_df['equip'] == 'INCOMER') & (loads_df['bus'] == 'A')]
                #     loads_df_inc1.loc[:, 'CB_TAG'] = 1
                #     loads_df_inc1.loc[:, 'starter_type'] = 'INCOMER'
                #     loads_df_inc1.loc[:, 'BUS_NUMBER'] = 'A'
                #
                #     loads_df_inc2 = loads_df.loc[(loads_df['equip'] == 'INCOMER') & (loads_df['bus'] == 'B')]
                #     loads_df_inc2.loc[:, 'CB_TAG'] = 1
                #     loads_df_inc2.loc[:, 'starter_type'] = 'INCOMER'
                #     loads_df_inc2.loc[:, 'BUS_NUMBER'] = 'B'
                #
                #     loads_df_sb = pd.DataFrame()
                #
                #     if loads_df.loc[(loads_df['equip'] == 'SECT_BREAKER')].shape[0] == 1:
                #         loads_df_sb = loads_df.loc[(loads_df['equip'] == 'SECT_BREAKER')]
                #         loads_df_sb.loc[:, 'CB_TAG'] = 1000
                #         loads_df_sb.loc[:, 'BUS_NUMBER'] = 'A/B'
                #         loads_df_sb.loc[:, 'starter_type'] = 'SECT_BREAKER'
                #
                #     if order == "ПО ТИПУ ФИДЕРОВ":
                #         loads_df_A = loads_df_A.sort_values(by='starter_type', ascending=False)
                #         loads_df_A.loc[:, 'CB_TAG'] = range(2, len_A + 2)
                #
                #         loads_df_B = loads_df_B.sort_values(by='starter_type', ascending=False)
                #         loads_df_B.loc[:, 'CB_TAG'] = range(2, len_B + 2)
                #
                #     loads_df_new = pd.concat([loads_df_inc1, loads_df_A, loads_df_sb, loads_df_B, loads_df_inc2])
                #
                #     loads_df_new.loc[:, 'app_num'] = loads_df_new.CB_TAG.astype('str') + loads_df_new.BUS_NUMBER
                #
                #     for i in range(loads_df_new.shape[0]):
                #         ins_block = msp.add_blockref(loads_df_new.starter_type[i], insert=(point, -5000))
                #
                #         if loads_df_new.CB_TAG[i] < 10:
                #             feeder_num = '0' + str(loads_df_new.CB_TAG[i])
                #         else:
                #             feeder_num = str(loads_df_new.CB_TAG[i])
                #
                #         if loads_df_new.CB_TAG[i] == 1000:
                #             feeder_num = ''
                #
                #         bus_num = loads_df_new.BUS_NUMBER[i]
                #
                #         att_values = {
                #             'CB_RATING': str(loads_df_new.CB_RATING[i]) + 'A',
                #             'CB_NUM': str(bus_num) + str(feeder_num),
                #             'CB_AMPACITY': str(loads_df_new.CB_AMPACITY[i]) + 'A',
                #             'CB_TRIP-UNIT': loads_df_new.CB_SET[i],
                #             'CB_SC-RATING_POLARITY': loads_df_new.RAT_POL[i],
                #             'CONSUM-CABLE_TAG': loads_df_new['CONSUM-CABLE_TAG'][i],
                #             'CONSUM-CABLE_TYPE': loads_df_new['CONSUM-CABLE_TYPE'][i].replace('.0m', 'm').replace('.0/',
                #                                                                                                   '/'),
                #             'CONSUMER_TAG': loads_df_new.index[i],
                #             'CONSUMER_POWER': round(loads_df_new.rated_power[i], 1),
                #             'CONSUMER_AMPACITY': round(loads_df_new.rated_current[i] * loads_df_new.eff[i], 1),
                #             'CONSUMER_COS': round(loads_df_new.power_factor[i], 2),
                #             'CONSUMER_EFFICIENCY': round(loads_df_new.eff[i], 2),
                #             'CONSUMER_OPER-MODE': loads_df_new.load_duty[i],
                #             'SCHEME_TYPE': loads_df_new.SCHEME_TYPE[i],
                #             'CONT_NUM': 'C' + str(feeder_num) + str(bus_num),
                #             'CONT_AMPACITY': loads_df_new.CONT_AMPACITY[i],
                #             'VFD_AMPACITY': loads_df_new.VFD_AMPACITY[i],
                #             'VFD_TAG': loads_df_new.VFD_TAG[i],
                #             'HEATER-CABLE_TAG': loads_df_new['HEATER-CABLE_TAG'][i].replace('.0m', 'm'),
                #             'HEATER-CABLE_TYPE': loads_df_new['HEATER-CABLE_TYPE'][i].replace('.0m', 'm').replace('.0/',
                #                                                                                                   '/'),
                #             'LCS1-CABLE_TAG1': loads_df_new['LCS1-CABLE_TAG1'][i].replace('.0m', 'm'),
                #             'LCS1-CABLE_TYPE1': loads_df_new['LCS1-CABLE_TYPE1'][i].replace('.0m', 'm'),
                #             'LCS1-CABLE_TAG2': loads_df_new['LCS1-CABLE_TAG2'][i].replace('.0m', 'm'),
                #             'LCS1-CABLE_TYPE2': loads_df_new['LCS1-CABLE_TYPE2'][i].replace('.m0', 'm'),
                #             'LCS2-CABLE_TAG': loads_df_new['LCS2-CABLE_TAG'][i].replace('.0m', 'm'),
                #             'LCS2-CABLE_TYPE': loads_df_new['LCS2-CABLE_TYPE'][i].replace('.0m', 'm'),
                #             # 'LCS3-CABLE_TAG':  loads_df_new['LCS3-CABLE_TAG'][i],
                #             # 'LCS3-CABLE_TYPE':  loads_df_new['LCS3-CABLE_TYPE'][i],
                #             'CONSUMER_DESCR': loads_df_new['load_service'][i],
                #             # msp.add_mtext(loads_df_new['load_service'][i], dxfattribs={"style": "OpenSans"})
                #             'MCU_TAG': 'MCU' + str(feeder_num) + str(bus_num)
                #         }
                #
                #         ins_block.add_auto_attribs(att_values)
                #
                #         step = 73.25 if loads_df_new.starter_type[i] != 'CB' else 50.25
                #         step = 73.25 if loads_df_new.starter_type[i] != 'CB' else 50.25
                #
                #         if loads_df_new.equip[i] == "INCOMER":
                #             step = 52.215
                #
                #         if loads_df_new.equip[i] == "SECT_BREAKER":
                #             step = 58.472
                #
                #         point += step
                #
                #
                #     add_gen_data(msp, loads_df, loads_df_new, point)
                #
                #     dxf_file = doc.saveas('SLD.dxf')
                #
                #     report = ("ОДНОЛИНЕЙКА В ФОРМАТЕ .dxf ГОТОВА. Качайте файл SLD.dxf")
                #
                #     st.success(report)
                #
                #
                #     buffer_2 = io.BytesIO()
                #
                #     buffer_2.write(dxf_file)
                #
                #     st.download_button('Get SLD', data=buffer_2,
                #                        file_name=f'SLD {datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")}.xlsx',
                #                        mime=None, key=None, help=None, on_click=None, args=None, kwargs=None,
                #                        disabled=False, use_container_width=False)

                    # if dxf_template:
                    #     st.download_button('Get SLD here', data=dxf_template, file_name='SLD.dxf', mime=None, key=None,
                    #                        help=None,
                    #                        on_click=None, args=None, kwargs=None, disabled=False, use_container_width=False)


