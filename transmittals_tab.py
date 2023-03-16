# -*- coding: utf-8 -*-

from time import sleep
import streamlit as st
import tkinter as tk
from tkinter import filedialog

def transmittals_content():
    tr_empty1, tr_content, tr_empty2 = st.columns([1,9,1])
    with tr_empty1:
        st.empty()
    with tr_empty2:
        st.empty()


    with tr_content:
        st.title(':orange[Transmittals]')

        placeholder = st.empty()
        sleep(1)
        # Replace the placeholder with some text:
        placeholder.text("Hello")
        sleep(1)
        # Replace the text with a chart:
        placeholder.line_chart({"data": [1, 5, 2, 6]})
        sleep(1)
        # Replace the chart with several elements:
        with placeholder.container():
            st.write("This is one element")
            st.write("This is another")
        sleep(1)
        # Clear all those elements:
        placeholder.empty()

# import libraries


# Set up tkinter
root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

# Folder picker button
st.title('Folder Picker')
st.write('Please select a folder:')
clicked = st.button('Folder Picker')
if clicked:
    dirname = st.text_input('Selected folder:', filedialog.askdirectory(master=root)) #master=root
