""" Trilio functions """
import logger
import requests
import datetime
import json
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


def create_workload(token, token_data, server_id):
    """ Create a workload for a given server """
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads"
    headers = os.os_headers(token)
    server = os.get_server(token, token_data, server_id)
    workload_type_id = "f82ce76f-17fe-438b-aa37-7a023058e50d"
    data = {
        "workload": {
            "name": server["id"],
            "description": None,
            "workload_type_id": "f82ce76f-17fe-438b-aa37-7a023058e50d",
            "source_platform": None,
            "instances": [
                {
                    "instance-id": server["id"]
                }
            ],
            "jobschedule": {
                "enabled": False,
                "timezone": "EST"
            },
            "metadata": {}
        }
    }
    data_json = json.dumps(data)
    logger.info(f"Creating workload for server {server['id']}")
    resp = requests.post(workload_url, headers=headers, verify=False, data=data_json)
    if resp.status_code != 202 and resp.status_code != 201:
        # it should return 201 created but returns 202 accepted for some reason
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




def workload_fits(workload_id):
    """ return bool, is this workload likely to fit into the backup window? """
    # TODO: this
    return False


def get_next_workload_to_run(token, token_data):
    """ Find the next workload to run """
    workloads = get_workloads(token, token_data)
    # Have any workloads not had any snapshots yet? If so, choose it.
    # First, find the snapshots associated with each workload
    for workload in workloads:
        workload_id = workload["id"]
        snaps[workload_id] = trilio.get_snapshots(token, token_data, workload_id=workload_id)
        workload["snaps"] = snaps
    # Check if any of the workloads have no snaps, and if they fit
    for workload in [ w for w in workloads if not w["snaps"] ]:
        if trilio.workload_fits(workload["id"]):
            return workload
    # If not, get a list of workloads sorted least recently backed up

    # Is its backup less than a week old? Exit.
    # Otherwise, check how long it would take to back up.
    # If it would finish before the window is up, choose it.
    # Trigger its backup


def exec_full_snaposhot(token, token_data, next_workload):
    """ Run a full snapshot """
    return


def is_max_workloads_running(token, token_data):
    """ Return bool, are the max number of workloads already running? """
    return True

