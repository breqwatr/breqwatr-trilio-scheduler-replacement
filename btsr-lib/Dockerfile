# image: breqwatr/btsr-lib
FROM ubuntu:focal
ADD lib/ /btsr/lib
RUN mkdir /app \
    && apt-get update \
    && apt-get install -y \
      python3 \
      python3-pip \
    && pip install /btsr/lib
