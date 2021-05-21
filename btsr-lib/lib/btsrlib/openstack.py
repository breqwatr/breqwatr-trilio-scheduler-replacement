""" OpenStack functions """
import requests
from btsrlib.common import env


class OpenstackException(Exception):
    """ Something has gone wrong with a call to OpenStack """

def get_os_env():
    """ Return the OpenStack environment values in a dictionary """
    keys = ["OS_PROJECT_DOMAIN_NAME", "OS_USER_DOMAIN_NAME", "OS_PROJECT_NAME", "OS_TENANT_NAME", "OS_USERNAME", "OS_PASSWORD", "OS_AUTH_URL", "OS_INTERFACE", "OS_ENDPOINT_TYPE", "OS_IDENTITY_API_VERSION", "OS_REGION_NAME", "OS_AUTH_PLUGIN"]
    os_env = {}
    for key in keys:
      os_env[key] = env(key)
    return os_env


def get_token(os_env):
    """ Get an OpenStack token and API catalog using global vars """
    # Build json data to send to openstack api
    os_username = os_env["OS_USERNAME"]
    os_password = os_env["OS_PASSWORD"]
    os_auth_url = os_env["OS_AUTH_URL"]
    os_user_domain_name = os_env["OS_USER_DOMAIN_NAME"]
    os_project_name = os_env["OS_PROJECT_NAME"]
    os_project_domain_name = os_env["OS_PROJECT_DOMAIN_NAME"]
    login_data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": os_username,
                        "password": os_password,
                        "domain": {"name": os_user_domain_name},
                    }
                },
            },
            "scope": {
                "project": {
                    "name": os_project_name,
                    "domain": {"name": os_project_domain_name},
                }
            },
        }
    }
    token_url = f"{os_auth_url}/auth/tokens"
    resp = requests.post(token_url, json=login_data, verify=False)
    if resp.status_code != 201:
        raise OpenstackException(f"{resp.status_code}: {resp.reason}")
    token = resp.headers["X-Subject-Token"]
    return token, resp.json()


def os_headers(token):
    """ Return the format expected by openstack/trilio for HTPP headers """
    return {"Content-Type": "application/json", "X-Auth-Token": token}


def os_endpoint(name, token_data):
    """ Return the OpenStack endpoint from the token's JSON data """
    os_interface = get_os_env()["OS_INTERFACE"]
    catalog = next(c for c in token_data["token"]["catalog"] if c["name"] == name)
    return next(e["url"] for e in catalog["endpoints"] if e["interface"] == os_interface)


def get_servers(token, token_data):
    """ Return a list of servers in the scoped project """
    nova_url = os_endpoint("nova", token_data)
    servers_url = f"{nova_url}/servers"
    headers = os_headers(token)
    resp = requests.get(servers_url, headers=headers, verify=False)
    if resp.status_code != 200:
        raise OpenstackException(f"{resp.status_code}: {resp.reason}")
    return resp.json()["servers"]

