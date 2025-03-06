import sys
sys.path.append('../src')


import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import folium
from tqdm import tqdm
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

if not 'previous_prompt_text' in st.session_state.keys():
    st.session_state['previous_prompt_text'] = None    

if not 'prompt_text' in st.session_state.keys():
    st.session_state['prompt_text'] = None    

if not 'previous_location' in st.session_state.keys():
    st.session_state['previous_location'] = None    

if not 'svimage' in st.session_state.keys():
    st.session_state['svimage'] = None    

if not 'previous_prompt_text' in st.session_state.keys():
    st.session_state['previous_prompt_text'] = None    

if not 'gemini_response' in st.session_state.keys():
    st.session_state['gemini_response'] = None    



if not 'clipboard_history' in st.session_state.keys():
    st.session_state['clipboard_history'] = []

if not 'first_run' in st.session_state.keys():
    clipboard.copy('dummy')
    st.session_state['first_run'] = 'done'

def call_gemini(svimg, prompt, msgbox):
    prompt = prompt.strip()
    msgbox.markdown(utils.text_with_gif('calling gemini', '../imgs/hourglass.gif'),
                        unsafe_allow_html=True)

    if len(prompt)==0:
        prompt = 'describe this image'

    r = utils.get_gemini_response(svimg, prompt)
    msgbox.empty()
    return r

def disable_ctrl_enter():
    import streamlit.components.v1 as components
    components.html(
        """
    <script>
    const textareas = parent.document.querySelectorAll("textarea");
    textareas.forEach(textarea => {
      textarea.addEventListener("keydown", function(event) {
        if ((event.ctrlKey || event.metaKey) && event.keyCode === 13) {
          event.preventDefault();
          event.stopPropagation();
        }
      });
    });
    </script>
    """,
        height=0,
    )

st.header('StreetView analytics with Gemini', divider='gray')
st.markdown('**Instructions**: Select a use case and click `send to gemini` **OR** navigate anywhere, click on the map, write a prompt and `send to gemini`.')

paste = clipboard.paste()
new_coords = False
if paste.startswith('COORDS'):
    new_coords = True
    st.session_state['clipboard_history'].append(paste)

marker_data = utils.add_marker(st.session_state)

m = folium.Map(zoom_start = marker_data['zoom'])
folium.plugins.MousePosition().add_to(m)
folium.plugins.Geocoder(add_marker=False).add_to(m)
utils.add_basemaps(m)

m.add_child(folium.ClickForLatLng('"COORDS " + lat + "," + lng', alert=False))

col1, col2 = st.columns([.6,.4])

with col1:

    the_map = st_folium(m, 
                        center=marker_data['location'], 
                        zoom=marker_data['zoom'],
                        width=1100,
                        height=500, 
                        feature_group_to_add=marker_data['fg'])

    gemini_response = None

    msgbox = st.markdown('')
    
    if marker_data['location'] != st.session_state['previous_location'] or \
       st.session_state['prompt_text'] != st.session_state['previous_prompt_text']:

        lat, lon = marker_data['location']

        msgbox.markdown(utils.text_with_gif('downloading streetview imagery', '../imgs/hourglass.gif'),
                                unsafe_allow_html=True)
        headings = [0,90,180,270]
        svimg = {}

        for heading in headings:
            svimg[heading] = utils.pull_streetview_image(lon, lat, 
                                                         heading=heading, 
                                                         fov=90, 
                                                         pitch=0,
                                                         size='500x500')

        svimg = np.vstack([np.transpose(z, (1,0,2)) for z in svimg.values()])
        svimg = np.transpose(svimg, (1,0,2))

        gemini_response = call_gemini(svimg, st.session_state['prompt_text'], msgbox)

        st.session_state['svimage'] = svimg
        st.session_state['gemini_response'] = gemini_response
        msgbox.empty()
        
        st.session_state['previous_prompt_text'] = st.session_state['prompt_text']
        st.session_state['previous_location'] = marker_data['location']

    if st.session_state['svimage'] is not None:
        lat, lon = marker_data['location']
        st.image(st.session_state['svimage'])
        msgbox.write (f'Downloaded streetView 360 imagery at lat: {lat:.5f}, lon: {lon:.5f}')

        

with col2:
    st.header('Use cases', divider='gray')
    c1,c2,c3,c4 = st.columns(4)

    with c1:
        if st.button('madrid\n[construction]'):
            clipboard.copy('COORDS 40.41912,-3.70617')
            st.session_state['prompt_text'] = 'Are there construction works in this image. If so, describe their nature.'
            st.rerun()

    with c2:
        if st.button('medellin\n[informal business]'):
            clipboard.copy('COORDS 6.24949,-75.57015')
            st.session_state['prompt_text'] = '''
Are there informal business in this image. If so, describe them and  include bounding box detections in json            
            '''
            st.rerun()

    with c3:
        if st.button('new york\n[people and signs]'):
            clipboard.copy('COORDS 40.71494,-73.99840')
            st.session_state['prompt_text'] = '''
    count the number of people and vehicles in this mage.
    also, read all the sings and text that you see
            '''
            st.rerun()

    with c4:
        if st.button('rome\n[building assesment]'):
            clipboard.copy('COORDS 41.89451,12.47358')
            st.session_state['prompt_text'] = '''
what is the name of business and restaurants that you see here?
what is the overall state of the buildings?                 
        '''
            st.rerun()


    st.header('Gemini')
    if 'prompt_text' in st.session_state:
        text = st.session_state['prompt_text']
    else:
        text = ''
    #st.markdown('prompt (**EDIT and PLAY with IT**)!!')
    prompt_box = st.text_area(label='prompt (**EDIT and PLAY with IT**)!!', value=text, height=100)

    if marker_data['location'] is not None:
        gemini_button = st.button('send to gemini')

        if st.session_state['gemini_response'] is not None:
            st_response = st.markdown(f'**gemini response**\n\n{st.session_state['gemini_response'].text}')
        else:
            st_response = st.markdown('')

        if gemini_button:
            st.session_state['prompt_text'] = str(prompt_box).strip()
            st.rerun()

if st.session_state['previous_prompt_text'] is None and st.session_state['prompt_text'] is not None:
    st.session_state['previous_prompt_text'] = st.session_state['prompt_text']

disable_ctrl_enter()
