#!/bin/bash
# enter the interactve idle worker container
kubectl exec -it \
  $(kubectl get pods | grep Running | grep btsr-worker-idle | awk '{print $1}') -- bash
