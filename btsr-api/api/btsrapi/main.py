""" btsr api entrypoint """
from flask import Flask, render_template
import btsrlib.config as config
import btsrlib.redis as redis
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
    client = redis.get_client()
    # summary = redis.get_dict(redis.get_client(), "servers_summary")
    return render_template("orphans.html")


app.add_url_rule("/", "index", index, methods=["GET"])
app.add_url_rule("/test", "test_api", test_api, methods=["GET"])
app.add_url_rule("/servers", "report", servers, methods=["GET"])
app.add_url_rule("/running", "running", running, methods=["GET"])
app.add_url_rule("/orphans", "orphans", orphans, methods=["GET"])


