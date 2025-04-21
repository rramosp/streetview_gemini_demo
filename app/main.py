from flask import Flask, request, render_template, send_from_directory, jsonify
import os
from skimage import io
import tempfile
import requests
from google import genai
import markdown
from io import BytesIO
from PIL import Image
import base64 
import numpy as np

app = Flask(__name__)


model_id='gemini-2.0-flash-exp'

zoom2fov = lambda zoom: np.arctan(2**(1-zoom))*360/np.pi

def call_streetview_and_gemini(prompt, lon, lat, heading=180, zoom=1, pitch=0, size='1200x600'):


    """
    Takes a prompt string and a location spec in Google Streetview and
        
        1. Uses the Streetview Static API to download the streetview image
        2. Sends it to Gemini along with the prompt

    Returns a dict with the text and image elements returned by Gemini             
    """
    
    with tempfile.TemporaryDirectory() as tmpdir:

        response_html_text = None
        response_html_image = None
        response_metadata = None

        try:

            pic_base = 'https://maps.googleapis.com/maps/api/streetview?'

            # define the params for the picture request
            pic_params = {'key': os.environ['GENAI_API_KEY'],
                        'location' : f"{lat},{lon}",
                        'heading': heading,
                        'fov': zoom2fov(zoom) ,
                        'pitch': pitch,
                        'size': size}
            
            # Call Streetview
            pic_response = requests.get(pic_base, params=pic_params)


            input_filename = f'{tmpdir}/input.jpg'
            output_filename = f'{tmpdir}/output.jpg'

            with open(input_filename, "wb") as file:
                file.write(pic_response.content)
            
            pic_response.close()
            
            # Call Gemini
            client = genai.Client(api_key=os.environ['GENAI_API_KEY'])
            img_object = client.files.upload(file=input_filename)
        
            response = client.models.generate_content(                
                model=model_id,
                contents=[prompt,img_object],
                config=genai.types.GenerateContentConfig(response_modalities=['Text', 'Image'])
            )

            response_metadata = response.usage_metadata.model_dump()
            
            for part in response.candidates[0].content.parts:
                if part.text:
                    response_html_text = markdown.markdown(part.text.strip().replace('**Caption:** ', ''))
                elif part.inline_data:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(output_filename)
                    
                    data = open(output_filename, 'rb').read() # read bytes from file
                    data_base64 = base64.b64encode(data)  # encode to base64 (bytes)
                    data_base64 = data_base64.decode()    # convert bytes to string
                    response_html_image = '<img width="800px%", src="data:image/jpeg;base64,' + data_base64 + '">'


        except Exception as e:
            response_html_text = (f"<b/>ERROR<b/><br/>{e}")

    return { 'html_text':response_html_text, 'html_image': response_html_image, 'metadata': response_metadata, 'model_id': model_id }

@app.route("/")
def main():
    from glob import glob
    print('main', os.getcwd(), glob('*'))
    return send_from_directory('.', 'index.html')

@app.route("/<path:path>")
def send_local(path):
	print('local', path)
	return send_from_directory('.', path)

@app.route('/foo', methods=['POST']) 
def foo():
    print (request.json)
    data = {'gemini-text': 'hola que tal', 'ntokens': 3012}
    return jsonify(data)


@app.route('/gemini', methods=['POST']) 
def gemini():
    r = request.json
    print (r)
    response = call_streetview_and_gemini(prompt=r['prompt'], lon=r['lon'], lat=r['lat'], heading=r['heading'], zoom=r['zoom'], pitch=r['pitch'])
    return jsonify(response)


@app.route('/static/<path:path>') #Everything else just goes by filename
def send_from_filesystem(path):
	print(path)
	return send_from_directory('./static/', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)