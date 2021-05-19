#!/bin/bash

if [ ! -f custom-resources.yaml ]; then
  echo "ERROR: You need to cd to calico"
  exit 1
fi

echo "installing calico"
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml
kubectl create -f custom-resources.yaml

echo "waiting a minute before removing the node-role.kubernetes.io/master taint"
sleep 60
kubectl taint nodes --all node-role.kubernetes.io/master-

