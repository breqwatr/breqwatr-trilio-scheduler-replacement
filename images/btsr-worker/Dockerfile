FROM ubuntu:focal

RUN mkdir /app \
    && apt-get update \
    && apt-get install -y \
      python3 \
      python3-pip \
    && pip install \
      storops \
      python-openstackclient

COPY image-files /

CMD /start.sh
