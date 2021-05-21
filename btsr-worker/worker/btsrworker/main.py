""" Entrypoint for btsr-worker """
import click
from pprint import pprint

import btsrlib.openstack as os
import btsrlib.trilio as trilio
import btsrlib.config as config
import btsrlib.redis as redis


@click.command(name="save-summary")
def save_summary():
    openrc_files = config.get_openrc_files()
    for project in openrc_files:
        config.source_openrc_file(openrc_files[project])
        env = os.get_os_env()
        token, token_data = os.get_token(env)
        servers = os.get_servers(token, token_data)
        server_details = os.get_servers_details(token, token_data, servers)
        summary = trilio.get_trilio_summary(server_details)
        client = redis.get_client()
        redis.set_dict(client, project, summary)


@click.command(name="print-summary")
def print_summary():
    openrc_files = config.get_openrc_files()
    for project in openrc_files:
        client = redis.get_client()
        data = redis.get_dict(client, project)
        pprint(data)


def get_entrypoint():
    """ Return the entrypoint click group """

    @click.group()
    def entrypoint():
        """ Entrypoint for Click """

    entrypoint.add_command(save_summary)
    entrypoint.add_command(print_summary)
    return entrypoint


def main():
    """ Entrypoint defined in setup.py """
    entrypoint = get_entrypoint()
    entrypoint()
