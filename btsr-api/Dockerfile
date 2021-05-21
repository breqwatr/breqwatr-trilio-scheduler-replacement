# image: breqwatr/btsr-api
FROM breqwatr/btsr-lib
COPY image-files /
ADD api/ /api
RUN pip install /api
CMD /start.sh
