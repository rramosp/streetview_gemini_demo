#!/bin/bash

if [ -z "${GENAI_API_KEY}" ]; then
    echo "error: must set GENAI_API_KEY env var"
    exit -1
fi

if [ -z "${GOOGLE_MAPS_API_KEY}" ]; then
    echo "error: must set GOOGLE_MAPS_API_KEY env var"
    exit -1
fi

sed "s/__GOOGLE_MAPS_API_KEY__/${GOOGLE_MAPS_API_KEY}/g" app/index-template.html  > app/index.html

cd app
python main.py
cd 
