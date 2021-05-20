""" Entrypoint for btsr-worker """
import btsrworker.lib.openstack as os
import btsrworker.lib.trilio as trilio

def main():
    env = os.get_os_env()
    print("BTSR WORKER")
    token, token_data = os.get_token(env)
    # servers = os.get_servers(token, token_data)
    workloads = trilio.get_workloads(token, token_data)
    workload = trilio.get_workload(token, token_data, workloads[0]['id'])
    from pprint import pprint
    pprint(workload)
