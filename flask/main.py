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


app = Flask(__name__)


def call_streetview_and_gemini(prompt, lon, lat, heading=180, zoom=1, pitch=0, size='600x600'):

    """Takes an addres string as an input and returns an image from google maps streetview api"""
    pic_base = 'https://maps.googleapis.com/maps/api/streetview?'

    # define the params for the picture request
    #pic_params = {'key': get_api_key(),
    pic_params = {'key': os.environ['STREETVIEW_API_KEY'],
                'location' : f"{lat},{lon}",
                'heading': heading,
                'zoom': zoom ,
                'pitch': pitch,
                'size': size}
    
    #Requesting data
    print('calling streetview')
    pic_response = requests.get(pic_base, params=pic_params)

    with tempfile.TemporaryDirectory() as tmpdir:
        input_filename = f'{tmpdir}/input.jpg'
        output_filename = f'{tmpdir}/output.jpg'

        with open(input_filename, "wb") as file:
            file.write(pic_response.content)
        
        # Closing connection to API
        pic_response.close()
        
        #client = genai.Client(api_key=get_api_key())
        try:
            client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
            img_object = client.files.upload(file=input_filename)
        
            response_html_text = None
            response_html_image = None
            response = client.models.generate_content(
                
            model='gemini-2.0-flash-exp',
            contents=[prompt,img_object],
            config=genai.types.GenerateContentConfig(response_modalities=['Text', 'Image'])
            )

            for part in response.candidates[0].content.parts:
                if part.text:
                    print ('has text')
                    response_html_text = markdown.markdown(part.text.strip().replace('**Caption:** ', ''))
                elif part.inline_data:
                    print ('has image')
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(output_filename)
                    
                    data = open(output_filename, 'rb').read() # read bytes from file
                    data_base64 = base64.b64encode(data)  # encode to base64 (bytes)
                    data_base64 = data_base64.decode()    # convert bytes to string
                    response_html_image = '<img width=400px, src="data:image/jpeg;base64,' + data_base64 + '">'

        except Exception as e:
            response_html_text = (f"<b/>ERROR<b/><br/>{e}")



    return {'html_text':response_html_text, 'html_image': response_html_image, 'metadata': response.usage_metadata.model_dump()}


@app.route("/")
def main():
    return render_template('./index.html')


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
def senf_from_filesystem(path):
	print(path)
	return send_from_directory('./static/', path)

