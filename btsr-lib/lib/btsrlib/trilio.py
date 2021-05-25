""" Trilio functions """
import requests
import datetime
import btsrlib.openstack as os

ENDPOINT = "TrilioVaultWLM"


def get_datetime(trilio_timestamp):
    """ Return a datetime object from a trilio timestamp """
    return datetime.datetime.strptime(trilio_timestamp, "%Y-%m-%dT%H:%M:%S.%f")


def get_workloads(token, token_data):
    """Get a list of Trilio workloads"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workloads_url = f"{wlm_url}/workloads"
    headers = os.os_headers(token)
    resp = requests.get(workloads_url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["workloads"]


def get_workload(token, token_data, workload_id):
    """Get info about a particular workload"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads/{workload_id}"
    headers = os.os_headers(token)
    resp = requests.get(workload_url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["workload"]


def get_snapshots(token, token_data, workload_id=None):
    """ List the snapshots of a workload, sorted by created date (old to new) """
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    if workload_id is None:
        url = f"{wlm_url}/snapshots"
    else:
        url = f"{wlm_url}/snapshots?workload_id={workload_id}"
    headers = os.os_headers(token)
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    snaps = resp.json()["snapshots"]
    snaps.sort(key=lambda s: get_datetime(s["created_at"]), reverse=False)
    return snaps


def get_snapshot(token, token_data, snapshot_id):
    """ Get info about a snapshot """
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    url = f"{wlm_url}/snapshots/{snapshot_id}"
    headers = os.os_headers(token)
    resp = requests.get(url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["snapshot"]


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
            "id": server_id,
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
