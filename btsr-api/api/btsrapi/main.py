""" btsr api entrypoint """
import logging
import datetime
from flask import Flask, render_template

import btsrlib.redis as redis

import btsrlib.openstack as os
import btsrlib.trilio as trilio
import btsrlib.config as config


app = Flask(__name__)


def index():
    """index page"""
    return (
        "<a href='/report/servers'>server report</a><br />\n"
        "<a href='/report/running'>running backups report</a><br />\n"
        "<a href='/report/orphans'>orphaned workloads report</a><br />\n"
    )


def test_api():
    """everything ok?"""
    return "OK 1\n"


def server_dt(server):
    """Get the dt of the server's created"""
    # ...apparently the timestamp is in Zulu time, because reasons
    return datetime.datetime.strptime(server["created"], "%Y-%m-%dT%H:%M:%SZ")


def servers():
    """Servers page"""
    client = redis.get_client()
    servers_summary = redis.get_dict(redis.get_client(), "servers_summary")
    servers = [servers_summary[server_id] for server_id in servers_summary]
    servers.sort(key=lambda s: server_dt(s), reverse=False)
    return render_template("servers.html", servers=servers)


def running():
    """Running page"""
    logging.debug("Updating servers_summary report")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    workloads = trilio.get_workloads(token, token_data)
    running_summary = []
    locked = [w for w in workloads if w["status"] != "available"]
    summary = redis.get_dict(redis.get_client(), "servers_summary")
    for workload in locked:
        sdata = trilio.get_snapshots(token, token_data, workload_id=workload["id"])
        if not sdata:
            continue
        server_name = "-"
        if summary and workload["name"] in summary:
            server_name = summary[workload["name"]]["name"]
        snap_start = sdata[-1]["created_at"]
        start_dt = datetime.datetime.strptime(snap_start, "%Y-%m-%dT%H:%M:%S.%f")
        now_dt = now = datetime.datetime.now()
        snap_duration = str(now_dt - start_dt)
        data = {
            "id": workload["id"],
            "name": workload["name"],
            "server_name": server_name,
            "snap_duration": snap_duration,
        }
        running_summary.append(data)
    return render_template("running.html", workloads=running_summary)


def orphans():
    """Orphans page"""
    client = redis.get_client()
    orphans_summary = redis.get_dict(redis.get_client(), "orphans_summary")
    return render_template("orphans.html", workloads=orphans_summary)


app.add_url_rule("/", "index", index, methods=["GET"])
app.add_url_rule("/test", "test_api", test_api, methods=["GET"])
app.add_url_rule("/servers", "report", servers, methods=["GET"])
app.add_url_rule("/running", "running", running, methods=["GET"])
app.add_url_rule("/orphans", "orphans", orphans, methods=["GET"])
