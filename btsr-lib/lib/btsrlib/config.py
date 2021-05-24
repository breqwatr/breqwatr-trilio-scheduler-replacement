""" configuration functions """
import configparser
import os
import shlex
import subprocess


def source_openrc_file():
    """source an openrc file"""
    full_path = f"/btsr/openrc.sh"  # hardcoded to the manifests
    command = shlex.split(f"env -i bash -c 'source {full_path} && env'")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.decode().partition("=")
        os.environ[key] = value.replace("\n", "")
    proc.communicate()
