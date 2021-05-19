# Trilio scehduler replacement

## Setup
This is intended to run as a single-node k8s cluster on an ubuntu 20.04 VM.

Pull the code then run the following to set it up:

```
# Install k8s
cd bin
./bootstrap-node.sh

# Add Calico
cd calico
./install-calico.sh

# Enable MetalLB for a given IP range
cd ../metallb
ip_range="10.106.252.140-10.106.252.165"
install-metallb.sh $ip_range

# Deploy NGINX ingress controller

```
