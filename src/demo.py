import sys
sys.path.append('../src')


import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import folium
from tqdm import tqdm
from st_click_detector import click_detector
from PIL import Image
import io
import pickle
from folium.plugins import Draw
from folium.utilities import JsCode
import requests
import tempfile
from skimage import io
import clipboard
import utils

st.set_page_config(layout='wide')

if not 'clipboard_history' in st.session_state.keys():
    st.session_state['clipboard_history'] = []

if not 'first_run' in st.session_state.keys():
    clipboard.copy('dummy')
    st.session_state['first_run'] = 'done'

st.header('StreetView Analytics with Gemini', divider='gray')
st.markdown('**Instructions**: Select a use case or navigate anywhere, click on the map and write a prompt. Send to Gemini.')

paste = clipboard.paste()
new_coords = False
if paste.startswith('COORDS'):
    new_coords = True
    st.session_state['clipboard_history'].append(paste)

marker_data = utils.add_marker(st.session_state)
print (marker_data)
m = folium.Map(zoom_start = marker_data['zoom'])
folium.plugins.MousePosition().add_to(m)
folium.plugins.Geocoder(add_marker=False).add_to(m)

m.add_child(folium.ClickForLatLng('"COORDS " + lat + "," + lng', alert=False))

col1, col2 = st.columns([.6,.4])

with col1:

    the_map = st_folium(m, 
                        center=marker_data['location'], 
                        zoom=marker_data['zoom'],
                        width=1300,
                        height=500, 
                        feature_group_to_add=marker_data['fg'])


    c21,c22 = st.columns(2)
    with c21:
        sv_imgsize = st.selectbox(
            "Streetview image size to download",
            ("300x300", "500x500", "1000x1000"),
            index=1,
        )   
    with c22:
        sv_zoom = st.selectbox(
            "Streetview zoom level to download",
            (1,3,6,10,20),
            index=2,
        )   

    if marker_data['location'] is not None:

        lat, lon = marker_data['location']
        st.markdown (f'Downloaded streetView 360 imagery at lat: {lat:.5f}, lon: {lon:.5f}')
        headings = [0,90,180,270]
        svimg = {}

        for heading in headings:
            svimg[heading] = utils.pull_streetview_image(lon, lat, heading=heading, zoom=sv_zoom, size=sv_imgsize)

        svimg = np.vstack([np.transpose(z, (1,0,2)) for z in svimg.values()])
        svimg = np.transpose(svimg, (1,0,2))
        st.image(svimg)


with col2:
    st.header('Use cases', divider='gray')
    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button('madrid [construction]'):
            clipboard.copy('COORDS 40.41912,-3.70617')
            st.session_state['prompt_text'] = 'Are there construction works in this image. If so, describe their nature.'
            st.rerun()

    with c2:
        if st.button('medellin [informal business]'):
            clipboard.copy('COORDS 6.24949,-75.57015')
            st.session_state['prompt_text'] = '''
Are there informal business in this image. If so, indicate precisely where and include bounding box detections in json            
            '''
            st.rerun()

    with c3:
        if st.button('new york [people and signs]'):
            clipboard.copy('COORDS 40.71494,-73.99840')
            st.session_state['prompt_text'] = '''
    count the number of people and vehicles in this mage.
    also, read all the sings and text that you see
            '''
            st.rerun()


    st.header('Gemini')
    if 'prompt_text' in st.session_state:
        text = st.session_state['prompt_text']
    else:
        text = ''
    prompt_box = st.text_area(label='prompt (edit it!!)', value=text, height=150)

    if marker_data['location'] is not None:
        if st.button('send to gemini'):
            prompt = str(prompt_box).strip()
            if len(prompt)==0:
                prompt = 'describe this image'

            r = utils.get_gemini_response(svimg, prompt)
            st.markdown(f'**gemini response**\n\n{r.text}')

            
print ('------------------------')