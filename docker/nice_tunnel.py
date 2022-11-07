#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import yaml
import time
from os.path import expanduser

traefik_config_dir = expanduser("~") + '/.traefik/config'

def read_args():
    parser = argparse.ArgumentParser(description="Adds a forwarding rule to traefik")
    parser.add_argument('-t','--type', help='Type can be either tcp or http', required=True)
    parser.add_argument('-d','--domain', help='Domain should be a valid domain name, i.e. sub.example.com', required=True)
    parser.add_argument('-p','--port', help='Port to which traefik will forward on the server', required=True)

    # Read arguments from command line
    return parser.parse_args()

def create_traefik_config(protocol, host, port, tunnel_id):
    print("Executed with protocol {}, host {}, port {}".format(protocol, host, port))
    host_key = "Host"
    service_key = "url"
    service_scheme = "http://"
    if protocol == "tcp":
        host_key = "HostSNI"
        service_key = "address"
        service_scheme = ""

    return {
        protocol: {
            'routers': {
                tunnel_id + '_router': {
                    'rule': host_key + '(`' + host + '`)',
                    'tls': {
                        'certResolver': 'letsencrypt'
                    },
                    'service': tunnel_id + '_service',
                    'entryPoints': ['websecure']
                }
            },
            'services': {
                tunnel_id + '_service': {
                    'loadBalancer': {
                        'servers': [
                            {
                                service_key: service_scheme + 'host.docker.internal' + ':' + port
                            }
                        ]
                    }
                }
            }
        }
    }

def get_tunnel_id(host, port):
    tunnel_id_host_key = host
    if host == "*":
        tunnel_id_host_key = "asterisk"

    return tunnel_id_host_key + '.' + port

if __name__ == '__main__':

    args = read_args()
    protocol = args.type
    host = args.domain
    port = args.port

    tunnel_id = get_tunnel_id(host, port)
    traefik_config = create_traefik_config(args.type, args.domain, args.port, tunnel_id)

    config_path = traefik_config_dir + '/' + tunnel_id + '.yml'

    with open(config_path, 'w') as file:
        documents = yaml.dump(traefik_config, file)

    print("Tunnel created successfully")

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Cleaning up tunnel...")
            if os.path.exists(config_path):
                os.remove(config_path)
            break
