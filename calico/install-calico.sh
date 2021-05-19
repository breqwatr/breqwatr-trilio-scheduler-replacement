#!/bin/bash

if [ ! -f custom-resources.yaml ]; then
  echo "ERROR: You need to cd to calico/"
fi

echo "installing calico"
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml

kubectl taint nodes --all node-role.kubernetes.io/master-

