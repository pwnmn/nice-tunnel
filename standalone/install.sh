#/bin/bash

# Traefik version used. Can be increased with time
traefik_version=2.10.5
# Contains script that will add dynamic forwarding rule using protocol, domain and port as parameters
forwarding_script=nice_tunnel.py
# Contains dynamic config to expose the traefik dashboard
traefik_dynamic_config=dashboard_router.yml

printf "Downloading traefik v${traefik_version}...\n\n"
traefik_gz=traefik_v${traefik_version}_linux_386.tar.gz
curl -s -O -L https://github.com/traefik/traefik/releases/download/v${traefik_version}/${traefik_gz}
printf "Download finished. Unpacking...\n\n"
tar xf ${traefik_gz}

rm ${traefik_gz}
rm LICENSE.md
rm CHANGELOG.md

read -p "Please input the email you would like to use with the lestencrypt certificate: " email
read -p "Please input the base domain you would like to use, i.e. example.com: " base_domain

# Create configuration folders if they don't exist
user_home=$HOME
mkdir -p $user_home/.config
mkdir -p $user_home/.traefik/standalone/config
mkdir -p $user_home/.traefik/standalone/acme
USER_HOME=$user_home EMAIL=$email envsubst < traefik_template.yml | tee $user_home/.config/traefik.yml > /dev/null
BASE_DOMAIN=$base_domain envsubst < dashboard_router.yml | tee $user_home/.traefik/standalone/config/dashboard_router.yml > /dev/null

printf "Enabling traefik to bind to low ports. Please input your sudo password if prompted.\n"
sudo setcap 'cap_net_bind_service=+ep' traefik
printf "Copying tunneling script to /usr/local/bin which should be on the PATH\n"
sudo cp ${forwarding_script} /usr/local/bin
sudo chmod +x /usr/local/bin/${forwarding_script}
