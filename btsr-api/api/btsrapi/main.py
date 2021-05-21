""" btsr api entrypoint """
from flask import Flask

app = Flask(__name__)

def test_api():
    """ everything ok? """
    return "OK 1\n"

def render_report():
    """ Render the backup report """
    return "report"

app.add_url_rule('/test', 'test_api', test_api, methods=['GET'])
app.add_url_rule('/report', 'report', render_report, methods=['GET'])


# intentionally left to 404 - security through obscurity!
# app.add_url_rule('/', 'test_api', test_api, methods=['GET'])

