""" Common library functions """
import os

def env(var, default=None):
    """ load the config from env vars """
    if var not in os.environ:
        if default is None:
            raise Exception(f"{var} is required")
        else:
            return default
    return os.environ[var]
