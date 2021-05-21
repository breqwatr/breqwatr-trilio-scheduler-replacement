""" Entrypoint for btsr-worker """
import btsrlib.openstack as os
import btsrlib.trilio as trilio
import btsrlib.config as config
import btsrlib.redis as redis


def main():
    print("BTSR WORKER")
    openrc_files = config.get_openrc_files()
    for project in openrc_files:
        print(f"project: {project}")
        config.source_openrc_file(openrc_files[project])
        env = os.get_os_env()
        token, token_data = os.get_token(env)
        print("getting server details...")
        servers = os.get_servers(token, token_data)
        server_details = os.get_servers_details(token, token_data, servers)
        print("writing to redis...")
        client = redis.get_client()
        redis.set_dict(client, project, server_details)
        print("done")
        data = redis.get_dict(client, project)
        from pprint import pprint

        pprint(data)
    # workloads = trilio.get_workloads(token, token_data)
    # workload = trilio.get_workload(token, token_data, workloads[0]['id'])
    # from pprint import pprint
    # pprint(workload)
