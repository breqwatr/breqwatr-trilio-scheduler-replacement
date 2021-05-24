# image: breqwatr/btsr-lib
FROM ubuntu:focal
RUN mkdir -p /var/log/btsr \
    && apt-get update \
    && apt-get install -y \
      python3 \
      python3-pip
ADD lib/ /btsr/lib
# multiple run layers on purpose, trading image size for build speed
RUN pip install /btsr/lib
