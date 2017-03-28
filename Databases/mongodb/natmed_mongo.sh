docker run \
    --detach \
    --publish=27017:27017 \
    --volume=$HOME/mongo/natmed/data:/data/db \
    mongo:latest