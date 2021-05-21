#!/bin/bash
echo "starting btsr-api"
gunicorn btsrapi.main:app --bind 0.0.0.0:80
