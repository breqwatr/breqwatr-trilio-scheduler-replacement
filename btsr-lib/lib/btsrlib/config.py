""" configuration functions """
import configparser
import os
import shlex
import subprocess

def get_openrc_files():
    """ Return the project names and paths of the openrc files """
    config = configparser.ConfigParser()
    config.read("/config/openrcPaths.conf")
    files = {}
    for (project_name, path) in config.items("DEFAULT"):
        files[project_name] = path
    return files

def source_openrc_file(path):
    """ source an openrc file """
    full_path = f"/btsr/openrc/{path}"
    command = shlex.split(f"env -i bash -c 'source {full_path} && env'")
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.decode().partition("=")
        os.environ[key] = value.replace("\n","")
    proc.communicate()
