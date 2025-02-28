
import requests
from skimage import io
import folium
import numpy as np
import tempfile
from google import genai

def get_api_key():
    with open('apikey.txt') as f:
        api_key = f.read().strip()
    return api_key

def pull_streetview_image(lon, lat, heading=180, zoom=5, size='600x600'):

    """Takes an addres string as an input and returns an image from google maps streetview api"""
    pic_base = 'https://maps.googleapis.com/maps/api/streetview?'

    # define the params for the picture request
    pic_params = {'key': get_api_key(),
                'location' : f"{lat},{lon}",
                'heading': heading,
                'zoom': zoom ,
                'size': size}
    
    #Requesting data
    pic_response = requests.get(pic_base, params=pic_params)

    filename = f'/tmp'
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = f'{tmpdir}/img.jpg'
        with open(filename, "wb") as file:
            file.write(pic_response.content)
        
        # Closing connection to API
        pic_response.close()
        
        img = io.imread(filename)
    return img


def add_marker(session_state):

    hist = session_state['clipboard_history']
    if len(hist)<1:
        return {'location': None, 'fg': None, 'zoom': None}

    coords = hist[-1]
    lat,lon = [float(i) for i in coords.split(' ')[-1].split(',')]
    print ('coords', lat, lon)
    marker_feature_group = folium.FeatureGroup(name=str(np.random.randint(1000000)))
    marker = folium.Marker(
            location=[lat, lon],
            popup=f"the click popup",
            tooltip=f"the click tooltip",
            icon=folium.Icon(color="green")
        )
    marker_feature_group.add_child(marker)

    last_coords = coords
    return {'location': [lat, lon], 'fg': marker_feature_group, 'zoom': 15}


def get_gemini_response(img, prompt):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = f'{tmpdir}/img.jpg'
        io.imsave(filename, img)
    
    
        client = genai.Client(api_key=get_api_key())
        img_object = client.files.upload(file=filename)
    
    
        response = client.models.generate_content(
          model='gemini-2.0-flash',
          contents=[prompt,img_object]
        )
    
    return response