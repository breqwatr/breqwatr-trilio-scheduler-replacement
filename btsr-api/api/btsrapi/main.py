""" btsr api entrypoint """
import datetime
from flask import Flask, render_template
import btsrlib.config as config
import btsrlib.redis as redis
import btsrlib.openstack as os
import btsrlib.trilio as trilio
import btsrlib.config as config

# probably dont need these...
import btsrapi.servers as servers
import btsrapi.running as running
import btsrapi.orphans as orphans


app = Flask(__name__)


def index():
    """ index page """
    return (
        "<a href='/report/servers'>server report</a><br />\n"
        "<a href='/report/running'>running backups report</a><br />\n"
        "<a href='/report/orphans'>orphaned workloads report</a><br />\n"
    )

def test_api():
    """everything ok?"""
    return "OK 1\n"

def servers():
    """ Servers page """
    client = redis.get_client()
    summary = redis.get_dict(redis.get_client(), "servers_summary")
    return render_template("servers.html", servers=summary)

def running():
    """ Running page """
    client = redis.get_client()
    # summary = redis.get_dict(redis.get_client(), "servers_summary")
    return render_template("running.html")

def orphans():
    """ Orphans page """
    logging.debug("Creting orphans report")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    workloads = trilio.get_workloads(token, token_data)
    parsed_workloads = []
    for workload in workloads:
        wsnaps = trilio.get_snapshots(token, token_data, workload_id=workload["id"])
        wdata = trilio.get_workload(token, token_data, workload["id"])
        total_size = round(wdata["storage_usage"]["usage"] / 1024 / 1024 / 1024)
        wdata = {
            "id": workload["id"],
            "name": workload["name"]
            "num_snaps": len(wsnaps)
            "last_snap": wsnaps[-1]["created_at"]
            "server_names": ", ".join([ i["name"] for i in wdata["instances"] ])
            "total_snap_size": total_size
        }
        parsed_workloads.append(wdata)

    return render_template("orphans.html", workloads=parsed_workloads)


app.add_url_rule("/", "index", index, methods=["GET"])
app.add_url_rule("/test", "test_api", test_api, methods=["GET"])
app.add_url_rule("/servers", "report", servers, methods=["GET"])
app.add_url_rule("/running", "running", running, methods=["GET"])
app.add_url_rule("/orphans", "orphans", orphans, methods=["GET"])


