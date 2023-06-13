# -*- coding: utf-8 -*-

import streamlit as st
from utilities import center_style, left_style


# @st.cache_data(ttl=60 * 60 * 12)
# def fetch_emojis():
#     resp = requests.get(
#         'https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json')
#     json = resp.json()
#     codes, emojis = zip(*json.items())
#     return pd.DataFrame({
#         'Emojis': emojis,
#         'Shortcodes': [f':{code}:' for code in codes],
#     })
#
#
# def emoji_content():
#     empty1, content, empty2 = st.columns([1, 9, 1])
#     with empty1:
#         st.empty()
#     with empty2:
#         st.empty()
#     with content:
#         st.markdown('''
#         # Streamlit emoji shortcodes
#
#         Below are all the emoji shortcodes supported by Streamlit.
#
#         Shortcodes are a way to enter emojis using pure ASCII. So you can type this `:smile:` to show this
#         :smile:.
#
#         (Keep in mind you can also enter emojis directly as Unicode in your Python strings too — you don't
#         *have to* use a shortcode)
#         ''')
#
#         emojis = fetch_emojis()
#         st.table(emojis)


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

        ru, en = st.columns(2, gap='medium')

        ru.subheader("Вкладка 'Home'")
        ru.write("")

        ru.markdown('<div style="text-align: justify;">'
                    'На вкладке <b>Home</b> отображаются новые <b>Задания</b> от смежных отделов '
                    '(если их внесли в базу не Вы) и <b>Трансмитталы</b>. Чтобы скрыть Задания и '
                    'Трансмитталы, нажмите кнопку под соответствующим блоком.'
                    '</div>', unsafe_allow_html=True)
        ru.divider()

        en.subheader("Вкладка 'Home'")
        en.markdown('<div style="text-align: justify;">'
                    'На вкладке <b>Home</b> отображаются новые <b>Задания</b> от смежных отделов '
                    '(если их внесли в базу не Вы) и <b>Трансмитталы</b>. Чтобы скрыть Задания и '
                    'Трансмитталы, нажмите кнопку под соответствующим блоком.'
                    '</div>', unsafe_allow_html=True)
        en.divider()

