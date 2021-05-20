""" Entrypoint for btsr-worker """
import btsrworker.lib.openstack as os

def main():
    env = os.get_os_env()
    print("BTSR WORKER")
    token, token_data = os.get_token(env)
    servers = os.get_servers(token, token_data)
    from pprint import pprint
    pprint(servers)
