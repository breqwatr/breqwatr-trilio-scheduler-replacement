#!/bin/bash
set -e

if [[ ! -f metallb-configmap.yaml.template ]]; then
  echo "ERROR: need to cd to metallb"
  echo 1
fi

if [[ "$1" == "" ]]; then
  echo "ERROR: IP range is required as pos arg - example: 10.106.254.101-10.106.254.106"
  exit 1
fi
ip_range=$1

# set strictARP: true
kubectl get configmap  -n kube-system  kube-proxy -o yaml > kube-proxy-configmap.yaml
sed -i 's/strictARP: false/strictARP: true/g' kube-proxy-configmap.yaml
kubectl apply -f kube-proxy-configmap.yaml
rm -f kube-proxy-configmap.yaml

# Install metalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.5/manifests/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.9.5/manifests/metallb.yaml
kubectl create secret generic -n metallb-system memberlist --from-literal=secretkey="$(openssl rand -base64 128)"

cp metallb-configmap.yaml.template metallb-configmap.yaml
sed "s/ADDRESSES/$ip_range/g" metallb-configmap.yaml.template > metallb-configmap.yaml
kubectl apply -f metallb-configmap.yaml
rm metallb-configmap.yaml
