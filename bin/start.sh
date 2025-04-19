if [ -z "${GCP_API_KEY}" ]; then
    echo "error: must set GCP_API_KEY env var"
    exit -1
fi

sed "s/__GCP_API_KEY__/${GCP_API_KEY}/g" app/index-template.html  > app/index.html

cd app
flask --app main run
cd 