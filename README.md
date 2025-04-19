# Streetview analytics with Gemini

This demo allows you to navigate to a location in Google StreetView and use Gemini to find stuff about it. For instance

- Count people, signs, vehicles, trees
- Estimate quality/status of road infrastructures, signs, markings
- Estimate vegetation, characterize buildings
- Detect informal business, human activity
- Read signs and panels for business, indications, places
- Anything in your imagination

![metric objects definitions](imgs/svgemini.png)

# Running the demo

create a nre project in GCP

api key with
 --

 gcloud services enable  --project keen-index-457301-a6 "maps-backend.googleapis.com"


maps-backend.googleapis.com
generativelanguage.googleapis.com          Generative Language API
street-view-image-backend.googleapis.com   Streetview Static API

Run this demo locally in your machine, as it uses the clipboard to communicate between Streamlit and javascript.

## with docker

install

    git clone https://github.com/rramosp/streetview_gemini_demo.git
    cd streetview_gemini_demo
    sh bin/build_docker.sh

run

    export GCP_API_KEY=[your gcp api key]
    sh bin/run_docker.sh

open your browser at [http://localhost:5000](http://localhost:5000)


## with conda envs

install

    git clone https://github.com/rramosp/streetview_gemini_demo.git
    cd streetview_gemini_demo
    conda create -n demo python=3.12
    conda activate demo
    pip install -r requirements.txt

run

    cd src
    export GCP_API_KEY=[your gcp api key]
    bin/start.sh

open your browser at [http://localhost:5000](http://localhost:5000)
