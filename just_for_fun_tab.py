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

        ru, en = st.columns(2, gap='large')

        lang = None

        if ru.button("RU", use_container_width= True):
            lang = "RU"

        if en.button("EN", use_container_width= True):
            lang = "EN"

        if lang is None:
            st.subheader("Select the language * Выберите язык")

        def help_ru_en(page, div_ru, div_en):
                if lang == "RU":
                    # ru, en = st.columns(2, gap='large')
                    st.subheader(f":orange[Страница '{page}']")
                    st.write("")
                    st.markdown(div_ru, unsafe_allow_html=True)
                    st.divider()

                if lang == "EN":
                    st.subheader(f":orange[Page '{page}']")
                    st.write("")
                    st.markdown(div_en, unsafe_allow_html=True)
                    st.divider()

        div_ru = '<div style="text-align: justify;">' \
                 'На cтранице <b>Home</b> отображаются новые <b>Задания</b> от смежных отделов ' \
                 '(если их внесли в базу не Вы) и <b>Трансмитталы</b>. Чтобы скрыть Задания и ' \
                 'Трансмитталы, нажмите кнопку под соответствующим блоком.' \
                 '</div>'

        div_en = '<div style="text-align: justify;">' \
                 'At the page <b>Home</b> are showing <b>Task</b> from other Departments ' \
                 '(if they were added to DataBase not by You) & <b>Transmittals</b>. To hide Tasks & ' \
                 'Transmittals, click the button under the corresponding block.' \
                 '</div>'
        help_ru_en("Home", div_ru, div_en)

        div_ru = '<div style="text-align: justify;">Страница <b>Drawings</b> предназначена для просмотра и обновления' \
                 ' статусов <b>Комплекта чертежей</b>, переназначения исполнителей, ревизий чертежей, примечаний и' \
                 ' трансмитталов' \
                 '</div>'

        div_en = '<div style="text-align: justify;">' \
                 'Page <b>Drawings</b> is intended for review and update of <b>Unit\'s</b> status, ' \
                 'reassignment of performer, drawings revisions, notes and transmittals' \
                 '</div>'
        help_ru_en("Drawings", div_ru, div_en)

        div_ru = '<div style="text-align: justify;">' \
                 'На странице <b>Transmittals</b> можно добавлять, просматривать или редактировать ' \
                 '<b>Трансмитталы</b>, (входящие и исходящие)' \
                 '</div>'

        div_en = '<div style="text-align: justify;">' \
                 'On the <b>Transmittals</b> page you can add, view or edit ' \
                 '<b>Transmittals</b>, (incoming and outgoing)' \
                 '</div>'
        help_ru_en("Transmittals", div_ru, div_en)
