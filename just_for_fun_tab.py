# -*- coding: utf-8 -*-

import streamlit as st
from utilities import center_style


def manual():

    center_style()

    fun_1, fun_content, fun_2 = st.columns([1, 9, 1])
    fun_1.empty()
    fun_2.empty()
    with fun_content:
        st.title(':orange[Manual] - under Development')
        st.divider()
        # st.write("🌴 Short time to relax")
        #
        # st.write("check out this [Мальтийский механизм](https://www.wikiwand.com/ru/"
        #          "%D0%9C%D0%B0%D0%BB%D1%8C%D1%82%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9"
        #          "_%D0%BC%D0%B5%D1%85%D0%B0%D0%BD%D0%B8%D0%B7%D0%BC)")
        #
        # st.write("check out this [Сверление квадратных отверстий](https://etudes.ru/etudes/drilling-square-holes/)")

        ru, en = st.columns(2, gap='large')

        ru.subheader("Вкладка 'Home'")
        ru.write("")

        ru.markdown('<div style="text-align: justify;">'
                    'На cтранице <b>Home</b> отображаются новые <b>Задания</b> от смежных отделов '
                    '(если их внесли в базу не Вы) и <b>Трансмитталы</b>. Чтобы скрыть Задания и '
                    'Трансмитталы, нажмите кнопку под соответствующим блоком.'
                    '</div>', unsafe_allow_html=True)
        ru.divider()

        en.subheader("Вкладка 'Home'")
        en.write("")
        en.markdown('<div style="text-align: justify;">'
                    'At the page <b>Home</b> are showing <b>Task</b> from other Departments '
                    '(if they were added to DataBase not by You) & <b>Transmittals</b>. To hide Tasks & '
                    'Transmittals, click the button under the corresponding block.'
                    '</div>', unsafe_allow_html=True)
        en.divider()
