sudo docker run -p 8501:8501  \
                -e DISPLAY=$DISPLAY  \
                -e GEMINI_API_KEY=$GEMINI_API_KEY \
                -e STREETVIEW_API_KEY=$STREETVIEW_API_KEY \
                -v /tmp/.X11-unix:/tmp/.X11-unix  \
                -e QT_X11_NO_MITSHM=1  \
                svgemini/demo 
