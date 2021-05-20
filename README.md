# Trilio scehduler replacement

## Setup K8S
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
cd ../nginx-ingress
./install-nginx.ingress.sh
```

## Deploy the app

```
# Build the images
cd ../
./build-images.sh
```

Create a `btsr-helm.yaml` to identify your openrc files:
```yaml
# btsr-helm.yaml
... somehow specify the openrc file(e) to use

```
# Deploy the app
cd ../helm
helm install -f btsr.yaml btsr ./btsr

# Show it
helm list
```
