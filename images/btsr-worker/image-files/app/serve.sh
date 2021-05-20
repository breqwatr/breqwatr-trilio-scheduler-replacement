#!/bin/bash
echo "starting up an api"
gunicorn btsrworker.api.report:app --bind 0.0.0.0:80
