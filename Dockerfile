FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update
RUN apt install -y xclip

# Copy in the source code
COPY src ./src
COPY imgs ./imgs
WORKDIR src
EXPOSE 8501

# Setup an app user so the container doesn't run as the root user
#RUN useradd app
#USER app

#CMD ["/bin/bash", "check.sh"]
CMD ["streamlit", "run", "--server.headless", "true", "demo.py"]