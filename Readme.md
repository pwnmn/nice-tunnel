# Purpose

Often it is hard to expose a web service that is running on a local computer to the outside world to quickly show it to others. This is a solution to easily expose a web service using your own domain and a server.

# How-To

Requirements:

* A nice tunnel traefik server listening on port 443 of `your-own-domain.com`
* The nice_tunnel.py scfript available on the PATH of the server
* An SSH server running on port 22 of `your-own-domain.com`.
* A web server running on port 8080 of your laptop.

Run the following command on your local computer that is running a web server that you like to expose.

```bash
ssh -tR :9001:localhost:8080 user@your-own-domain.com nice_tunnel.py -t http -d sub1.your-own-domain.com -p 9001
```

Now any requests to `https://sub1.your-own-domain.com` will be proxied to your local webserver.


# How it works

The command does the following things.

1. It starts a remote SSH tunnel from the server port 9001 to local port 8080
2. It runs the command `nice_tunnel.py --type http --domain sub.your-own-domain.com --port 9001`
   on the server.
   The python script parses the domain and port and uses the traefik reverse proxy's file provider to
   configure and reverse proxy `sub1.your-own-domain.com` to port 9001 on the server. Traefik
   automatically retrieves an HTTPS cert using letsencrypt for `sub1.your-own-domain.com`.

**Note:** The `-t` is necessary so that doing CTRL-C on your laptop stops the
`nice_tunnel.py` command on the server, which allows it to clean up the tunnel
on Traefik. Otherwise it would leave `nice_tunnel.py` running and just kill your
SSH tunnel locally.


# Running the server

Assuming you already have an ssh server listening on the server, getting the nice-tunnel server
running consists of the following steps, depending whether you'd like to use it as a standalone binary or use docker with docker-compose.

## Standalone

Navigate to the `standalone` folder in and execute the `install.sh` script. It wil download the traefik
reverse proxy, set up a configuration folder in `/usr/local/etc/traefik` and set the correct rights to write to it.
Afterwards, it copies the `nice_tunnel.py` script to `/usr/local/bin` which should be on the PATH.

**Note:** Traefik needs to bind to port 443. To enable this without running as root, the `CAP_NET_BIND_SERVICE` capability has to be set with the binary. This is also done with the installation script above.

The server can then be started by simply executing `./traefik`.

## Docker Compose

Navigate to the docker folder and execut ethe `./install.sh` script. This will copy the `nice_tunnel.py` script to 
`/usr/local/bin` which should be on the PATH as with the standalone installation. With docker compose, the file configurations are stored in `~/.traefik/`.

Adjust the `BASE_DOMAIN` and `EMAIL` in the .env file and start the traefik server up with `docker-compose up -d`.

**Note:** Using docker, traefik is running inside a container. It will not be able to reach the ssh tunnel on port 9001 as it is running on localhost by default. The following configuration has to be enabled with sshd in the `sshd_config`.

```bash
GatewayPorts clientspecified
```

Add it to the configuration, restart sshd and double-check that it is enabled by using `sudo sshd -T | grep gateway`.
The option should appear in the output as `gatewayports clientspecified`.


# Thanks

Nice tunnel is heavily inspired by [SirTunnel](https://github.com/matiboy/SirTunnel). SirTunnel is using caddy as the reverse proxy which only works
with http traffic. Traefik can also expose TCP traffic such as databases. The goal is to enable forwarding for both
types of traffic.
