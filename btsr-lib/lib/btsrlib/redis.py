""" Lib to interact with redis """
import redis

def get_client():
    """ Return a connected redis client """
    return redis.Redis(host='10.106.4.0', port=6379)
    # ,password='password')
