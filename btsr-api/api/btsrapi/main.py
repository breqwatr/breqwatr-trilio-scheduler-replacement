""" btsr api entrypoint """
from flask import Flask, render_template
import btsrlib.config as config
import btsrlib.redis as redis


app = Flask(__name__)


def test_api():
    """everything ok?"""
    return "OK 1\n"


def render_report():
    """Render the backup report"""
    openrc_files = config.get_openrc_files()
    assert(openrc_files, "openrc files need to be populated")
    for project in openrc_files:
        client = redis.get_client()
        summary = redis.get_dict(client, project)
		# TODO: multi-project support
        return render_template("report.html", servers=summary)


app.add_url_rule("/test", "test_api", test_api, methods=["GET"])
app.add_url_rule("/report", "report", render_report, methods=["GET"])


