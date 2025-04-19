if [ -z "${GEMINI_API_KEY}" ]; then
    echo "error: must set GEMINI_API_KEY env var"
    exit -1
fi

if [ -z "${STREETVIEW_API_KEY}" ]; then
    echo "error: must set STREETVIEW_API_KEY env var"
    exit -1
fi


sudo docker run -p 8501:8501  \
                -e DISPLAY=$DISPLAY  \
                -e GEMINI_API_KEY=$GEMINI_API_KEY \
                -e STREETVIEW_API_KEY=$STREETVIEW_API_KEY \
                -v /tmp/.X11-unix:/tmp/.X11-unix  \
                -e QT_X11_NO_MITSHM=1  \
                svgemini/demo 
