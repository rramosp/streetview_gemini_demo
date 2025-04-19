if [ -z "${GCP_API_KEY}" ]; then
    echo "error: must set GCP_API_KEY env var"
    exit -1
fi

sudo docker run -p 5000:5000  \
                -e GCP_API_KEY=$GCP_API_KEY \
                --net=host \
                streetviewgemini/demo 
