import requests # type: ignore


def brp_request(rpc_endpoint, host, port, params={}):
    print("brp_simple_request")

    """Fetch the registry schema from a running Bevy application"""

    # 0.16+ payload
    data = {"jsonrpc": "2.0", "method": rpc_endpoint, "params": params}
    r = requests.post(host + ":" + str(port), json=data)
    brp_response = r.json()
    return brp_response

def brp_simple_request(rpc_endpoint, host, port):
    print("brp_simple_request")

    """Fetch the registry schema from a running Bevy application"""

    # 0.16+ payload
    data = {"jsonrpc": "2.0", "method": rpc_endpoint, "params": {}}
    r = requests.post(host + ":" + str(port), json=data)
    brp_response = r.json()
    return brp_response

def brp_fetch_skein_presets(host, port):
    """Fetch the presets (and Default values) from a running Bevy application"""
    
    data = {"jsonrpc": "2.0", "method": "skein/presets", "params": {}}
    r = requests.post(host + ":" + str(port), json=data)
    brp_response = r.json()
    return brp_response