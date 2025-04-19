FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY app ./app
COPY bin ./bin
EXPOSE 5000

CMD ["sh", "bin/start.sh"]

