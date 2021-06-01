#!/bin/bash
set -e


#################
# sanity checks #
#################
if [[ "$(lsb_release -rs)" != "20.04" ]]; then
  echo "ERROR: Expected Ubuntu 20.04" >&2
  exit 1
fi

if [[ "$(whoami)" != "root" ]]; then
  echo "ERROR: be root" >&2
  exit 1
fi


##########
# Docker #
##########
echo "Installing Docker..."
if [[ "$(which docker)" == "" ]] ; then
  apt-get update
  apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io
  echo "Done installing docker"
else
  echo "  Docker was already installed"
fi
echo


####################################
# let iptables see bridged traffic #
####################################
echo "Letting iptables see bridged traffic..."
if [[ ! -f /etc/modules-load.d/k8s.conf ]] ; then
	cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF
	cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
	sysctl --system
else
  echo "  iptables already allowed to see bridged traffic"
fi
echo


#####################################
# Install kubeadm, kubelet, kubectl #
#####################################
echo "Installing kubeadm, kubelet, kubectl"
if [[ "$(dpkg -l | grep kubectl)" == "" ]]; then
  apt-get update
  apt-get install -y apt-transport-https ca-certificates curl
  curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
  echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
  apt-get update
  apt-get install -y kubelet kubeadm kubectl
  # hold prevents updates to this packages
  apt-mark hold kubelet kubeadm kubectl
else
  echo "  kubeadm, kubelet, kubectl are already installed"
fi
echo


############
# init k8s #
############
echo "Running kubeadm init"
if [[ ! $(docker ps --format '{{.Names}}' | grep k8s_kube-apiserver) ]]; then
  kubeadm init --pod-network-cidr="192.168.0.0/24" --service-cidr "192.168.1.0/24"
else
  echo "  kubeadm already initialized"
fi
echo


#########
# Utils #
#########
if [[ ! $(dpkg -l | grep apache2-utils) ]]; then
  apt-get install -y apache2-utils
fi

############
# env conf #
############
echo "configuring $HOME/.bashrc"
if [[ "$(cat $HOME/.bashrc | grep 'KUBECONFIG')" == "" ]] ; then
  export KUBECONFIG=/etc/kubernetes/admin.conf
  echo 'export KUBECONFIG=/etc/kubernetes/admin.conf' >> $HOME/.bashrc
  echo 'export KUBECONFIG=/etc/kubernetes/admin.conf'
  echo "Done configuring $HOME/.bashrc"
else
  echo "  $HOME/.bashrc already configured"
fi
echo


########
# helm #
########
echo "installing helm"
if [[ "$(which helm)" == "" ]]; then
  snap install helm --classic
else
  echo "  helm was already installed"
fi
echo


# Verify
sleep 30
kubectl cluster-info
