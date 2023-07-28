# -*- coding: utf-8 -*-
import datetime
import io

import pandas as pd
import streamlit as st


def nearest(lst, target):
    return min(lst, key=lambda x: abs(x - target))


def distr_main():
    lc, rc = st.columns(2, gap='large')

    rc.text('')
    rc.text('')
    ratio = rc.slider("Select the ratio (adjust for better result)", min_value=0.1, max_value=1.0, value=0.2, step=0.05)
    # iterations = rc.slider("Iteration Quantity (adjust for better result)", min_value=3, max_value=50, value=5, step=1,)

    load_list = lc.file_uploader("LOAD LIST loader", type='xlsx', key='for_single_phases')

    st.divider()
    lc, rc = st.columns(2, gap='large')

    if not load_list:
        st.info("ADD LOAD LIST")
        st.stop()

    loads_df = pd.read_excel(load_list, sheet_name="Sheet1")

    iterations = len(loads_df) + 5

    lc.subheader('Initial Load List')
    lc.data_editor(loads_df, use_container_width=True)

    lc.write(f"#### {len(loads_df)} loads. Consumption: {round(loads_df.load.sum(),3)} kW")

    f_max = 0
    let_max = ''
    f_min_init = loads_df.load.sum()
    let_min = ''

    f_min = f_min_init
    # st.write(f"f_min:{f_min}")

    final_df = pd.DataFrame(columns=['consumer_name', 'load', 'phase'])

    while len(loads_df):

        for f in ("A", "B", "C"):
            if len(loads_df):
                ind_max = loads_df.load.idxmax()
                ind_min = loads_df.load.idxmin()

                loads_df.loc[ind_max, 'phase'] = f
                loads_df.loc[ind_min, 'phase'] = f

                load_name_max = (loads_df.loc[[ind_max], 'consumer_name'].to_numpy()[0])
                load_name_min = (loads_df.loc[[ind_min], 'consumer_name'].to_numpy()[0])

                if load_name_max == load_name_min:
                    final_df = pd.concat([final_df, loads_df.loc[[ind_max]]])
                else:
                    final_df = pd.concat([final_df, loads_df.loc[[ind_max]]])
                    final_df = pd.concat([final_df, loads_df.loc[[ind_min]]])

                loads_df = loads_df.drop([ind_max, ind_min])

    for iterat in range(1, iterations):

        f_max = 0
        f_min = f_min_init

        for f in ("A", "B", "C"):

            f_sum = final_df.loc[final_df.phase == f, 'load'].sum()

            if f_sum > f_max:
                f_max = f_sum
                let_max = f

            if f_sum < f_min:
                f_min = f_sum
                let_min = f

        half_delta = (f_max - f_min) / (2 * iterat * ratio)
        l = final_df.loc[final_df.phase == let_max, 'load'].tolist()
        nearest_value = nearest(l, half_delta)
        nearest_index = final_df[(final_df.load == nearest_value) & (final_df.phase == let_max)].index[0]
        final_df.loc[nearest_index, 'phase'] = let_min

    rc.subheader('Distributed Load List')
    rc.data_editor(final_df, use_container_width=True)

    rc.write(f"#### {len(final_df)} loads. Consumption: {round(final_df.load.sum(),3)} kW")
    st.divider()

    c1, c2,c3 = st.columns(3, gap='large')

    f_max = 0
    f_min = f_min_init

    for f in ("A", "B", "C"):
        f_sum = final_df.loc[final_df.phase == f, 'load'].sum()

        if f_sum > f_max:
            f_max = f_sum
            let_max = f

        if f_sum < f_min:
            f_min = f_sum
            let_min = f

        c1.write(f"Phase {f}: {round(f_sum, 3)} kW")

    c2.write(f"Max: Phase {let_max}: {round(f_max, 3)} kW")
    c2.write(f"Min: Phase {let_min}: {round(f_min, 3)} kW")

    c2.write(f"### Delta: {round(f_max - f_min, 3)} kW")

    final_df.set_index('consumer_name', inplace=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer) as writer:
        final_df.to_excel(writer)

    c3.text('')
    c3.text('')
    c3.text('')

    c3.download_button(
        label='Get Distributed Load List here', data=buffer,
        file_name=f'Distributed Loads {datetime.datetime.today().strftime("%Y-%m-%d-%H-%M")}.xlsx'
    )
