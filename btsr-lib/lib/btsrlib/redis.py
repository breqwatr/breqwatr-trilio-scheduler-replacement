""" Lib to interact with redis """
import redis
import json


def get_client():
    """Return a connected redis client"""
    return redis.Redis(host="10.106.4.0", port=6379)


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
