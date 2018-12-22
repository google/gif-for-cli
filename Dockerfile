FROM python:3.6-alpine
MAINTAINER pierrefenoll@gmail.com
RUN set -x \
 && apk update && apk upgrade \
 && apk add ffmpeg zlib-dev libjpeg-turbo-dev \
            gcc musl-dev \
 && export PATH="$PATH:/root/.local/bin" \
 && pip3 install --user gif-for-cli
ENTRYPOINT ["/root/.local/bin/gif-for-cli"]
