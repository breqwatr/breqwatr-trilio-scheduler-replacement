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
    """ Save to redis a list of all the servers and their backup-related details """
    logging.debug("Updating reports")
    config.source_openrc_file()
    env = os.get_os_env()
    token, token_data = os.get_token(env)
    servers = os.get_servers(token, token_data)
    server_details = os.get_servers_details(token, token_data, servers)
    summary = trilio.get_trilio_summary(server_details)
    client = redis.get_client()
    redis.set_dict(client, "servers_summary", summary)
    redis.set_last_updated(client)


@click.command(name="print-reports-data")
def print_reports_data():
    """ Troubleshooting command to show the data about servers from redis """
    logging.debug("printing reports data")
    client = redis.get_client()
    data = redis.get_dict(client, "servers_summary")
    pprint(data)


@click.command(name="create-missing-workloads")
def create_missing_workloads():
    """ Find any servers with enable-backups=true and create workloads for them. """
    logging.info("creating missing workloads")
    client = redis.get_client()
    redis.set_last_updated(client)


@click.command(name="delete-old-snapshots")
def delete_old_snapshots():
    """ Find any workloads with 2 'available' snapshots and delete the older one """
    logging.info("deleting old snapshots")
    client = redis.get_client()
    redis.set_last_updated(client)


@click.command(name="start-snapshots")
def start_snapshots():
    """ start snapshots if any are due to start """
    logging.info("starting snapshots")
    client = redis.get_client()
    redis.set_last_updated(client)


def get_entrypoint():
    """ Return the entrypoint click group """

    @click.group()
    def entrypoint():
        """ Entrypoint for Click """

    entrypoint.add_command(update_reports)
    entrypoint.add_command(print_reports_data)
    entrypoint.add_command(create_missing_workloads)
    entrypoint.add_command(delete_old_snapshots)
    entrypoint.add_command(start_snapshots)
    return entrypoint


def main():
    """ Entrypoint defined in setup.py """
    entrypoint = get_entrypoint()
    entrypoint()
