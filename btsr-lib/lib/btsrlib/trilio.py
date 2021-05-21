""" Trilio functions """
import requests
import btsrlib.openstack as os

ENDPOINT = "TrilioVaultWLM"


def get_workloads(token, token_data):
    """Get a list of Trilio workloads"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workloads_url = f"{wlm_url}/workloads"
    headers = os.os_headers(token)
    workloads_resp = requests.get(workloads_url, headers=headers, verify=False)
    if workloads_resp.status_code != 200:
        raise os.OpenStackException(f"{resp.status_code}: {resp.reason}")
    return workloads_resp.json()["workloads"]


def get_workload(token, token_data, workload_id):
    """Get info about a particular workload"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads/{workload_id}"
    headers = os.os_headers(token)
    workload_resp = requests.get(workload_url, headers=headers, verify=False)
    if workload_resp.status_code != 200:
        raise os.OpenStackException(f"{resp.status_code}: {resp.reason}")
    return workload_resp.json()["workload"]


def is_backup_enabled(server):
    """Return if backups are enabled or not in a server"""
    return (
        "metadata" in server
        and "enable-backups" in server["metadata"]
        and (
            server["metadata"]["enable-backups"].lower() == "yes"
            or server["metadata"]["enable-backups"].lower() == "true"
        )
    )


def get_trilio_summary(server_details):
    """Given a dict of server details, remove extrenuous data and add trilio data"""
    data = {}
    for server_id in server_details:
        server = server_details[server_id]
        data[server_id] = {
            "name": server["name"],
            "created": server["created"],
            "backups_enabled": str(is_backup_enabled(server)),
            "workload_exists": "False",
            "last_backup": "never",
            "last_backup_duration": "-",
            "last_backup_size": "-",
            "last_backup_error": "-",
        }
    return data
