""" Trilio functions """
import requests
import btsrworker.lib.openstack as os

ENDPOINT = "TrilioVaultWLM"

def get_workloads(token, token_data):
    """ Get a list of Trilio workloads """
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workloads_url = f"{wlm_url}/workloads"
    headers = os.os_headers(token)
    workloads_resp = requests.get(workloads_url, headers=headers, verify=False)
    if workloads_resp.status_code != 200:
        raise os.OpenStackException(f"{resp.status_code}: {resp.reason}")
    return workloads_resp.json()["workloads"]


def get_workload(token, token_data, workload_id):
    """ Get info about a particular workload """
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads/{workload_id}"
    headers = os.os_headers(token)
    workload_resp = requests.get(workload_url, headers=headers, verify=False)
    if workload_resp.status_code != 200:
        raise os.OpenStackException(f"{resp.status_code}: {resp.reason}")
    return workload_resp.json()["workload"]

