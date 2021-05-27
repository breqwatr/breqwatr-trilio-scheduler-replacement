import urllib3
import requests
import logging

# enable logging and configure the log file path
logging.basicConfig(
    filename="/var/log/btsr/btsr.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# disable ssl warnings
urllib3.disable_warnings()

# disable urllib3 log spam
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
