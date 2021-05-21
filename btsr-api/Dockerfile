# image: breqwatr/btsr-api
FROM breqwatr/btsr-lib
COPY image-files /
ADD api/ /btsr/api
RUN pip install /btsr/api
CMD /start.sh
