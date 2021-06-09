""" Trilio functions """
import requests
import datetime
import json
import btsrlib.openstack as os
import btsrlib.trilio as trilio
from btsrlib.common import env

ENDPOINT = "TrilioVaultWLM"


def conf():
    """Return a dict with the configured env vars"""
    keys = [
        "concurrent_fulls_cloud",
        "concurrent_fulls_host",
        "concurrent_total_cloud",
        "concurrent_total_host",
        "nfs_speed_bytes_per_second",
        "time_est_volume_create_time_seconds",
        "time_est_workload_time_seconds",
        "time_est_fudge_factor",
        "backup_interval_days",
        "backup_full_interval_days",
        "backup_retention_days",
        "allow_weekdays",
        "allow_weekends",
        "allow_all_day_weekdays",
        "allow_all_day_weekends",
        "weekday_blacklist_start_time",
        "weekday_blacklist_end_time",
        "weekend_blacklist_start_time",
        "weekend_blacklist_end_time",
    ]
    data = {}
    for key in keys:
        data[key] = env(key)
        if data[key].lower() == "yes" or data[key].lower() == "true":
            data[key] = True
        elif data[key].lower() == "no" or data[key].lower() == "false":
            data[key] = False
    return data


def get_datetime(trilio_timestamp):
    """Return a datetime object from a trilio timestamp"""
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
    """Create a workload for a given server"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads"
    headers = os.os_headers(token)
    server = os.get_server(token, token_data, server_id)
    workload_type_id = "f82ce76f-17fe-438b-aa37-7a023058e50d"
    data = {
        "workload": {
            "name": server["id"],
            "description": server["name"],
            "workload_type_id": "f82ce76f-17fe-438b-aa37-7a023058e50d",
            "source_platform": None,
            "instances": [{"instance-id": server["id"]}],
            "jobschedule": {"enabled": False, "timezone": "EST"},
            "metadata": {},
        }
    }
    data_json = json.dumps(data)
    resp = requests.post(workload_url, headers=headers, verify=False, data=data_json)
    if resp.status_code != 202 and resp.status_code != 201:
        # it should return 201 created but returns 202 accepted for some reason
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["workload"]


def get_snapshots(token, token_data, workload_id=None):
    """List the snapshots of a workload, sorted by created date (old to new)"""
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
    """Get info about a snapshot"""
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


def get_trilio_summary(token, token_data, server_details):
    """Given a dict of server details, remove extrenuous data and add trilio data"""
    data = {}
    workloads = trilio.get_workloads(token, token_data)
    for server_id in server_details:
        server = server_details[server_id]
        workload_exists = "False"
        last_backup = "never"
        last_backup_duration = "-"
        last_backup_size = "-"
        last_backup_error = "-"
        time_since_last = "-"
        workload = next((w for w in workloads if w["name"] == server_id), None)
        if workload:
            workload_exists = "True"
            wdata = trilio.get_workload(token, token_data, workload["id"])
            if wdata["storage_usage"]["full"]["snap_count"] > 0:
                last_backup = wdata["updated_at"]
                lb_dt = get_datetime(last_backup)
                now = datetime.datetime.now()
                time_since_last = str(now - lb_dt)
                usage = wdata["storage_usage"]["full"]["usage"]
                last_backup_size = round(usage / 1024 / 1024 / 1024, 2)
        data[server_id] = {
            "id": server_id,
            "name": server["name"],
            "host": server['OS-EXT-SRV-ATTR:hypervisor_hostname'],
            "status": server["status"],
            "created": server["created"],
            "backups_enabled": str(is_backup_enabled(server)),
            "workload_exists": workload_exists,
            "last_backup": last_backup,
            "time_since_last_backup": time_since_last,
            "last_backup_duration": last_backup_duration,
            "last_backup_size": last_backup_size,
            "last_backup_error": last_backup_error,
        }
    return data


def datetime_today_at(now, time):
    """Return a datetime of today at the given time"""
    return datetime.datetime.combine(
        now, datetime.datetime.strptime(time, "%H:%M").time()
    )


def workload_fits(token, token_data, workload_id):
    """return bool, is this workload likely to fit into the backup window?"""
    now = datetime.datetime.now()
    # check if any workload could run right now
    is_weekday = now.weekday() < 5
    is_weekend = not is_weekday
    config = conf()
    # can it run today? (weekday/weekend check)
    if is_weekday and not config["allow_weekdays"]:
        return False
    if is_weekend and not config["allow_weekends"]:
        return False
    # can it run at this time?
    day_conf_str = "weekday" if is_weekday else "weekend"
    allow_all_day = config[f"allow_all_day_{day_conf_str}s"]
    blacklist_start = config[f"{day_conf_str}_blacklist_start_time"]
    blacklist_end = config[f"{day_conf_str}_blacklist_end_time"]
    blacklist_start_dt = datetime_today_at(now, blacklist_start)
    blacklist_end_dt = datetime_today_at(now, blacklist_end)
    if not allow_all_day and now > blacklist_start_dt and now < blacklist_end_dt:
        return False
    # Now that we know the workload can start now, will it likely also finish soon?
    # I'd originally intended to do a bunch of fun math and analysis for this...
    # Instead since I'm out of time:
    #   If the workload has never ran before, yeah sure go for it.
    #   If the workload has ran before, check its last snap to see how long that took.
    snaps = get_snapshots(token, token_data, workload_id=workload_id)
    workload = get_workload(token, token_data, workload_id)
    if workload["storage_usage"]["full"]["snap_count"] == 0:
        return True
    # TODO: Check the size of the last snap and estimate if it'll finish in time
    return True


def get_qty_snaps_running_per_host(token, token_data, workloads):
    """ return a dict by hostname listing the qty of snaps now running on it """
    running = {}
    server_ids = [ w["name"] for w in workloads if w["status"] != "available" ]
    for server_id in server_ids:
        server = os.get_server(token, token_data, server_id)
        host = server["OS-EXT-SRV-ATTR:hypervisor_hostname"]
        if host in running:
            running[host] += 1
        else:
            running[host] = 1
    return running


def is_max_running_on_host(token, token_data, server_id, running_per_host):
    """ return bool - does this host have too many running? """
    host_max = int(env("concurrent_fulls_host"))
    server = os.get_server(token, token_data, server_id)
    host = server["OS-EXT-SRV-ATTR:hypervisor_hostname"]
    if host not in running_per_host:
        return False
    return host_max >= running_per_host[host]


def get_next_workload_to_run(token, token_data):
    """Find the next workload to run"""
    workloads = get_workloads(token, token_data)
    running_per_host = get_qty_snaps_running_per_host(token, token_data, workloads)
    # Have any workloads not had any snapshots yet? If so, choose it.
    # First, find the snapshots associated with each workload
    for workload in workloads:
        workload_id = workload["id"]
        snaps = trilio.get_snapshots(token, token_data, workload_id=workload_id)
        workload["snaps"] = snaps
    # Check if any of the workloads have no snaps, and if they fit
    for workload in [w for w in workloads if not w["snaps"]]:
        if is_max_running_on_host(token, token_data, workload["name"], running_per_host):
            continue
        if trilio.workload_fits(token, token_data, workload["id"]):
            return workload
    # If not, get a list of workloads sorted least recently ran
    workloads.sort(key=lambda w: get_datetime(w["updated_at"]), reverse=False)
    now = datetime.datetime.now()
    for workload in workloads:
        # Check if the host this VM is on already has too many workloads running
        if is_max_running_on_host(token, token_data, workload["name"], running_per_host):
            continue
        # Check if the snapshots are old enough to re-do
        snaps = get_snapshots(token, token_data, workload["id"])
        if not snaps:
            return workload
        # Check if the last snapshot over a week old
        snap_date = get_datetime(snaps[-1]["created_at"])
        last_week = now - datetime.timedelta(days=7)
        if snap_date < last_week:
            return workload
    return  # handle receiving None gracefully


def exec_full_snapshot(token, token_data, workload_id):
    """Run a full snapshot"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    workload_url = f"{wlm_url}/workloads/{workload_id}?full=1"
    headers = os.os_headers(token)
    data = {"snapshot": {"name": None, "description": None, "is_scheduled": False}}
    data_json = json.dumps(data)
    resp = requests.post(workload_url, headers=headers, verify=False, data=data_json)
    if resp.status_code != 200 and resp.status_code != 201:
        # it should return 201 created but returns 200 ok for some reason
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["snapshot"]


def is_max_workloads_running(token, token_data):
    """Return bool, are the max number of workloads already running?"""
    max_cloud_workloads = int(conf()["concurrent_total_cloud"])
    workloads = get_workloads(token, token_data)
    unavail_workloads = [w for w in workloads if w["status"] != "available"]
    return len(unavail_workloads) >= max_cloud_workloads


def delete_snapshot(token, token_data, snapshot_id):
    """delete a given snapshot"""
    wlm_url = os.os_endpoint(ENDPOINT, token_data)
    snapshots_url = f"{wlm_url}/snapshots/{snapshot_id}"
    headers = os.os_headers(token)
    resp = requests.delete(snapshots_url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise os.OpenstackException(f"{resp.status_code}: {resp.reason}")
