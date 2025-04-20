# Streetview analytics with Gemini

This demo allows you to navigate to a location in Google StreetView and use Gemini to find stuff about it. For instance

- Count people, signs, vehicles, trees
- Estimate quality/status of road infrastructures, signs, markings
- Estimate vegetation, characterize buildings
- Detect informal business, human activity
- Read signs and panels for business, indications, places
- Anything in your imagination

![streetview with gemini](imgs/svgemini.png)

# Running the demo


## Setup

create or choose a project in GCP and follow these steps


1. Enable the APIs
   
```
        gcloud services enable --project <YOUR_PROJECT_ID> \
            maps-backend.googleapis.com \
            generativelanguage.googleapis.com \
            street-view-image-backend.googleapis.com
```

Check they are enabled

        gcloud services list --project <YOUR_PROJECT_ID>
   

1. In GCP Console, under `APIS and Services` $\to$ `Credentials` create TWO new API keys. 

Allow one (`GOOGLE_MAPS_API_KEY`) to use the following API

```
        maps-backend.googleapis.com                Maps Javascript API
```

Allow the second one (`GENAI_API_KEY`) to use these APIs

```
        generativelanguage.googleapis.com          Generative Language API
        street-view-image-backend.googleapis.com   Streetview Static API
```



## Run with docker (recommended)

install

    git clone https://github.com/rramosp/streetview_gemini_demo.git
    cd streetview_gemini_demo
    sh bin/build_docker.sh

run

    export GOOGLE_MAPS_API_KEY=[your google maps api key]
    export GENAI_API_KEY=[your genai api key]
    sh bin/run_docker.sh

open your browser at [http://localhost:5000](http://localhost:5000)


## Or run with conda envs

install

    git clone https://github.com/rramosp/streetview_gemini_demo.git
    cd streetview_gemini_demo
    conda create -n demo python=3.12
    conda activate demo
    pip install -r requirements.txt

run

    export GOOGLE_MAPS_API_KEY=[your google maps api key]
    export GENAI_API_KEY=[your geani api key]
    bin/start.sh

open your browser at [http://localhost:5000](http://localhost:5000)
