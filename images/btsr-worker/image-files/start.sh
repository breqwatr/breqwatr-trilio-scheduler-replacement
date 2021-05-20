#!/bin/bash

if [[ ! -f /app/admin-openrc.sh ]]; then
  echo "ERROR: /app/export-openrc.sh not found"
  exit 1
fi

path=$(date "+%Y-%m-%d-%H-%M-%S").log
echo "Hello" > $path

