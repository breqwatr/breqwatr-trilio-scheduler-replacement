""" Lib to interact with redis """
from datetime import datetime
import logging
import redis
import json


def get_client():
    """Return a connected redis client"""
    # k8s DNS will resolve the service to an IP
    return redis.Redis(host="btsr-redis", port=6379)


def set_dict(client, key, data):
    """Write a dict to redis - redis handles nested dicts very poorly"""
    client.set(key, json.dumps(data))


def get_dict(client, key):
    """Read a dict from redis"""
    return json.loads(client.get(key))


def set_str(client, key, data):
    """Read a str from redis"""
    client.set(key, data)


def get_str(client, key):
    """Read a str from redis"""
    return client.get(key)


def set_last_updated(client):
    """ Update the 'last_updated' key with a datestamp """
    now = str(datetime.now())
    logging.debug(f"setting last_updated in redis to {now}")
    client.set("last_updated", now)
