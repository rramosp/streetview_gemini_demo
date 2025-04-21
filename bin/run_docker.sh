if [ -z "${GENAI_API_KEY}" ]; then
    echo "error: must set GENAI_API_KEY env var"
    exit -1
fi

if [ -z "${GOOGLE_MAPS_API_KEY}" ]; then
    echo "error: must set GOOGLE_MAPS_API_KEY env var"
    exit -1
fi

sudo docker run -p 5000:5000  \
                -e GENAI_API_KEY=$GENAI_API_KEY \
                -e GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY \
                streetviewgemini/demo 
