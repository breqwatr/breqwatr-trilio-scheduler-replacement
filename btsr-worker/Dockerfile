# image: breqwatr/btsr-api
FROM breqwatr/btsr-lib
ADD worker/ /btsr/worker
ADD image-files/ /
RUN pip install /btsr/worker
CMD tail -f /dev/null
