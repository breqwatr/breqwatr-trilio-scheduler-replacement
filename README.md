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

### OpenStack & Trilio auth config

Make a directory to store the auth file(s). You could also use a PV but for simplicity
a local hostVol is used from /btsr/openrc/. Also make a logs dir.

```bash
mkdir -p /btsr/openrc/ /var/log/btsr
```

Create at least one openrc file to authenticate to your openstack project

`vi /btsr/openrc/project-openrc.sh`

```
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=<project name>
export OS_TENANT_NAME=<project name>
export OS_USERNAME=<username>
export OS_PASSWORD=<password>
export OS_AUTH_URL=https://<cloud fqdn>:5000/v3
export OS_INTERFACE=public
export OS_ENDPOINT_TYPE=publicURL
export OS_IDENTITY_API_VERSION=3
export OS_REGION_NAME=RegionOne
export OS_AUTH_PLUGIN=password
```


Create a helm config file to identify your openrc files:

`vi btsr-helm.yaml`

```yaml
# btsr-helm.yaml
... somehow specify the openrc file(e) to use
```

### Deploy the app using Helm
cd ../helm
helm install -f btsr.yaml btsr ./btsr

# Show it
helm list
```
