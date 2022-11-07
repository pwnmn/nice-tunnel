#/bin/bash

# Contains script that will add dynamic forwarding rule using protocol, domain and port as parameters
forwarding_script=nice_tunnel.py

echo "Creating config folder in /user/local/etc/traefik for dynamic traefik config and adjusting rights."
mkdir -p ~/.traefik/config
echo "Copying tunneling script to /usr/local/bin which should be on the PATH. Please input your sudo password if prompted."
sudo cp ${forwarding_script} /usr/local/bin
sudo chmod +x /usr/local/bin/${forwarding_script}
