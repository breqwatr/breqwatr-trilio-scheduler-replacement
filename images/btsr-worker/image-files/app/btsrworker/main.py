""" Entrypoint for btsr-worker """
import btsrworker.lib.openstack as os

def main():
    env = os.get_os_env()
    print("BTSR WORKER")
