""" Entrypoint for btsr-worker """
import click
import logging
from pprint import pprint

import btsrlib  # sets up log file
import btsrlib.openstack as os
import btsrlib.trilio as trilio
import btsrlib.config as config
import btsrlib.redis as redis


@click.command(name="update-reports")
def update_reports():
    """Save to redis a list of all the servers and their backup-related details"""
    # get the list of servers for its report
    logging.info("Updating servers_summary report")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    servers = os.get_servers(token, token_data)
    server_details = os.get_servers_details(token, token_data, servers)
    summary = trilio.get_trilio_summary(token, token_data, server_details)
    client = redis.get_client()
    redis.set_dict(client, "servers_summary", summary)
    # find all the workloads that aren't being tracked by this
    logging.debug("Updating orphans report")
    workloads = trilio.get_workloads(token, token_data)
    parsed_workloads = []
    for workload in workloads:
        # logging.debug(f"  update-reports: parsing workload: {workload['id']}")
        if workload["name"] in summary:
            if summary[workload["name"]]["backups_enabled"].lower() == "true":
                continue
        wsnaps = trilio.get_snapshots(token, token_data, workload_id=workload["id"])
        last_snap = wsnaps[-1]["created_at"] if wsnaps else "never"
        wdata = trilio.get_workload(token, token_data, workload["id"])
        total_size = round(wdata["storage_usage"]["usage"] / 1024 / 1024 / 1024)
        wdata = {
            "id": workload["id"],
            "name": workload["name"],
            "num_snaps": len(wsnaps),
            "last_snap": last_snap,
            "server_names": ", ".join([i["name"] for i in wdata["instances"]]),
            "total_snap_size": total_size,
        }
        parsed_workloads.append(wdata)
    redis.set_dict(client, "orphans_summary", parsed_workloads)
    redis.set_last_updated(client)


@click.command(name="print-reports-data")
def print_reports_data():
    """Troubleshooting command to show the data about servers from redis"""
    logging.debug("printing reports data")
    client = redis.get_client()
    data = redis.get_dict(client, "servers_summary")
    pprint(data)


@click.command(name="create-missing-workloads")
def create_missing_workloads():
    """Find any servers with enable-backups=true and create workloads for them."""
    logging.info("creating missing workloads")
    client = redis.get_client()
    server_summary = redis.get_dict(client, "servers_summary")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    workloads = trilio.get_workloads(token, token_data)
    for server_id, server in server_summary.items():
        if server["workload_exists"].lower() != "false":
            continue
        if server["backups_enabled"].lower() == "false":
            continue
        this_workload = next((w for w in workloads if w["name"] == server_id), False)
        if this_workload:
            # This workload already exists
            continue
        logging.info(f"creating workload for server id: {server_id}")
        trilio.create_workload(token, token_data, server_id)
    redis.set_last_updated(client)


@click.command(name="start-snapshots")
def start_snapshots():
    """start snapshots if any are due to start"""
    logging.info("starting snapshots")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    # check if max workloads are running, exit if they are
    if trilio.is_max_workloads_running(token, token_data):
        logging.debug("not running any snaps, is_max_workloads_running == True")
        return
    # queue up the next workload
    next_workload = trilio.get_next_workload_to_run(token, token_data)
    if next_workload:
        workload_id = next_workload["id"]
        logging.debug(f"Running snapshot on workload id: {workload_id}")
        trilio.exec_full_snapshot(token, token_data, workload_id)


@click.command(name="delete-old-snapshots")
def delete_old_snapshots():
    """Delete any old snapshots if a newer full exists"""
    logging.info("creating missing workloads")
    client = redis.get_client()
    server_summary = redis.get_dict(client, "servers_summary")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    snaps = trilio.get_snapshots(token, token_data)
    workload_ids = {snap["workload_id"] for snap in snaps}
    for workload_id in workload_ids:
        workload_snaps = [s for s in snaps if s["workload_id"] == workload_id]
        workload_snaps.sort(key=lambda s: trilio.get_datetime(s["created_at"]), reverse=False)
        if len(workload_snaps) < 2:
            # no old snaps to delete from this workload
            continue
        if workload_snaps[-1]["status"] != "available":
            # Something is wrong here, don't delete things
            continue
        del workload_snaps[-1]
        for workload_snap in workload_snaps:
            snapshot_id = workload_snap["id"]
            logging.info(f"deleting snapshot id: {snapshot_id}")
            trilio.delete_snapshot(token, token_data, snapshot_id)


def get_entrypoint():
    """Return the entrypoint click group"""

    @click.group()
    def entrypoint():
        """Entrypoint for Click"""

    entrypoint.add_command(update_reports)
    entrypoint.add_command(print_reports_data)
    entrypoint.add_command(create_missing_workloads)
    entrypoint.add_command(delete_old_snapshots)
    entrypoint.add_command(start_snapshots)
    return entrypoint


def main():
    """Entrypoint defined in setup.py"""
    entrypoint = get_entrypoint()
    entrypoint()
